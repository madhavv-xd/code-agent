import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from context import build_context
from llm import ask

console = Console()

INTENTS = {
    "explain":  ['explain', 'what does', 'how does', 'tell me about',
                 'describe', 'what is', 'walk me through'],
    "review":   ['review', 'check', 'find bugs', 'any issues',
                 'edge cases', 'problems', 'wrong', 'audit'],
    "improve":  ['improve', 'refactor', 'better', 'optimize',
                 'clean', 'suggestions', 'best practice'],
    "fix":      ['fix', 'error', 'bug', 'crash', 'broken',
                 'not working', 'failing', 'exception'],
    "debug":   ["bug", "error", "traceback", "exception", "crash", "failing",
    "stacktrace"],
    "optimize": ["performance", "speed", "latency", "memory", "slow", "bottleneck"], 
}

def detect_intent(question):
    q = question.lower()
    for intent, keywords in INTENTS.items():
        if any(k in q for k in keywords):
            return intent
    return "general"

COT = "\nThink step by step before answering. Show code examples where helpful."

PROMPTS = {
    "explain": "You are a coding assistant that explains code clearly. Cover: purpose, inputs/outputs, key logic." + COT,
    "review":  "You are a senior code reviewer. Find bugs, edge cases, security issues, error handling problems. Format: ## Issues\n## Suggestions\n## Overall" + COT,
    "improve": "You are a code quality assistant. Suggest improvements with before/after examples. Format: ## What to improve\n## Changes (with code)" + COT,
    "fix":     "You are a debugging assistant. Find root cause and provide a fix. Format: ## Root cause\n## Fix\n## Prevention" + COT,
    "general": "You are a helpful coding assistant. Answer naturally and concisely. Use markdown for code.",
}

LABELS = {
    "explain": ("blue",   "Explanation"),
    "review":  ("yellow", "Code Review"),
    "improve": ("cyan",   "Improvements"),
    "fix":     ("red",    "Fix"),
    "general": ("green",  "Response"),
}

@click.command()
@click.option('--file',  '-f', default=None,  help='File to focus on')
@click.option('--root',  '-r', default='.',   help='Project root')
@click.option('--model', '-m', default=None,  help='qwen / llama / mistral / gemma / deepseek')
@click.option('--save',  '-s', is_flag=True,  help='Save responses to suggestions.md')
def main(file, root, model, save):
    console.print("[bold green]Code Agent[/bold green] — type 'quit' to exit\n")
    if file:
        console.print(f"[dim]Focusing on: {file}[/dim]\n")

    history = []

    while True:
        try:
            question = Prompt.ask("[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if question.lower() in ('quit', 'exit', 'q'):
            break

        if not question.strip():
            continue

        intent = detect_intent(question)

        if intent != "general":
            context = build_context(question, file_path=file, project_root=root)
        else:
            context = question

        if history:
            history_text = "\n".join(
                [f"Q: {h[0]}\nA: {h[1]}" for h in history[-2:]]
            )
            full_message = f"Previous conversation:\n{history_text}\n\n{context}"
        else:
            full_message = context

        console.print(f"\n[dim]Thinking ({intent})...[/dim]")

        try:
            answer = ask(PROMPTS[intent], full_message, model=model)
            history.append((question, answer))

            color, label = LABELS[intent]
            console.print(f"\n[bold {color}]{label}:[/bold {color}]")
            console.print(Markdown(answer))
            console.print()

            if save:
                with open("suggestions.md", "a") as f:
                    f.write(f"## {label}\n**Q:** {question}\n\n{answer}\n\n---\n")
                console.print("[dim]saved to suggestions.md[/dim]\n")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")

if __name__ == '__main__':
    main()