# ProxyMaAI

A Better Context Manager for Local AI using llama.cpp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A memory proxy that prevents context overflow by automatically shifting old tokens, cleaning stale chat history, and keeping conversations smooth on low-end hardware. Designed to extend long chats, improve responsiveness, and make local AI feel smarter without needing more RAM or GPU power.

## Quick Start

### 1. Prerequisites
- Download your own GGUF model from Hugging Face or preferred provider
- Install Python 3.10+ and `pip install -r requirements.txt`
- Install [llama.cpp](https://github.com/ggerganov/llama.cpp) with server support

### 2. Download and Configure Models
1. Place your GGUF model file in the ProxyMaAI folder
2. Rename it to match the `MODEL_NAME.gguf` in `ai_launcher.bat`

```python
set MODEL=your_model.gguf # Must match your downloaded file
```

### 3. Configure Proxy Manager
1. In the `ai_launcher.bat`
