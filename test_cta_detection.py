
from tools.content_analyzer import CTA_PATTERN


test_cases = [
    "What questions should we be asking to transform education?",
    "What do you think about Artificial Intelligence?",
    "How can we improve education using AI?",
    "Do you agree with this approach?",
    "Share your thoughts in the comments.",
    "Follow us for more updates.",
    "Artificial Intelligence is changing education.",
]


print("\n========== CTA DETECTION TEST ==========\n")

for text in test_cases:

    result = bool(CTA_PATTERN.search(text))

    print(f"Text: {text}")
    print(f"CTA Detected: {result}")
    print("-" * 60)
