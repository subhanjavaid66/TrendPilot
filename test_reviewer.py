
from agent.reviewer import review_content

content = """
Artificial Intelligence is changing the world through innovation.

Generative AI and AI-powered automation are creating new opportunities.

#ArtificialIntelligence #Technology #Innovation
"""

try:

    result = review_content(
        content=content,
        topic="Artificial Intelligence",
        platform="Instagram",
        tone="Professional"
    )

    print("\n========== AI CONTENT REVIEW ==========")
    print(result)

except Exception as error:

    print("\nReviewer Error:", error)
