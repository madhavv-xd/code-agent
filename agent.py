import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from context import build_context
from llm import ask

console = Console()

SYSTEM_PROMPT = """You are a helpful coding assistant.
You are given a project's file structure and optionally a specific file's content.
Answer questions about the code when asked.
If the user says hello or asks a general question, respond normally without forcing code context.
Keep responses concise and relevant to what was actually asked.
Format code using markdown when showing code."""

CODE_KEYWORDS = ['file', 'code', 'function', 'bug', 'error', 'explain',
                 'fix', 'improve', 'what does', 'how does', 'review', 'class']

def is_code_question(question):
    return any(keyword in question.lower() for keyword in CODE_KEYWORDS)

@click.command()
@click.option('--file', '-f', default=None, help='Specific file to focus on')
@click.option('--root', '-r', default='.',  help='Project root directory')
@click.option('--model', '-m', default=None, help='Model to use (overrides .env)')
def main(file, root, model):
    if model:
        import config
        config.OLLAMA_MODEL = model

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

        # only build file context if it's a code-related question
        if is_code_question(question):
            context = build_context(question, file_path=file, project_root=root)
        else:
            context = question  # just send question directly

        if history:
            history_text = "\n".join(
                [f"Q: {h[0]}\nA: {h[1]}" for h in history[-1:]]
            )
            full_message = f"Previous conversation:\n{history_text}\n\n{context}"
        else:
            full_message = context

        console.print("\n[dim]Thinking...[/dim]")

        try:
            answer = ask(SYSTEM_PROMPT, full_message)
            history.append((question, answer))
            console.print("\n[bold green]Agent:[/bold green]")
            console.print(Markdown(answer))
            console.print()

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")

if __name__ == '__main__':
    main()