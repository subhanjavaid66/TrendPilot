
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def test_gemma():
    prompt = "Explain what TrendPilot AI assistant could do in three simple points."

    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        print("\nGemma Response:")
        print(result["response"])

    except requests.exceptions.RequestException as error:
        print("Connection Error:", error)


if __name__ == "__main__":
    test_gemma()
