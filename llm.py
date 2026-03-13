import requests
import config

def ask_gemini(system_prompt, user_message):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.GEMINI_KEY)
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=user_message
    )
    return resp.text

def ask_ollama(system_prompt, user_message):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "stream": False
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

def ask(system_prompt, user_message):
    if config.PROVIDER == "gemini":
        return ask_gemini(system_prompt, user_message)
    elif config.PROVIDER == "ollama":
        return ask_ollama(system_prompt, user_message)
    else:
        raise ValueError(f"Unknown provider: {config.PROVIDER}")