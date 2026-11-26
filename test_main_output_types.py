import unittest

from main import _extract_post_caption, _normalize_output_type
from run_tests import check_output_contract
from tools.content_analyzer import analyze_content


class TestOutputTypeNormalization(unittest.TestCase):
    def test_assignment_post_labels_map_to_post(self):
        for label in ("Post", "Post + hashtags", "Short post", "Portfolio post"):
            with self.subTest(label=label):
                self.assertEqual(_normalize_output_type(label), "Post")

    def test_assignment_script_labels_map_to_reel_script(self):
        for label in ("Reel script", "Video script"):
            with self.subTest(label=label):
                self.assertEqual(
                    _normalize_output_type(label),
                    "Reel Script",
                )

    def test_combined_post_and_reel_script_label(self):
        self.assertEqual(
            _normalize_output_type("Post + Reel Script"),
            "Post + Reel Script",
        )

    def test_rejects_unknown_output_type(self):
        with self.assertRaises(ValueError):
            _normalize_output_type("Carousel")

    def test_output_contract_requires_script_for_script_mode(self):
        issues = check_output_contract(
            {
                "output_type": "Video script",
                "content": "Caption",
                "reel_script": None,
                "saved_file": __file__,
            }
        )

        self.assertIn(
            "Expected a reel script, but none was generated.",
            issues,
        )


class TestPostCaptionExtraction(unittest.TestCase):
    def test_analysis_excludes_script_and_keeps_its_appended_hashtags(self):
        post = (
            "YOLOv8 helmet detection project applies computer vision to "
            "identify helmets in video frames. In a construction site pilot, "
            "the model can flag missed detections for human review, helping "
            "teams assess their safety workflows without replacing on-site "
            "judgment. Lighting, camera angles, and occlusion still affect "
            "reliability, so teams should validate performance on "
            "representative footage before deployment. What safeguards "
            "would you prioritize?"
        )
        script = " ".join(["Scene with camera and helmet detection."] * 60)
        combined = (
            f"**Post:**\n{post}\n\n**Reel Script:**\n{script}\n\n"
            "#YOLOv8 #HelmetSafety #ObjectDetection"
        )

        caption = _extract_post_caption(combined)
        analysis = analyze_content(
            caption,
            topic="YOLOv8 helmet detection project",
            platform="LinkedIn",
        )

        self.assertNotIn("Scene with camera", caption)
        self.assertIn("#YOLOv8", caption)
        self.assertGreaterEqual(analysis["word_count"], 50)
        self.assertLessEqual(analysis["word_count"], 250)
        self.assertEqual(analysis["checks"]["length"], 20)


if __name__ == "__main__":
    unittest.main()
