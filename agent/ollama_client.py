import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Cap on generated tokens per call. Keeps a slow laptop from writing very long replies.
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "300"))


def generate_response(prompt, system_prompt=None, temperature=0.3):
    """
    Send a prompt to the local Ollama model and return its response.
    Prints how long each call took so you can see progress and speed.
    """

    full_prompt = prompt

    if system_prompt:
        full_prompt = f"System instructions:\n{system_prompt}\n\nUser request:\n{prompt}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "keep_alive": "30m",  # keep the model loaded between calls
        "options": {
            "temperature": temperature,
            "num_predict": OLLAMA_NUM_PREDICT
        }
    }

    started = time.time()
    print("   ... waiting for the model", flush=True)

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()
        print(f"   [model replied in {time.time() - started:.0f}s]", flush=True)
        return result.get("response", "").strip()

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Ollama took too long to respond. Please try again."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error    
