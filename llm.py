import config
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

console = Console()


def resolve_model(model):
    if model in config.GROQ_MODELS:
        return config.GROQ_MODELS[model]
    # Allow raw model strings (e.g. "llama-3.3-70b-versatile") to pass through
    return model


def ask(system_prompt, user_message, model=None, stream=True):
    """
    Call the Groq API.
    If stream=True, streams tokens to the terminal and returns the full text.
    If stream=False, blocks and returns the full text directly.
    """
    from openai import OpenAI

    selected = model or config.DEFAULT_MODEL
    model_string = resolve_model(selected)

    display = selected if selected in config.GROQ_MODELS else model_string

    client = OpenAI(
        api_key=config.GROQ_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    if stream:
        return _stream(client, model_string, messages)
    else:
        resp = client.chat.completions.create(
            model=model_string,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return resp.choices[0].message.content


def _stream(client, model_string, messages):
    """Stream response tokens, render markdown live, return full text."""
    full_text = ""

    with client.chat.completions.create(
        model=model_string,
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
        stream=True,
    ) as stream:
        with Live(Text(""), console=console, refresh_per_second=15) as live:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_text += delta
                live.update(Markdown(full_text))

    return full_text