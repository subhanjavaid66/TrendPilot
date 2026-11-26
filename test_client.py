from agent.ollama_client import generate_response

try:
    answer = generate_response(
        "Explain TrendPilot in three simple points."
    )

    print("\nGemma Response:")
    print(answer)

except RuntimeError as error:
    print("Error:", error)