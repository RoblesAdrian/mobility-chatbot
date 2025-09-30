import requests

OLLAMA_MODEL = "gemma:2b"

def ask_ollama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    return response.json()["response"].strip()
