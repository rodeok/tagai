# 🤖 TagAI

**TagAI** is an autonomous AI coding assistant that supports a wide range of LLM providers. It features a robust **self-healing loop** that writes, tests, and fixes code until it runs perfectly.

## ✨ Features

- **🌐 Multi-LLM Support**: Use your favorite models from **Groq**, **OpenAI**, **Anthropic (Claude)**, **Google Gemini**, or even **Local LLMs** (via Ollama/LM Studio).
- **🩺 Self-Healing**: Automatically detects errors during execution and iterates until the code is clean.
- **🛠️ Built-in Tools**: Full filesystem access and integrated Git tools with safety prompts.
- **🛡️ Auto-Verification**: Automatically verifies your API keys and model configuration during setup.
- **🎤 Natural Language Git**: Manage your repository using plain English.

## 📦 Installation

Install TagAI directly from GitHub:

```bash
pip install git+https://github.com/rodeok/tagai.git
```

## ⚙️ Configuration

TagAI supports multiple providers. You will be prompted to choose one when you first run the app.

### Included Providers:
- **Groq**: Lightning-fast inference (Llama 3.3, etc.)
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude 3.5 Sonnet, Opus
- **Google Gemini**: Gemini 1.5 Pro/Flash
- **Local**: Any OpenAI-compatible endpoint (Ollama, LM Studio)

### Setup Wizard
Simply run `tagai` and follow the prompts to select your provider, model, and enter your API key. Everything is saved to a local `.env` file for you.

To force a reconfiguration, run:
```bash
tagai
# Type 'config' inside the interactive session
```

## 🚀 Usage

Start the interactive session:
```bash
tagai
```

### Commands:
- `build <file>`: Describe a task and have TagAI build and self-heal the file.
- `git <cmd>`: Run raw git commands directly (e.g., `git status`).
- `config`: Switch providers or models.
- `tokens`: View current session token usage.
- `clear`: Reset the conversation history.
- `exit`: Quit the session.

### Example:
> **You:** "build a python script that fetches the weather for London"
>
> **TagAI:** "Building 'weather.py'... 🩺 Self-Healing Iteration 1... 🛡️ No errors detected. Build successful."

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
