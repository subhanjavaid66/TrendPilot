
from memory.file_saver import save_output

sample_result = {
    "plan": {
        "topic": "Artificial Intelligence"
    },
    "content": "AI is transforming the future.",
    "research": {
        "trends": [
            "Generative AI",
            "AI Automation",
            "Responsible AI"
        ]
    },
    "hashtags": {
        "hashtags": [
            "#AI",
            "#Technology",
            "#Innovation"
        ]
    },
    "analysis": {
        "quality_score": 90
    },
    "review": "Good content."
}

saved_path = save_output(sample_result)

print("\n========== FILE SAVING TEST ==========")
print("Report saved successfully!")
print("File location:", saved_path)
