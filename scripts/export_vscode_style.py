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


VSCODE_STYLE = r"""
<style>
  :root {
    --page-bg: #ffffff;
    --page-fg: #202124;
    --muted: #6a737d;
    --border: #d8dee4;
    --code-bg: #f6f8fa;
    --code-border: #d0d7de;
    --output-bg: #fbfbfb;
  }

  @page {
    size: A4;
    margin: 12mm 13mm;
  }

  html,
  body {
    background: var(--page-bg) !important;
    color: var(--page-fg) !important;
    font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif !important;
    font-size: 16px !important;
    line-height: 1.72 !important;
  }

  body {
    max-width: 960px;
    margin: 0 auto !important;
    padding: 18px 20px !important;
  }

  .jp-Notebook,
  .jp-NotebookPanel-notebook,
  .jp-Cell,
  .jp-Cell-inputWrapper,
  .jp-Cell-outputWrapper {
    background: transparent !important;
  }

  .jp-Cell {
    padding: 0 !important;
    margin: 0 0 18px 0 !important;
  }

  .jp-MarkdownCell,
  .jp-MarkdownOutput {
    font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif !important;
  }

  .jp-MarkdownOutput h1,
  .jp-MarkdownOutput h2,
  .jp-MarkdownOutput h3,
  .jp-MarkdownOutput h4 {
    color: #1f2328 !important;
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    page-break-after: avoid;
  }

  .jp-MarkdownOutput h1 {
    font-size: 28px !important;
    line-height: 1.25 !important;
    margin: 20px 0 18px !important;
    text-align: center;
  }

  .jp-MarkdownOutput h2 {
    font-size: 23px !important;
    margin: 26px 0 13px !important;
    padding-bottom: 7px !important;
    border-bottom: 1px solid var(--border) !important;
  }

  .jp-MarkdownOutput h3 {
    font-size: 19px !important;
    margin: 22px 0 10px !important;
  }

  .jp-MarkdownOutput p,
  .jp-MarkdownOutput li {
    font-size: 16px !important;
  }

  .jp-MarkdownOutput blockquote {
    color: #4b5563 !important;
    border-left: 5px solid var(--border) !important;
    background: #f6f8fa !important;
    margin: 14px 0 !important;
    padding: 10px 16px !important;
  }

  .jp-MarkdownOutput code,
  .jp-RenderedText pre,
  pre,
  code,
  .highlight pre,
  .jp-CodeCell .jp-InputArea-editor {
    font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace !important;
    font-size: 13px !important;
    line-height: 1.55 !important;
  }

  .jp-MarkdownOutput code {
    background: rgba(175, 184, 193, 0.2) !important;
    color: #24292f !important;
    border-radius: 4px !important;
    padding: 0.12em 0.35em !important;
  }

  .jp-CodeCell .jp-InputArea-editor,
  .jp-RenderedText pre,
  div.highlight,
  pre {
    background: var(--code-bg) !important;
    border: 1px solid var(--code-border) !important;
    border-radius: 7px !important;
  }

  .jp-CodeCell .jp-InputArea-editor,
  div.highlight pre {
    padding: 12px 14px !important;
    overflow-wrap: anywhere !important;
    white-space: pre-wrap !important;
  }

  .jp-MarkdownOutput pre {
    padding: 10px 12px !important;
    white-space: pre !important;
    overflow: hidden !important;
    font-size: 10.5px !important;
    line-height: 1.5 !important;
  }

  .jp-InputPrompt,
  .jp-OutputPrompt {
    color: #8c959f !important;
    font-family: "JetBrains Mono", Consolas, monospace !important;
    font-size: 13px !important;
    min-width: 62px !important;
  }

  .jp-OutputArea-output {
    background: var(--output-bg) !important;
    border-left: 3px solid #d8dee4 !important;
    padding: 8px 12px !important;
    margin-top: 5px !important;
  }

  table {
    border-collapse: collapse !important;
    width: 100% !important;
  }

  th,
  td {
    border: 1px solid var(--border) !important;
    padding: 6px 10px !important;
  }

  img {
    max-width: 100% !important;
  }
</style>
"""


def edge_path() -> str:
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


def inject_style() -> None:
    html = HTML.read_text(encoding="utf-8")
    if "</head>" in html:
        html = html.replace("</head>", VSCODE_STYLE + "\n</head>", 1)
    else:
        html = VSCODE_STYLE + html
    HTML.write_text(html, encoding="utf-8")


def print_pdf() -> None:
    user_data = Path(tempfile.mkdtemp(prefix="llm-basics-print-"))
    port = 9232
    proc = subprocess.Popen(
        [
            edge_path(),
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
    inject_style()
    print_pdf()
    print(f"Wrote {HTML}")
    print(f"Wrote {PDF}")
