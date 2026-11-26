def generate_title_thumbnail(topic, platform, tone, angle=None):
    """Create quick title and thumbnail suggestions without another model call."""
    angle = angle or topic
    title = str(angle).strip().rstrip(".!?")
    if len(title) > 67:
        title = title[:64].rsplit(" ", 1)[0].rstrip(" ,;:") + "..."

    thumbnail = " ".join(str(topic).split()[:4]).upper()

    return {
        "title": title or str(topic)[:70],
        "thumbnail_text": thumbnail[:25],
    }
