# 从零手写大模型入门教程

这是一个面向 **0 基础学习者** 的大模型入门教程项目。

用尽量朴素的语言和可运行的 notebook，把大模型训练前最容易被跳过的部分讲清楚：

- 文本为什么要先变成数字
- tokenizer 是怎么把文本切成 token ID 的
- 训练样本为什么是“看到前面，预测下一个”
- token embedding 和 position embedding 分别解决什么问题
- 一段自然语言最终如何变成 Transformer 能计算的张量

当前内容主要来自我学习《LLMs from Scratch》Ch02 时整理和重写的练习笔记，并进一步改写成更适合初学者跟练的教程。

## 当前章节

| 章节 | Notebook | 导出版本 |
| --- | --- | --- |
| Ch02 文本数据处理 | `notebooks/ch02_text_data_processing.ipynb` | `exports/ch02_text_data_processing.pdf` |

## 项目结构

```text
llm-from-scratch-note/
├─ data/
│  └─ the-verdict.txt
├─ exports/
│  ├─ ch02_text_data_processing.html
│  └─ ch02_text_data_processing.pdf
├─ notebooks/
│  └─ ch02_text_data_processing.ipynb
├─ scripts/
│  └─ export.py
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

## 环境要求

推荐环境：

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- VS Code 或 JupyterLab
- Windows/macOS/Linux 均可

Python 依赖见 `pyproject.toml`：

- `torch`
- `tiktoken`
- `requests`
- `jupyter`
- `nbconvert`
- `pypdfium2`
- `websocket-client`

## 快速开始

进入项目目录：

```bash
cd llm-from-scratch-note
```

安装依赖（uv 会自动创建虚拟环境）：

```bash
uv sync
```

打开 notebook：

```bash
uv run jupyter lab notebooks/ch02_text_data_processing.ipynb
```

也可以直接用 VS Code 打开整个项目目录，然后运行 notebook。

## 重新导出 PDF

项目里带了一个导出脚本，会把 notebook 导出为 nbconvert 原始风格的 HTML 和 PDF：

```bash
uv run python scripts/export.py
```

输出文件：

```text
exports/ch02_text_data_processing.html
exports/ch02_text_data_processing.pdf
```

说明：这个导出脚本在 Windows 上会优先使用 Microsoft Edge 的无头打印能力，并关闭默认页眉页脚，所以 PDF 不会带文件名、日期、路径和页码。

## 数据说明

`data/the-verdict.txt` 是本教程使用的小型英文文本样本，来自《LLMs from Scratch》Ch02 示例数据，用于演示 tokenizer、滑动窗口和 embedding 输入构造。

## 路线规划

后续计划继续把内容改写为更基础的中文入门教程：

- Ch03 Attention 机制
- Ch04 GPT 模型结构
- Ch05 预训练流程
- Ch06/Ch07 微调与应用

## 致谢

本项目的学习路线和部分示例数据参考自 Sebastian Raschka 的 [LLMs from Scratch](https://github.com/rasbt/LLMs-from-scratch)。

本项目会尽量用自己的语言重新组织解释，目标是做成一份更适合中文初学者跟练的入门教程。
