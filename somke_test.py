"""
Quick check that every TrendPilot module works.
Run from the project root with Ollama running:  python smoke_test.py
"""
import re
import tempfile
from pathlib import Path

results = []


def check(name, fn):
    try:
        info = fn()
        print(f"PASS  {name}" + (f"  ->  {info}" if info else ""))
        results.append(True)
    except Exception as error:
        print(f"FAIL  {name}: {type(error).__name__}: {error}")
        results.append(False)


TOPIC, PLATFORM, TONE = "Travel Vlog", "Instagram", "Exciting"
SAMPLE = (
    "Planning a trip? Your next travel vlog can be smarter.\n\n"
    "AI itinerary tools help you plan faster. Which one would you try first? "
    "Share your thoughts in the comments.\n\n#TravelVlog #TravelTech #AItravel"
)
state = {}


def t_imports():
    import agent.planner, agent.generator, agent.reviewer, agent.executor  # noqa
    import tools.trend_research, tools.hashtag_tool, tools.content_analyzer  # noqa
    import tools.reel_script, tools.title_thumbnail, tools.json_utils  # noqa
    import memory.file_saver, memory.history  # noqa


def t_ollama():
    from agent.ollama_client import generate_response
    reply = generate_response("Reply with the single word OK.", temperature=0)
    assert reply, "empty reply"
    return reply[:30]


def t_json():
    from tools.json_utils import extract_json
    assert extract_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json("no json here") is None


def t_trends():
    from tools.trend_research import research_trends
    r = research_trends(TOPIC, PLATFORM, TONE)
    assert len(r["angles"]) >= 3, "fewer than 3 angles"
    assert r["best_angle"] in r["angles"]
    state["research"] = r
    return f"{len(r['angles'])} angles, source={r['source']}"


def t_hashtags():
    from tools.hashtag_tool import generate_hashtags
    r = generate_hashtags(TOPIC, state["research"]["trends"], PLATFORM)
    tags = r["hashtags"]
    assert len(tags) >= 3, "fewer than 3 hashtags"
    assert all(t.startswith("#") for t in tags)
    state["hashtags"] = tags
    return " ".join(tags)


def t_analyzer():
    from tools.content_analyzer import analyze_content
    r = analyze_content(SAMPLE, TOPIC, platform=PLATFORM)
    assert 0 <= r["quality_score"] <= 100
    state["analysis"] = r
    return f"score={r['quality_score']}, words={r['word_count']}"


def t_generator():
    from agent.generator import generate_content
    text = generate_content(
        TOPIC, PLATFORM, TONE, "Post",
        state["research"]["trends"], state["hashtags"],
        best_angle=state["research"]["best_angle"],
    )
    first = text.strip().splitlines()[0].lower()
    assert not re.match(r"(okay|sure|here)", first), f"preamble leaked: {first}"
    assert text.strip().endswith(state["hashtags"][-1]), "hashtags not appended"
    state["content"] = text
    return f"{len(text.split())} words"


def t_reviewer():
    from agent.reviewer import review_content
    r = review_content(state["content"], TOPIC, PLATFORM, TONE, analysis=state["analysis"])
    assert r["status"] in ("APPROVED", "NEEDS IMPROVEMENT")
    return r["status"]


def t_reel():
    from tools.reel_script import generate_reel_script
    r = generate_reel_script(TOPIC, PLATFORM, TONE, state["research"]["best_angle"])
    assert "scene" in r["script"].lower(), "no scenes in script"


def t_title():
    from tools.title_thumbnail import generate_title_thumbnail
    r = generate_title_thumbnail(TOPIC, PLATFORM, TONE)
    assert r["title"] and r["thumbnail_text"]
    return f"{r['title']} | {r['thumbnail_text']}"


def t_planner():
    from agent.planner import create_plan
    plan = create_plan(TOPIC, PLATFORM, TONE, "Post")
    assert [s["tool"] for s in plan["steps"]] == [
        "trend_research", "hashtag_tool", "content_analyzer"
    ]
    state["plan"] = plan


def t_saver():
    import memory.file_saver as fs
    fs.OUTPUT_DIR = Path(tempfile.mkdtemp())  # writes to a temp folder, not your outputs/
    result = {
        "plan": state["plan"], "topic": TOPIC, "platform": PLATFORM, "tone": TONE,
        "content": state["content"], "research": state["research"],
        "hashtags": {"hashtags": state["hashtags"]}, "analysis": state["analysis"],
        "review": "Status: APPROVED", "reel_script": "Scene 1", "hook": "Hook",
    }
    path = Path(fs.save_output(result))
    assert path.exists() and path.suffix == ".md"
    return path.name


for name, fn in [
    ("imports", t_imports),
    ("ollama connection", t_ollama),
    ("json_utils", t_json),
    ("trend_research", t_trends),
    ("hashtag_tool", t_hashtags),
    ("content_analyzer", t_analyzer),
    ("generator", t_generator),
    ("reviewer", t_reviewer),
    ("reel_script", t_reel),
    ("title_thumbnail", t_title),
    ("planner", t_planner),
    ("file_saver", t_saver),
]:
    check(name, fn)

print(f"\n{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)