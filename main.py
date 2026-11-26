
import os
import re

from agent.planner import create_plan
from agent.executor import execute_plan
from agent.generator import generate_content
from agent.reviewer import review_content, format_review

from tools.trend_research import research_trends
from tools.hashtag_tool import generate_hashtags
from tools.reel_script import generate_reel_script
from tools.title_thumbnail import generate_title_thumbnail

from memory.history import save_history
from memory.file_saver import save_output

# Max rewrites after the first draft
# One draft and one review are the fast default. Set this above 0 when
# additional model-driven rewrite rounds are preferred over response time.
MAX_REVISIONS = max(0, int(os.getenv("TRENDPILOT_MAX_REVISIONS", "0")))


def _normalize_output_type(output_type):
    """Map assignment and UI labels to the supported generation modes."""
    if not isinstance(output_type, str) or not output_type.strip():
        raise ValueError("Output type cannot be empty.")

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        output_type.lower(),
    ).strip()

    if "reel script" in normalized or "video script" in normalized:
        if "post" in normalized:
            return "Post + Reel Script"
        return "Reel Script"

    if "post" in normalized or "caption" in normalized:
        return "Post"

    raise ValueError(
        f"Unsupported output type: {output_type}. "
        "Choose Post, Post + Reel Script, or Reel Script."
    )


def _extract_post_caption(content):
    """Keep the post section for scoring when a draft also contains a script."""
    post_heading = re.search(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*{1,2}[ \t]*)?"
        r"(?:post(?:[ \t]+caption)?|caption)[ \t]*:?[ \t]*"
        r"(?:\*{1,2})?[ \t]*$",
        content,
    )
    script_heading = re.search(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*{1,2}[ \t]*)?"
        r"(?:reel|video)[ \t]+script[ \t]*:?[ \t]*"
        r"(?:\*{1,2})?[ \t]*$",
        content,
    )

    start = post_heading.end() if post_heading else 0
    end = (
        script_heading.start()
        if script_heading and script_heading.start() >= start
        else len(content)
    )
    caption = content[start:end].strip()

    hashtags = re.findall(r"(?<!\w)#[A-Za-z0-9_]+", content)
    existing_hashtags = {
        hashtag.lower()
        for hashtag in re.findall(r"(?<!\w)#[A-Za-z0-9_]+", caption)
    }
    missing_hashtags = [
        hashtag
        for hashtag in hashtags
        if hashtag.lower() not in existing_hashtags
    ]

    if missing_hashtags:
        caption = f"{caption}\n\n{' '.join(missing_hashtags)}".strip()

    return caption


def run_trendpilot(topic, platform, tone, output_type):
    output_type = _normalize_output_type(output_type)

    print("\n========== TRENDPILOT STARTED ==========")

    # 1. Plan
    print("\n[1] Creating execution plan...")
    plan = create_plan(
        topic=topic,
        platform=platform,
        tone=tone,
        output_type=output_type
    )

    for i, step in enumerate(plan["steps"], 1):
        print(f"   Step {i}: {step['tool']} - {step['purpose']}")

    # 2. Research + Hashtags
    print("\n[2] Running research and hashtag tools...")

    print("[Tool Called]: Trend Idea Generator")
    research = research_trends(topic, platform, tone)

    print("[Tool Called]: Hashtag Generator")
    hashtag_results = generate_hashtags(
        topic=topic,
        trends=research["trends"],
        platform=platform
    )
    hashtags = hashtag_results["hashtags"]

    analysis_plan = {
        "topic": topic,
        "steps": [
            s for s in plan["steps"]
            if s["tool"] == "content_analyzer"
        ],
    }

    if not analysis_plan["steps"]:
        raise ValueError("Execution plan does not contain content_analyzer.")

    # 3. Generate -> Analyze -> Review -> Revise
    content, analysis, review = None, None, None
    best = None
    revisions = 0

    for attempt in range(MAX_REVISIONS + 1):

        label = "Generating" if attempt == 0 else f"Revising (attempt {attempt})"
        print(f"\n[3] {label} content...")

        print("[Tool Called]: Caption Writer")

        feedback = None

        if review:
            feedback = "\n".join(
                f"- {x}" for x in (review["issues"] + review["suggestions"])
            )

        content = generate_content(
            topic=topic,
            platform=platform,
            tone=tone,
            output_type=output_type,
            trends=research["trends"],
            hashtags=hashtags,
            best_angle=research["best_angle"],
            feedback=feedback,
            previous_draft=content if review else None,
        )

        if output_type in ("Post", "Post + Reel Script"):
            content = _extract_post_caption(content)

        analysis = execute_plan(
            analysis_plan,
            generated_content=content,
            platform=platform
        )["content_analyzer"]

        print("[Tool Called]: Content Reviewer")

        review = review_content(
            content,
            topic,
            platform,
            tone,
            analysis=analysis
        )

        print(
            f"   Verdict: {review['status']} "
            f"(score {analysis['quality_score']}/100)"
        )

        if (
            best is None
            or review["status"] == "APPROVED"
            or analysis["quality_score"] > best["analysis"]["quality_score"]
        ):
            best = {
                "content": content,
                "analysis": analysis,
                "review": review
            }

        revisions = attempt

        if review["status"] == "APPROVED":
            break

    # Keep the best-scoring draft
    content = best["content"]
    analysis = best["analysis"]
    review = best["review"]

    # 4. Extra outputs (CONDITIONAL)
    reel_script = None
    title_data = {
        "title": None,
        "thumbnail_text": None
    }

    if output_type in ["Post + Reel Script", "Reel Script"]:

        print("\n[4] Generating reel script...")

        print("[Tool Called]: Reel Script Generator")

        reel_result = generate_reel_script(
            topic=topic,
            platform=platform,
            tone=tone,
            angle=research["best_angle"],
            caption=content,
        )

        reel_script = reel_result["script"]

    if output_type in ["Post", "Post + Reel Script"]:

        print("\n[5] Generating title and thumbnail...")

        print("[Tool Called]: Title and Thumbnail Generator")

        title_data = generate_title_thumbnail(
            topic,
            platform,
            tone,
            research["best_angle"]
        )

    first_line = next(
        (line for line in content.splitlines() if line.strip()),
        ""
    )

    hook = re.split(r"(?<=[.!?])\s+", first_line.strip())[0]

    # 5. Prepare final results
    final_results = {
        "plan": plan,
        "topic": topic,
        "platform": platform,
        "tone": tone,
        "output_type": output_type,
        "content_idea": research["best_angle"],
        "hook": hook,
        "research": research,
        "hashtags": hashtag_results,
        "content": content,
        "reel_script": reel_script,
        "title": title_data["title"],
        "thumbnail_text": title_data["thumbnail_text"],
        "analysis": analysis,
        "review": format_review(review),
        "revisions": revisions,
    }

    # 6. Save
    print("\n[6] Saving results...")

    print("[Tool Called]: Memory Tool")
    save_history(final_results)

    print("[Tool Called]: File Saver")
    saved_file = save_output(final_results)

    final_results["saved_file"] = saved_file

    print("Saved file path:", saved_file)

    return final_results


def ask_choice(prompt, options):
    print(f"\n{prompt}")

    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        choice = input("Choose a number: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]

        print("Invalid choice, try again.")


if __name__ == "__main__":

    topic = input("Enter your topic: ").strip()

    platform = ask_choice(
        "Choose platform:",
        ["Instagram", "LinkedIn", "X (Twitter)", "Facebook", "YouTube Shorts", "TikTok"],
    )

    tone = ask_choice(
        "Choose tone:",
        ["Professional", "Funny", "Motivational", "Casual", "Exciting"],
    )

    output_type = ask_choice(
        "Choose output type:",
        ["Post", "Post + Reel Script", "Reel Script"],
    )

    results = run_trendpilot(topic, platform, tone, output_type)

    print("\n========== CONTENT IDEA ==========")
    print(results["content_idea"])

    print("\n========== HOOK ==========")
    print(results["hook"])

    if output_type in ["Post", "Post + Reel Script"]:
        print("\n========== CAPTION ==========")
        print(results["content"])

    if results["reel_script"]:
        print("\n========== REEL SCRIPT ==========")
        print(results["reel_script"])

    if results["title"]:
        print("\n========== TITLE / THUMBNAIL ==========")
        print("Title:", results["title"])
        print("Thumbnail text:", results["thumbnail_text"])

    print("\n========== ANALYSIS ==========")

    a = results["analysis"]

    print(
        f"Score: {a['quality_score']}/100 | "
        f"Words: {a['word_count']} | "
        f"Hashtags: {a['hashtag_count']}"
    )

    for name, value in a["checks"].items():
        print(f"  {name}: {value}/{a['max_scores'][name]}")

    print("\n========== REVIEW ==========")
    print(results["review"])

    print("\nSaved file:", results["saved_file"])
