# Code Agent

A terminal-based AI coding assistant that reads your code and suggests improvements using Groq's free API.

## Requirements

- Python 3.8+
- Git
- Groq API key (free) — get one at https://console.groq.com

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
GROQ_API_KEY=your-key-here
DEFAULT_MODEL=gpt120b
```

---

## Run locally
```bash
# focus on a specific file
python agent.py --file src/main.py

# scan whole project
python agent.py --root .

# both
python agent.py --file src/main.py --root .
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

## Available models

| Shortname | Model | Best for |
|---|---|---|
| `gpt120b` | gpt-oss-120b | code (default) |
| `gpt20b` | gpt-oss-20b | fast general use |

Switch models with `--model` flag:
```bash
codeagent --file app.py --model gpt20b
codeagent --file app.py --model gpt120b
```

---

## Usage examples
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

# fix an error
codeagent --file main.py
> fix the error in this file

# scan whole project
codeagent --root .
> what does this project do

# save suggestions to file
codeagent --file app.py --save
> review this file
# saves to suggestions.md
```

---

## Intent detection

The agent automatically detects what kind of help you need and adjusts its response format:

| Your question | Intent | Output |
|---|---|---|
| "explain this" / "what does this do" | Explain | Blue — covers purpose, inputs, logic |
| "find bugs" / "review this" | Review | Yellow — issues, suggestions, overall |
| "improve this" / "refactor" | Improve | Cyan — before/after code examples |
| "fix this" / "there's an error" | Fix | Red — root cause, fix, prevention |
| "hello" / anything else | General | Green — normal response |

---

## Getting updates
```bash
cd ~/code-agent
git pull
pip install -r requirements.txt
```

---

## Project structure
```
code-agent/
├── agent.py         # main entry point, chat loop, intent detection
├── context.py       # reads files, builds prompt
├── llm.py           # groq API calls, model routing
├── config.py        # loads settings from .env
└── requirements.txt
```

---

## Troubleshooting

**codeagent command not found** — run `source ~/.bashrc` or `source ~/.zshrc`.

**Invalid API key** — make sure `.env` exists in the `code-agent` folder and `GROQ_API_KEY` is correct.

**Rate limited** — Groq free tier allows 30 requests/minute and 14,400/day. Switch models with `--model` flag to spread usage.

**File not found** — make sure the path you pass to `--file` is correct relative to where you run the command.

**No response / timeout** — Groq might be briefly down. Wait a few seconds and try again.