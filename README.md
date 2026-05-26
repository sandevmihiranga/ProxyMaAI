# ProxyMaAI

*A Better Context Manager for Local AI using llama.cpp*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ProxyMaAI is a lightweight memory proxy for local AI models running with llama.cpp/llamafile.
It helps prevent context overflow by automatically shifting old tokens, cleaning stale chat history, and keeping long conversations responsive — even on lower-end hardware.

Designed for people who want:

* Longer AI conversations without crashes
* Faster and smoother replies
* Better memory handling on limited RAM
* Automatic context cleanup
* A more stable local AI experience

---

# Features

* Dynamic context shifting
* Automatic old-token cleanup
* Lower RAM usage during long chats
* Helps reduce repetition loops
* Works with llama.cpp web UI
* Optimized for low-end and CPU-only systems
* Simple setup with Python + llamafile

---

# Quick Start

## 1. Prerequisites

Before installing ProxyMaAI, make sure you have:

* A GGUF model from [Hugging Face](https://huggingface.co?utm_source=chatgpt.com) or another provider
* Python 3.10+
* `requests` library installed
* A copy of [llamafile](https://github.com/mozilla-ai/llamafile/releases?utm_source=chatgpt.com)

Install Python dependency:

```bash
pip install requests
```

Rename your downloaded llamafile executable to:

```text
llamafile.exe
```

---

## 2. Installation

Download or place these files inside your project folder:

```text
context_proxy.py
ai_launcher.bat
```

---

## 3. Folder Structure

Your ProxyMaAI folder should look like this:

```text
ProxyMaAI/
│
├── models/
├── ai_launcher.bat
├── context_proxy.py
└── llamafile.exe
```

Place your GGUF model inside the `models` folder.

Example:

```text
models/
└── mistral-7b-instruct.Q4_K_M.gguf
```

---

# How It Works

ProxyMaAI acts like a middle layer between your frontend and the AI model.

Instead of letting the context window completely fill up and slow down:

* Old conversation tokens get shifted automatically
* Stale context gets cleaned
* Active conversation stays prioritized
* Memory usage stays more stable over time

This allows longer chats without requiring massive hardware upgrades.

---

# Designed For

* llama.cpp users
* llamafile users
* CPU-only AI setups
* Low RAM systems
* Experimental local AI projects
* People trying to push smaller hardware further

---

# Notes

* ProxyMaAI does **not** modify your AI model
* Works best with instruct/chat models
* Performance depends on your hardware and GGUF quantization

---

# License

This project is licensed under the MIT License.
