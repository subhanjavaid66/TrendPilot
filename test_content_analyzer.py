
from tools.content_analyzer import (
    _check_formatting,
    _check_topic_relevance,
    analyze_content,
)
import unittest


class TestHashtagRelevance(unittest.TestCase):
    def test_camel_case_topic_hashtags_are_relevant(self):
        result = analyze_content(
            content=(
                "Elon Musk's achievements include building companies "
                "that pursue ambitious engineering goals. His work at "
                "Tesla and SpaceX has influenced electric vehicles, "
                "spaceflight, and technology. Which achievement do you "
                "think has made the biggest difference?"
            ),
            topic="Elon Musk Achievements",
            hashtags=[
                "#ElonMuskAchievements",
                "#MuskAchievements",
                "#ElonMusk",
            ],
            platform="LinkedIn",
        )

        self.assertEqual(result["relevant_hashtag_count"], 3)
        self.assertEqual(result["checks"]["hashtags"], 15)

    def test_normal_words_and_hashtags_do_not_trigger_formatting_flags(self):
        result = analyze_content(
            content=(
                "Elon Musk's achievements influenced the industry, "
                "forcing companies to rethink technology. "
                "What do you think?"
                "\n#ElonMuskAchievements"
            ),
            topic="Elon Musk Achievements",
            platform="LinkedIn",
        )

        self.assertEqual(result["formatting_issues"], [])

    def test_detects_lowercase_word_joined_to_capitalized_word(self):
        issues = _check_formatting("Please discuss andThis topic.")

        self.assertIn(
            "Check for accidentally joined words.",
            issues,
        )

    def test_ai_education_without_in_alias_matches_related_content(self):
        score, suggestion = _check_topic_relevance(
            "AI Education",
            "Artificial intelligence can support classroom learning.",
        )

        self.assertEqual(score, 25)
        self.assertIsNone(suggestion)


class TestCallToAction(unittest.TestCase):
    def test_explore_imperative_is_recognized_as_a_call_to_action(self):
        result = analyze_content(
            content=(
                "Explore how YOLOv8 can support helmet detection. "
                "What safeguards would you prioritize?"
            ),
            topic="YOLOv8 helmet detection",
            platform="LinkedIn",
        )

        self.assertEqual(result["checks"]["call_to_action"], 10)


print("\n========== CONTENT ANALYZER TEST ==========")

# Test 1: Very short content
result1 = analyze_content(
    content="AI is transforming the future.",
    topic="Artificial Intelligence",
    hashtags=["#AI", "#Technology", "#Innovation"],
    platform="LinkedIn"
)

print("\nTEST 1: Short Content")
print("Word Count:", result1["word_count"])
print("Quality Score:", result1["quality_score"])
print("Suggestions:", result1["suggestions"])


# Test 2: Better quality content
result2 = analyze_content(
    content=(
        "Artificial Intelligence is transforming how businesses "
        "operate and how developers solve real-world problems. "
        "Generative AI tools are helping teams automate repetitive "
        "tasks, improve productivity, and explore new ideas. "
        "However, responsible AI development remains important "
        "for building trustworthy technology. "
        "How do you think AI will change your industry?"
    ),
    topic="Artificial Intelligence",
    hashtags=[
        "#ArtificialIntelligence",
        "#GenerativeAI",
        "#AIAutomation",
        "#MachineLearning"
    ],
    platform="LinkedIn"
)

print("\nTEST 2: Detailed Content")
print("Word Count:", result2["word_count"])
print("Quality Score:", result2["quality_score"])
print("Suggestions:", result2["suggestions"])


print("\n========== TEST COMPLETED ==========")
