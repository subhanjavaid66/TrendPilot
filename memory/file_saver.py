import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


def _slug(text, limit=40):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:limit] or "output"


def save_output(result):
    """
    Save the result as:
      outputs/generated_posts/<name>.md      full readable report
      outputs/generated_scripts/<name>.md    reel script only
      outputs/saved_results/<name>.json      raw data
    Returns the path of the main report as a string.
    """
    posts_dir = OUTPUT_DIR / "generated_posts"
    scripts_dir = OUTPUT_DIR / "generated_scripts"
    results_dir = OUTPUT_DIR / "saved_results"
    for folder in (posts_dir, scripts_dir, results_dir):
        folder.mkdir(parents=True, exist_ok=True)

    plan = result.get("plan", {})
    topic = result.get("topic") or plan.get("topic", "untitled")
    platform = result.get("platform") or plan.get("platform", "")
    tone = result.get("tone") or plan.get("tone", "")

    now = datetime.now()
    name = f"{_slug(topic)}_{_slug(platform, 15)}_{now.strftime('%Y%m%d_%H%M%S')}"

    analysis = result.get("analysis", {})
    checks = analysis.get("checks", {})
    checks_text = "\n".join(f"- {k.replace('_', ' ').title()}: {v}" for k, v in checks.items())
    angles = result.get("research", {}).get("angles") or result.get("research", {}).get("trends", [])
    angles_text = "\n".join(f"{i}. {a}" for i, a in enumerate(angles, 1))
    hashtags = " ".join(result.get("hashtags", {}).get("hashtags", []))

    report = f"""# TrendPilot Report

**Topic:** {topic}
**Platform:** {platform}
**Tone:** {tone}
**Generated:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**Revisions made by agent:** {result.get("revisions", 0)}

## Content Idea
{result.get("content_idea", "")}

## Hook
{result.get("hook", "")}

## Caption
{result.get("content", "")}

## Hashtags
{hashtags}

## Reel Script
{result.get("reel_script", "Not generated.")}

## Title and Thumbnail
- **Title:** {result.get("title", "")}
- **Thumbnail text:** {result.get("thumbnail_text", "")}

## Content Angles Considered
{angles_text}

## Content Analysis
- **Quality score:** {analysis.get("quality_score", "N/A")}/100
- **Word count:** {analysis.get("word_count", "N/A")}
- **Hashtag count:** {analysis.get("hashtag_count", "N/A")}
{checks_text}

## AI Review
{result.get("review", "")}
"""

    report_path = posts_dir / f"{name}.md"
    report_path.write_text(report, encoding="utf-8")

    if result.get("reel_script"):
        script_text = f"# Reel Script: {topic} ({platform})\n\n{result['reel_script']}\n"
        (scripts_dir / f"{name}_reel.md").write_text(script_text, encoding="utf-8")

    (results_dir / f"{name}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )

    return str(report_path)