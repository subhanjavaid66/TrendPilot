
import re

from agent.ollama_client import generate_response


PLACEHOLDER_PATTERN = re.compile(
    r"\[[^\]]{1,100}\]"
    r"|<[^>]{1,100}>"
    r"|\b(?:insert|add|mention|replace with)"
    r"\s+(?:your|a|the)\s+(?:example|topic|text|name|concept)\b",
    re.IGNORECASE,
)

PERSONAL_EXPERIENCE_PATTERN = re.compile(
    r"\b(?:"
    r"I remember (?:struggling|facing|having|learning)"
    r"|I struggled"
    r"|I faced"
    r"|I experienced"
    r"|I overcame"
    r"|in my experience"
    r"|my personal experience"
    r"|for me,? (?:it was|the hardest|the biggest)"
    r")\b",
    re.IGNORECASE,
)


def _validate_script(script):
    """Check the generated script for common content problems."""

    errors = []

    if PLACEHOLDER_PATTERN.search(script):
        errors.append(
            "The script contains unfinished placeholders. "
            "Write complete sentences instead."
        )

    if PERSONAL_EXPERIENCE_PATTERN.search(script):
        errors.append(
            "The script invents a first-person personal experience. "
            "Use a general example instead."
        )

    # Count spoken words from the hook, voiceovers and closing line.
    spoken_parts = []

    for line in script.splitlines():
        line = line.strip()

        if line.startswith("Hook"):
            spoken_parts.append(line.split(":", 1)[-1])

        elif "Voiceover:" in line:
            spoken_parts.append(line.split("Voiceover:", 1)[-1])

        elif line.startswith("Closing line"):
            spoken_parts.append(line.split(":", 1)[-1])

    spoken_text = " ".join(spoken_parts)

    spoken_words = re.findall(r"\b[\w'-]+\b", spoken_text)

    if len(spoken_words) > 100:
        errors.append(
            f"The script contains {len(spoken_words)} spoken words. "
            "Keep the total at or below 100 words."
        )

    return errors


def generate_reel_script(
    topic,
    platform,
    tone,
    angle=None,
    caption=None,
):
    """
    Generate a 30-45 second reel script.

    If a caption is supplied, use it as context so the video
    script follows the same central idea and examples.
    """

    if not topic or not str(topic).strip():
        raise ValueError("Topic cannot be empty.")

    angle = angle or topic

    caption_context = ""

    if caption:
        caption_context = f"""
REFERENCE CAPTION:
{caption}

IMPORTANT CONSISTENCY REQUIREMENTS:
- The video script must communicate the same central idea as the caption.
- Use the same main example, concept or situation.
- Do not introduce a different coding concept or unrelated example.
- The script should complement the caption rather than repeat it word for word.
- Keep the message and tone consistent with the caption.
"""

    prompt = f"""
You are TrendPilot's short-video script generator.

Create a professional 30-45 second short-video script.

CONTENT DETAILS:
Topic: {topic}
Platform: {platform}
Selected angle: {angle}
Tone: {tone}

{caption_context}

SCRIPT FORMAT:

Hook (0-3s): One punchy opening line.

Scene 1 | Visual: Describe what is shown.
| Voiceover: "Write the spoken line."

Scene 2 | Visual: Describe what is shown.
| Voiceover: "Write the spoken line."

Scene 3 | Visual: Describe what is shown.
| Voiceover: "Write the spoken line."

Closing line: One memorable call to action.

CONTENT RULES:

1. Keep the complete spoken content under 100 words.
2. Make the script suitable for a 30-45 second video.
3. Use natural, conversational language.
4. Keep the requested tone consistent.
5. Make every scene relevant to the selected angle.
6. Do not invent statistics or unsupported facts.
7. Do not invent personal experiences or first-person stories.
8. Do not invent specific names, brands or product models.
9. Do not include hashtags.
10. Do not include unfinished placeholders or editing instructions.
11. Ensure the hook, scenes and closing line communicate one consistent idea.
12. Use complete sentences with correct grammar and spacing.

Return only the script in the specified format.
Do not include an introduction or explanation.
"""

    # Generate and validate, with one retry if needed.
    script = None
    validation_errors = []

    for attempt in range(2):

        current_prompt = prompt

        if attempt == 1:
            current_prompt += f"""

YOUR PREVIOUS SCRIPT FAILED VALIDATION.

Correct these problems:
{chr(10).join("- " + error for error in validation_errors)}

Return the complete corrected script.
"""

        response = generate_response(
            current_prompt,
            temperature=0.5 if attempt > 0 else 0.7,
        )

        if not response or not response.strip():
            continue

        script = response.strip()

        validation_errors = _validate_script(script)

        if not validation_errors:
            break

    if not script or not script.strip():
        raise ValueError(
            "Reel script generation returned empty output."
        )

    if validation_errors:
        raise ValueError(
            "Reel script failed validation after retry: "
            + "; ".join(validation_errors)
        )

    return {"script": script}
