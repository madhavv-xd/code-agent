import config
from rich.console import Console

console = Console()

def resolve_model(model):
    if model in config.GROQ_MODELS:
        return config.GROQ_MODELS[model]
    return model

def ask(system_prompt, user_message, model=None):
    from openai import OpenAI

    selected = model or config.DEFAULT_MODEL
    model_string = resolve_model(selected)

    display = selected if selected in config.GROQ_MODELS else model_string
    console.print(f"[dim]model: groq / {display}[/dim]")

    client = OpenAI(
        api_key=config.GROQ_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    resp = client.chat.completions.create(
        model=model_string,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return resp.choices[0].message.content