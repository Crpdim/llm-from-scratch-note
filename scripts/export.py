import base64
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

import requests
import websocket


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = PROJECT_ROOT / "notebooks" / "ch02_text_data_processing.ipynb"
EXPORTS = PROJECT_ROOT / "exports"
HTML = EXPORTS / "ch02_text_data_processing.html"
PDF = EXPORTS / "ch02_text_data_processing.pdf"


def browser_path() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "msedge",
        "google-chrome",
        "chromium",
    ]
    for candidate in candidates:
        if candidate.endswith(".exe") and Path(candidate).exists():
            return candidate
        if shutil.which(candidate):
            return candidate
    raise RuntimeError("Could not find Microsoft Edge, Chrome, or Chromium for PDF export.")


def run_nbconvert() -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "python",
            "-m",
            "nbconvert",
            "--to",
            "html",
            str(NOTEBOOK),
            "--output",
            HTML.name,
            "--output-dir",
            str(EXPORTS),
        ],
        check=True,
    )


def print_pdf_without_headers() -> None:
    user_data = Path(tempfile.mkdtemp(prefix="llm-basics-print-"))
    port = 9232
    proc = subprocess.Popen(
        [
            browser_path(),
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--remote-allow-origins=*",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            try:
                urlopen(f"http://127.0.0.1:{port}/json/version", timeout=0.25).read()
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("Browser DevTools endpoint did not start.")

        tabs = requests.get(f"http://127.0.0.1:{port}/json", timeout=10).json()
        page = next(t for t in tabs if t.get("type") == "page")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=10)
        msg_id = 0

        def call(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == msg_id:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        call("Page.enable")
        file_url = "file:///" + str(HTML.resolve()).replace("\\", "/")
        call("Page.navigate", {"url": file_url})
        time.sleep(2)

        result = call(
            "Page.printToPDF",
            {
                "landscape": False,
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": False,
                "paperWidth": 8.27,
                "paperHeight": 11.69,
                "marginTop": 0.35,
                "marginBottom": 0.35,
                "marginLeft": 0.35,
                "marginRight": 0.35,
            },
        )
        PDF.write_bytes(base64.b64decode(result["data"]))
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(user_data, ignore_errors=True)


if __name__ == "__main__":
    run_nbconvert()
    print_pdf_without_headers()
    print(f"Wrote {HTML}")
    print(f"Wrote {PDF}")
