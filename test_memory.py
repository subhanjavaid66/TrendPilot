
from memory.history import save_history, get_history


sample_result = {
    "plan": {
        "topic": "Artificial Intelligence"
    },
    "content": "AI is transforming the future.",
    "analysis": {
        "quality_score": 90
    },
    "review": "Good content."
}


save_history(sample_result)

history = get_history()

print("\n========== SAVED HISTORY ==========")
print(history)
