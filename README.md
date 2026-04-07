# 🤖 TagAI

**TagAI** is an autonomous AI coding assistant powered by Groq. it features a self-healing loop that writes, tests, and fixes code until it works perfectly.

## ✨ Features
- **🚀 Ultra-fast Code Generation**: Powered by Llama 3.3 and other Groq-hosted models.
- **🩺 Self-Healing**: Automatically detects errors during execution and iterates until the code is clean.
- **🛠️ Built-in Tools**: Full filesystem access and integrated Git tools.
- **🎤 Natural Language Git**: Manage your repository using plain English.

## 📦 Installation

Install TagAI directly from GitHub:

```bash
pip install git+https://github.com/rodeok/tagai.git
```

## ⚙️ Configuration

TagAI requires a **Groq API Key**. You can get one at [Groq Cloud](https://console.groq.com/).

### Option 1: Setup Wizard (Recommended)
Simply run `tagai` and follow the prompts to enter your API key. It will be saved to a local `.env` file.

### Option 2: Environment Variable
Alternatively, set the key in your terminal:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="your_key_here"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY="your_key_here"
```

## 🚀 Usage

Start the interactive session:
```bash
tagai
```

### Commands:
- `build <file>`: Describe a task and have TagAI build and self-heal the file.
- `git <cmd>`: Run raw git commands directly.
- `tokens`: View current session token usage.
- `clear`: Reset the conversation history.
- `help`: Show the help menu.

### Example:
> **You:** "initialise a git repo, add all files and make an initial commit"
>
> **TagAI:** "✅ Initialised repo... ✅ Added files... ✅ Committed 'initial commit'"

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
