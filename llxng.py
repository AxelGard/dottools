#!/usr/bin/env python3
import sys
import http.client
import json
import subprocess

from urllib.parse import urlencode
from urllib.request import urlopen


def get_urls(querry:str, searXNG_location="localhost", port=6767, max_number_of_reults:int=5) -> list[str]:  
    params = {"q": querry, "format": "json"}
    query = urlencode(params)

    conn = http.client.HTTPConnection(searXNG_location, port)
    conn.request("GET", f"/search?{query}")

    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return [i["url"] for i in data["results"]][:max_number_of_reults]



def get_ollama_models():
    """
    Returns a list of installed Ollama model names.

    Raises RuntimeError if the ollama command is not available or fails.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("Ollama is not installed or not on PATH")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run ollama list: {e.stderr}") from e

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 1:
        return []

    # Skip header line, extract model name (first column)
    models = []
    for line in lines[1:]:
        # Split on whitespace; model name is the first token
        model = line.split()[0]
        models.append(model)

    return models


def ask_ollama(question: str, model: str = "llama3.2:1b") -> str:
    """
    Send a prompt to local Ollama and return the model's answer as a string.
    Uses only Python's standard library.
    """
    conn = http.client.HTTPConnection("localhost", 11434)

    payload = json.dumps({"model": model, "prompt": question, "stream": False})

    headers = {"Content-Type": "application/json"}

    conn.request("POST", "/api/generate", body=payload, headers=headers)
    response = conn.getresponse()

    if response.status != 200:
        raise RuntimeError(f"Ollama error: {response.status} {response.reason}")

    data = response.read().decode("utf-8")
    conn.close()

    result = json.loads(data)
    return result.get("response", "")


def main(args: list[str]):
    assert len(args) > 2, "bad usage, ask <model> <promt>"
    model = args[0]
    installed_models = get_ollama_models()
    use_model = ""
    for m in installed_models:
        if model in m:
            use_model = m
    promt = """
    Give me a short and direct answer to the question:
        """ + " ".join(
        args[1:]
    )
    #answer = ask_ollama(promt, model=use_model)
    #if "<think>" in answer:
    #    answer = answer.split("<think>")[-1]
    #print(answer)
    print(get_urls(" ".join(args[1:])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
