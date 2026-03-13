# Code Agent

A terminal-based AI coding assistant that reads your code and suggests improvements. Supports Gemini API and local Ollama models.

## Requirements

- Python 3.8+
- Git
- Ollama (optional, for local models)

## Installation

### Step 1 — Clone the repo
```bash
git clone https://github.com/yourusername/code-agent.git
cd code-agent
```

### Step 2 — Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Create a `.env` file
Create a file called `.env` inside the `code-agent` folder:
```
# use gemini (recommended)
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your-key-here

# or use ollama (local, free)
MODEL_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5-coder
```
Get a free Gemini API key at https://aistudio.google.com

---

## Run locally
```bash
# focus on a specific file
python agent.py --file src/main.py

# scan whole project
python agent.py --root .
```

---

## Make it a global command

Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
alias codeagent="$HOME/code-agent/venv/bin/python $HOME/code-agent/agent.py"
```

Reload:
```bash
source ~/.bashrc   # or source ~/.zshrc
```

Now use it from any folder:
```bash
cd ~/any-project
codeagent --file src/main.py
```

---

## Ollama setup (optional)

Install Ollama from https://ollama.com then pull a model:
```bash
ollama pull qwen2.5-coder   # best for code (~4GB)
ollama pull llama3.2:3b     # smaller and faster (~2GB)
```

Start Ollama:
```bash
ollama serve
```

Update your `.env`:
```
MODEL_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5-coder
```

---

## Usage
```bash
# explain a file
codeagent --file app.py
> what does this file do

# find bugs
codeagent --file src/auth.py
> find any bugs or edge cases

# improve code
codeagent --file utils.py
> how can i improve this code
```

---

## Getting updates
```bash
cd ~/code-agent
git pull
pip install -r requirements.txt
```

---

## Troubleshooting

**codeagent command not found** — run `source ~/.bashrc` or `source ~/.zshrc` again.

**Ollama 404 error** — Ollama isn't running, start it with `ollama serve`.

**Model not found** — run `ollama list` to see exact model names, update `.env` to match exactly e.g. `qwen2.5-coder:7b`.

**Slow responses** — switch to Gemini or use a smaller model like `llama3.2:3b`.

**API key error** — make sure `.env` exists in the `code-agent` folder and `GEMINI_API_KEY` is set correctly.