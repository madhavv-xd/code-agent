# ◆ CodeAgent

> An interactive terminal coding assistant powered by [Groq](https://console.groq.com). Ask questions about your codebase and get streamed, intent-aware responses — like Claude Code, but for any project.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- **Streaming output** — tokens print live as they arrive, no blank waiting
- **Intent detection** — automatically routes your question to a specialised prompt (`fix`, `review`, `improve`, `explain`)
- **Slash command system** — switch files, models, and settings mid-session
- **Smart context loading** — loads only the relevant function or line range, not the whole file
- **Token budget guard** — auto-trims context before hitting model limits
- **Conversation history** — remembers the last 3 turns for follow-up questions
- **Save to file** — optionally append all responses to `suggestions.md`

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourname/codeagent.git
cd codeagent

# Install dependencies
pip install openai rich click python-dotenv
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_key_here
DEFAULT_MODEL=llama3-70b
```

> Get a free API key at [console.groq.com](https://console.groq.com) — no credit card required.

---

## 🚀 Usage

```bash
# Basic — auto-detects main.py / app.py in current directory
python agent.py

# Focus on a specific file
python agent.py --file src/api.py

# Point at a different project root
python agent.py --root ~/projects/myapp --file src/main.py

# Use a faster/smaller model
python agent.py --model llama3-8b

# Save all responses to suggestions.md
python agent.py --save

# Limit lines loaded per file (good for huge files)
python agent.py --max-lines 200

# Disable streaming (wait for full response at once)
python agent.py --no-stream
```

---

## 💬 Slash Commands

Once inside the agent, use these commands at any prompt:

| Command | Description |
|---|---|
| `/file src/foo.py` | Switch the focused file |
| `/model llama3-8b` | Switch model mid-session |
| `/model` | List available models |
| `/history` | Show conversation history |
| `/clear` | Clear conversation history |
| `/save` | Toggle save-to-file on/off |
| `/tree` | Print project file structure |
| `/help` | Show all commands |
| `/quit` | Exit |

---

## 🧠 Intent Detection

Your question is automatically routed to a specialised system prompt based on keywords:

| Intent | Trigger keywords | Response format |
|---|---|---|
| 🔴 **Fix** | fix, bug, error, crash, failing, exception… | Root cause → Fix → Prevention |
| 🟡 **Review** | review, audit, security, edge cases, issues… | Issues → Suggestions → Overall |
| 🔵 **Improve** | refactor, optimize, clean, best practice… | What to improve → Before/After code |
| 🟢 **Explain** | explain, how does, what is, walk me through… | Purpose → Logic → Gotchas |
| ⚪ **General** | anything else | Free-form answer |

Priority order is `fix > review > improve > explain`, so a question like *"find bugs and explain them"* routes to **Review**.

---

## ⚡ Available Models

| Alias | Model | Best for |
|---|---|---|
| `gpt120b` | gpt-oss-120b | Default — best quality |
| `gpt20b` | gpt-oss-20b | Fastest responses |

Switch at any time with `/model <alias>` or pass `--model` at startup.

---

## 🗂 Project Structure

```
codeagent/
├── agent.py      # CLI entry point, REPL loop, slash commands, UI
├── context.py    # File tree, smart scope detection, token budgeting
├── llm.py        # Groq API client with streaming support
├── config.py     # API key loading, model aliases, startup validation
└── .env          # Your API key (not committed)
```

---

## 🔧 How It Works

```
User input
    │
    ▼
detect_intent()        ← keyword match with priority ordering
    │
    ├─► PROMPTS[intent] ← specialised system prompt
    │
    ▼
build_context()        ← file tree + smart scope (function / line range / full file)
    │
    ▼
inject history         ← last 3 turns, with truncation notice
    │
    ▼
ask() → Groq API       ← streams tokens live via Rich Live
    │
    ▼
Rich Markdown output   ← coloured label + formatted response
    │
    └─► suggestions.md  ← optional save
```

---

## 🛠 Configuration

All config lives in `.env`:

```env
GROQ_API_KEY=gsk_...          # Required
DEFAULT_MODEL=gpt120b      # Optional, defaults to llama3-70b
```

If `GROQ_API_KEY` is missing, the agent exits immediately with setup instructions rather than crashing mid-session.

---

## 📋 Requirements

- Python 3.8+
- `openai` — Groq uses an OpenAI-compatible API
- `rich` — terminal UI, markdown rendering, streaming
- `click` — CLI argument parsing
- `python-dotenv` — `.env` file loading

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push and open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.