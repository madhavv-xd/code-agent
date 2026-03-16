import os
import sys
import time
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.rule import Rule
from rich.prompt import Prompt
from rich import box
from rich.style import Style
from rich.align import Align
from rich.padding import Padding

import config
from context import build_context
from llm import ask

console = Console()

# ── Intent detection ──────────────────────────────────────────────────────────

INTENTS = {
    "fix":      ['fix', 'error', 'bug', 'crash', 'broken',
                 'not working', 'failing', 'exception', 'traceback'],
    "review":   ['review', 'check', 'find bugs', 'any issues',
                 'edge cases', 'problems', 'wrong', 'audit', 'security'],
    "improve":  ['improve', 'refactor', 'better', 'optimize',
                 'clean', 'suggestions', 'best practice', 'rewrite'],
    "explain":  ['explain', 'what does', 'how does', 'tell me about',
                 'describe', 'what is', 'walk me through', 'understand'],
}

# Priority order: more specific intents first
INTENT_PRIORITY = ["fix", "review", "improve", "explain"]

def detect_intent(question):
    q = question.lower()
    for intent in INTENT_PRIORITY:
        if any(k in q for k in INTENTS[intent]):
            return intent
    return "general"


# ── Prompts ───────────────────────────────────────────────────────────────────

COT = "\nThink step by step. Show before/after code examples where helpful."

PROMPTS = {
    "explain": (
        "You are a coding assistant that explains code clearly and concisely. "
        "Cover: purpose, inputs/outputs, key logic, potential gotchas." + COT
    ),
    "review":  (
        "You are a senior code reviewer. Identify bugs, edge cases, security issues, "
        "and error handling gaps.\n"
        "Format your response as:\n"
        "## Issues\n## Suggestions\n## Overall assessment" + COT
    ),
    "improve": (
        "You are a code quality expert. Suggest concrete improvements with before/after "
        "code examples.\n"
        "Format your response as:\n"
        "## What to improve\n## Changes (with code)" + COT
    ),
    "fix":     (
        "You are a debugging expert. Find the root cause and provide a working fix.\n"
        "Format your response as:\n"
        "## Root cause\n## Fix\n## How to prevent this" + COT
    ),
    "general": (
        "You are a helpful coding assistant. You are given a project structure and "
        "optionally a focused file. Answer questions naturally, concisely, and accurately. "
        "Use markdown for code blocks."
    ),
}

# ── Visual config ─────────────────────────────────────────────────────────────

INTENT_META = {
    "explain": {"color": "cyan",         "icon": "◆", "label": "Explain"},
    "review":  {"color": "yellow",       "icon": "◈", "label": "Review"},
    "improve": {"color": "bright_cyan",  "icon": "◇", "label": "Improve"},
    "fix":     {"color": "bright_red",   "icon": "✖", "label": "Fix"},
    "general": {"color": "bright_green", "icon": "◉", "label": "Answer"},
}

SLASH_COMMANDS = {
    "/help":    "Show this help",
    "/file":    "Switch focused file   e.g. /file src/main.py",
    "/model":   "Switch model          e.g. /model llama3-8b",
    "/history": "Show conversation history",
    "/clear":   "Clear history",
    "/save":    "Toggle save-to-file",
    "/tree":    "Print project tree",
    "/quit":    "Exit",
}


# ── UI helpers ────────────────────────────────────────────────────────────────

def print_banner():
    console.print()
    banner = Text()
    banner.append("  ◆ ", style="bright_cyan bold")
    banner.append("Code", style="white bold")
    banner.append("Agent", style="bright_cyan bold")
    banner.append("  —  intelligent code assistant", style="dim")
    console.print(banner)
    console.print(Text("  type /help for commands  ·  Ctrl+C to exit", style="dim"))
    console.print()


def print_status_bar(file_path, model, save, history_count):
    items = []

    if file_path:
        short = os.path.relpath(file_path)
        items.append(Text(f" 📄 {short} ", style="bold white on #1a1a2e"))
    else:
        items.append(Text(" 📁 no file ", style="dim on #1a1a2e"))

    model_display = model or config.DEFAULT_MODEL
    items.append(Text(f" ⚡ {model_display} ", style="bold cyan on #1a1a2e"))

    if history_count:
        items.append(Text(f" 💬 {history_count} turns ", style="dim on #1a1a2e"))

    if save:
        items.append(Text(" 💾 saving ", style="bold green on #1a1a2e"))

    row = Text("  ").join(items)
    console.print(Padding(row, (0, 0, 1, 0)))


def print_help():
    console.print()
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t.add_column("cmd",  style="bright_cyan", no_wrap=True)
    t.add_column("desc", style="dim")
    for cmd, desc in SLASH_COMMANDS.items():
        t.add_row(cmd, desc)
    console.print(Panel(t, title="[bold]Commands[/bold]", border_style="dim", padding=(0, 1)))

    console.print()
    t2 = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t2.add_column("keyword", style="yellow", no_wrap=True)
    t2.add_column("intent",  style="dim")
    for intent, kws in INTENTS.items():
        meta = INTENT_META[intent]
        t2.add_row(
            f"[{meta['color']}]{meta['icon']} {meta['label']}[/{meta['color']}]",
            ", ".join(kws[:4]) + " …"
        )
    console.print(Panel(t2, title="[bold]Intent detection[/bold]", border_style="dim", padding=(0, 1)))
    console.print()


def print_history(history):
    if not history:
        console.print("[dim]  No history yet.[/dim]\n")
        return
    console.print()
    for i, (q, a, intent) in enumerate(history, 1):
        meta = INTENT_META[intent]
        console.print(f"  [{meta['color']}]{meta['icon']}[/{meta['color']}] [bold]#{i}[/bold]  {q}")
        # Show a one-line preview
        preview = a.split("\n")[0][:80]
        console.print(f"     [dim]{preview}…[/dim]")
    console.print()


def print_tree(root):
    from context import get_file_tree
    tree = get_file_tree(root)
    console.print(Panel(tree, title="[bold]Project tree[/bold]", border_style="dim"))


def thinking_spinner(intent):
    meta = INTENT_META[intent]
    console.print(
        f"\n  [{meta['color']}]{meta['icon']}  {meta['label']}…[/{meta['color']}]\n",
    )


# ── Slash command handlers ────────────────────────────────────────────────────

def handle_slash(command, state):
    """
    state = dict with keys: file, model, save, history, root
    Returns (handled: bool, should_continue: bool)
    """
    parts = command.strip().split(None, 1)
    cmd   = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/quit", "/exit", "/q"):
        return True, False

    if cmd == "/help":
        print_help()
        return True, True

    if cmd == "/clear":
        state["history"].clear()
        console.print("[dim]  History cleared.[/dim]\n")
        return True, True

    if cmd == "/history":
        print_history(state["history"])
        return True, True

    if cmd == "/tree":
        print_tree(state["root"])
        return True, True

    if cmd == "/save":
        state["save"] = not state["save"]
        status = "on" if state["save"] else "off"
        console.print(f"[dim]  Save to suggestions.md: {status}[/dim]\n")
        return True, True

    if cmd == "/file":
        if not arg:
            console.print("[dim]  Usage: /file <path>[/dim]\n")
            return True, True
        candidate = os.path.join(state["root"], arg) if not os.path.isabs(arg) else arg
        if os.path.exists(candidate):
            state["file"] = candidate
            console.print(f"[dim]  Switched to: {candidate}[/dim]\n")
        else:
            console.print(f"[yellow]  File not found: {candidate}[/yellow]\n")
        return True, True

    if cmd == "/model":
        if not arg:
            models = list(config.GROQ_MODELS.keys())
            console.print(f"[dim]  Available models: {', '.join(models)}[/dim]\n")
            return True, True
        state["model"] = arg
        console.print(f"[dim]  Model switched to: {arg}[/dim]\n")
        return True, True

    # Unknown slash command
    console.print(f"[yellow]  Unknown command: {cmd}. Type /help for available commands.[/yellow]\n")
    return True, True


# ── Save helper ───────────────────────────────────────────────────────────────

def save_response(question, answer, intent, label):
    with open("suggestions.md", "a", encoding="utf-8") as f:
        f.write(f"## {label}\n**Q:** {question}\n\n{answer}\n\n---\n")
    console.print("[dim]  ✓ saved to suggestions.md[/dim]\n")


# ── Main ──────────────────────────────────────────────────────────────────────

@click.command()
@click.option('--file',      '-f', default=None,  help='File to focus on')
@click.option('--root',      '-r', default='.',   help='Project root')
@click.option('--model',     '-m', default=None,  help='llama3-70b / llama3-8b / mixtral / gemma')
@click.option('--save',      '-s', is_flag=True,  help='Save responses to suggestions.md')
@click.option('--max-lines', '-l', default=300,   help='Max lines per file (0 = no limit)')
@click.option('--no-stream',       is_flag=True,  help='Disable streaming output')
def main(file, root, model, save, max_lines, no_stream):

    # Validate config before anything else
    try:
        config.validate()
    except EnvironmentError as e:
        console.print(f"\n[bold red]Configuration error:[/bold red]\n{e}\n")
        sys.exit(1)

    # Auto-detect file
    if not file:
        for candidate in ['main.py', 'app.py', 'index.py', 'index.js', 'app.js']:
            path = os.path.join(root, candidate)
            if os.path.exists(path):
                file = path
                break

    # Mutable state (modified by slash commands)
    state = {
        "file":  file,
        "model": model,
        "save":  save,
        "root":  root,
        "history": [],  # list of (question, answer, intent)
    }

    print_banner()

    if state["file"]:
        console.print(f"  [dim]Focused on:[/dim] [bold]{os.path.relpath(state['file'])}[/bold]\n")
    if max_lines:
        console.print(f"  [dim]Max lines:[/dim] {max_lines}\n")

    stream = not no_stream

    while True:
        # ── Status bar ──
        print_status_bar(state["file"], state["model"], state["save"], len(state["history"]))

        # ── Prompt ──
        try:
            question = Prompt.ask("[bold bright_cyan]›[/bold bright_cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]  Goodbye![/dim]\n")
            break

        question = question.strip()
        if not question:
            continue

        # ── Slash commands ──
        if question.startswith("/"):
            handled, should_continue = handle_slash(question, state)
            if handled and not should_continue:
                console.print("[dim]  Goodbye![/dim]\n")
                break
            continue

        # ── Detect intent ──
        intent = detect_intent(question)
        meta   = INTENT_META[intent]

        # ── Build context ──
        context = build_context(
            question,
            file_path=state["file"],
            project_root=state["root"],
            max_lines=max_lines,
        )

        # ── Inject history (last 3 turns, with cap notice) ──
        HISTORY_WINDOW = 3
        h = state["history"]
        if h:
            if len(h) > HISTORY_WINDOW:
                console.print(f"[dim]  (showing last {HISTORY_WINDOW} of {len(h)} turns)[/dim]")
            recent = h[-HISTORY_WINDOW:]
            history_text = "\n".join([f"Q: {r[0]}\nA: {r[1]}" for r in recent])
            full_message = f"Previous conversation:\n{history_text}\n\n{context}"
        else:
            full_message = context

        # ── Call LLM ──
        thinking_spinner(intent)

        try:
            answer = ask(
                PROMPTS[intent],
                full_message,
                model=state["model"],
                stream=stream,
            )

            # Print header + answer panel
            console.print()
            console.rule(
                f"[bold {meta['color']}]{meta['icon']} {meta['label']}[/bold {meta['color']}]",
                style="dim"
            )
            console.print()

            if not stream:
                # Stream already printed via Live; for no-stream, print now
                console.print(Markdown(answer))

            console.print()
            console.rule(style="dim")
            console.print()

            # Store in history
            state["history"].append((question, answer, intent))

            # Save if requested
            if state["save"]:
                save_response(question, answer, intent, meta["label"])

        except Exception as e:
            console.print(f"\n[bold red]  Error:[/bold red] {e}\n")
            if "AuthenticationError" in type(e).__name__:
                console.print("[dim]  Check your GROQ_API_KEY in .env[/dim]\n")


if __name__ == '__main__':
    main()