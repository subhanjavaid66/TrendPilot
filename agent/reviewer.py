
import re

from agent.ollama_client import generate_response


PASS_SCORE = 75

BULLET = re.compile(r"^\s*[-•*]\s+(.*\S)\s*$")

HEADER = re.compile(
    r"^(STRENGTHS|ISSUES|SUGGESTIONS)\s*:?\s*$",
    re.IGNORECASE
)

STATUS = re.compile(
    r"^STATUS\s*:\s*(.+)$",
    re.IGNORECASE
)


def _parse(raw):
    """
    Parse the AI review response.
    """

    status = None

    sections = {
        "strengths": [],
        "issues": [],
        "suggestions": []
    }

    current = None

    if not isinstance(raw, str):
        return status, sections

    for line in raw.splitlines():

        line = line.strip()

        if not line:
            continue

        clean = re.sub(r"[*#`]", "", line).strip()

        status_match = STATUS.match(clean)

        if status_match:

            value = status_match.group(1).strip().upper()

            if value.startswith("APPROVED"):
                status = "APPROVED"

            elif value.startswith("NEEDS IMPROVEMENT"):
                status = "NEEDS IMPROVEMENT"

            continue

        header_match = HEADER.match(clean)

        if header_match:
            current = header_match.group(1).lower()
            continue

        bullet = BULLET.match(line)

        if bullet and current:

            item = re.sub(
                r"[*`]",
                "",
                bullet.group(1)
            ).strip()

            if item.lower() not in (
                "none",
                "none.",
                "n/a",
                "no issues"
            ):

                if item and item not in sections[current]:
                    sections[current].append(item)

    return status, sections


def _prepare_analysis_context(analysis):
    """
    Prepare analyzer findings for the AI reviewer.
    """

    if not isinstance(analysis, dict):
        return "Analyzer information is unavailable."

    lines = []

    if "quality_score" in analysis:
        lines.append(
            f"Analyzer score: {analysis['quality_score']}/100"
        )

    if "word_count" in analysis:
        lines.append(
            f"Word count: {analysis['word_count']}"
        )

    if "hashtag_count" in analysis:
        lines.append(
            f"Hashtag count: {analysis['hashtag_count']}"
        )

    checks = analysis.get("checks", {})
    max_scores = analysis.get("max_scores", {})

    if isinstance(checks, dict):

        lines.append("\nAnalyzer checks:")

        for name, value in checks.items():

            maximum = max_scores.get(name, "?")

            lines.append(
                f"- {name}: {value}/{maximum}"
            )

    suggestions = analysis.get("suggestions", [])

    if suggestions:

        lines.append("\nAnalyzer suggestions:")

        for suggestion in suggestions[:5]:
            lines.append(f"- {suggestion}")

    return "\n".join(lines) if lines else "No analyzer details available."


def review_content(content, topic, platform, tone, analysis=None):
    """
    Review social media content using AI and analyzer findings.

    Decision rules:

    - Below 75: Needs improvement.
    - 75 or above: AI reviewer makes the final quality decision.
    - High analyzer scores do not automatically guarantee approval.
    """

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content cannot be empty.")

    if not topic or not str(topic).strip():
        raise ValueError("Topic cannot be empty.")

    analysis_context = _prepare_analysis_context(analysis)

    prompt = f"""
You are TrendPilot's senior social media content quality reviewer.

Your job is to determine whether generated content is genuinely
ready to publish.

You must be objective, critical and fair.

==============================
CONTENT INFORMATION
==============================

Topic: {topic}

Platform: {platform}

Desired tone: {tone}

Generated content:

{content}

==============================
CONTENT ANALYZER RESULTS
==============================

{analysis_context}

IMPORTANT:
The analyzer score is supporting information, not proof of quality.

A high score does not automatically mean the content is good.

A low score does not mean every aspect of the content is bad.

Examine the actual caption independently.

==============================
EVALUATION CRITERIA
==============================

1. TOPIC RELEVANCE AND SPECIFICITY

- Does the caption actually discuss the requested topic?
- Does it contain meaningful topic-specific details?
- Does it avoid unrelated statements?
- Does it demonstrate an understanding of the subject?

2. INFORMATION VALUE

- Identify the caption's concrete takeaway. If none can be stated,
  treat that as an information-value problem.
- Does it explain a useful detail, example, mechanism, trade-off,
  implication or practical step specific to this topic?
- Does it explain why that detail matters to the intended audience?
- Separate substantive information from unsupported claims and
  generic praise. Never reward length or confident wording by itself.

3. HOOK QUALITY

- Does the opening attract attention?
- Is it specific to the topic?
- Does it create genuine curiosity?
- Does it avoid overused AI-style openings?

4. NATURAL WRITING

- Does it sound like a real human social media creator?
- Is the language natural for the requested tone?
- Does it avoid excessive dramatic expressions?
- Are there repetitive or awkward sentences?

5. PLATFORM SUITABILITY

- Is the caption appropriate for {platform}?
- Is the length reasonable?
- Is the structure easy to read?
- Does it follow the platform's communication style?

6. ENGAGEMENT

- Is the CTA relevant to the topic?
- Does the question encourage meaningful interaction?
- Does the ending feel natural?

7. ORIGINALITY

- Does the caption offer an interesting perspective?
- Does it avoid generic filler?
- Does it avoid repeating the same idea?

8. FACTUAL RESPONSIBILITY

- Identify clearly unsupported or potentially misleading claims.
- Do not invent factual problems.
- Do not claim to have verified facts without evidence.
- If source information is unavailable, distinguish
  uncertain claims from confirmed errors.

9. HASHTAG QUALITY

- Check that each hashtag accurately describes the topic or a clearly
  supported subtopic, and adds a distinct discovery path.
- Flag unrelated, overly broad, repetitive or misleading tags.
- Judge the set for relevance and specificity as well as platform fit;
  hashtag count alone is not evidence of quality.

==============================
REVIEW DECISION RULES
==============================

APPROVED:

Use APPROVED when the caption is genuinely ready to publish.

It does not need to be perfect.

Minor stylistic improvements should not prevent approval.

NEEDS IMPROVEMENT:

Use NEEDS IMPROVEMENT when there are meaningful problems such as:

- Weak or irrelevant content.
- Generic or repetitive writing.
- Insufficient information value.
- Serious tone mismatch.
- Misleading or unsupported factual claims.
- Poor readability.
- Unnatural or ineffective engagement.

Do not approve weak content simply because it has a high
analyzer score.

Do not reject good content just because you personally prefer
a different writing style.

==============================
REVIEW OUTPUT
==============================

Return exactly this format:

STATUS: APPROVED or NEEDS IMPROVEMENT

STRENGTHS:
- Maximum 3 specific strengths.

ISSUES:
- Maximum 3 genuine problems.

SUGGESTIONS:
- Maximum 3 actionable improvements.

If a section has no items, write:
- None

IMPORTANT:

- Be specific.
- Avoid vague feedback.
- Do not repeat the same issue in multiple sections.
- Do not suggest unnecessary rewriting.
- Only review the caption and hashtags.
- Do not suggest images, videos or animations.
"""

    status = None

    sections = {
        "strengths": [],
        "issues": [],
        "suggestions": []
    }

    # Ask the AI reviewer, with one retry if parsing fails.
    for attempt in range(2):

        raw = generate_response(
            prompt,
            temperature=0.2
        )

        if not isinstance(raw, str) or not raw.strip():
            continue

        parsed_status, parsed_sections = _parse(raw)

        if parsed_status:

            status = parsed_status
            sections = parsed_sections
            break

    review = {
        "status": status,
        **sections
    }

    score = None

    if isinstance(analysis, dict):
        score = analysis.get("quality_score")

    review["llm_verdict"] = status

    # Fallback when the AI reviewer cannot return
    # a valid review.
    if status is None:

        review["status"] = (
            "APPROVED"
            if score is not None and score >= 90
            else "NEEDS IMPROVEMENT"
        )

        review["issues"].append(
            "AI review could not be completed. "
            "Fallback decision used the analyzer score."
        )

    # Final decision.
    if score is not None:

        review["quality_score"] = score

        if score < PASS_SCORE:

            review["status"] = "NEEDS IMPROVEMENT"

        elif status is not None:

            # AI reviewer decides for scores of 75 and above.
            # Even a score of 90+ cannot override a genuine issue.
            review["status"] = status

        # Add analyzer suggestions without duplicates.
        if isinstance(analysis, dict):

            for tip in analysis.get("suggestions", []):

                if (
                    tip
                    and tip not in review["suggestions"]
                    and len(review["suggestions"]) < 5
                ):
                    review["suggestions"].append(tip)

    return review


def format_review(review):
    """
    Format review results for Streamlit and file saving.
    """

    lines = [
        f"Status: {review['status']}"
    ]

    if "quality_score" in review:

        lines.append(
            f"Rule-based quality score: "
            f"{review['quality_score']}/100"
        )

    if (
        review.get("llm_verdict")
        and review["llm_verdict"] != review["status"]
    ):

        lines.append(
            f"AI reviewer verdict: "
            f"{review['llm_verdict']} (advisory)"
        )

    for title, key in (
        ("Strengths", "strengths"),
        ("Issues", "issues"),
        ("Suggestions", "suggestions")
    ):

        if review.get(key):

            lines.append(f"\n{title}:")

            lines.extend(
                f"- {item}"
                for item in review[key]
            )

    return "\n".join(lines)
