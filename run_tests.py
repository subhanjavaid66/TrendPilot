"""
Runs the assignment's 10 test cases through TrendPilot and writes tests/test_cases.md.

Usage (from the project root, Ollama running):
    python run_tests.py            # run all 10 cases
    python run_tests.py 3 7        # run only cases 3 and 7

Each run saves its own report in outputs/generated_posts/, so 10 runs give you
10 saved outputs (the assignment needs at least 5).
"""
import io
import json
import os
import re
import sys
import time
import traceback
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

# Test runs use at most 1 rewrite per case to keep total time down
os.environ.setdefault("TRENDPILOT_MAX_REVISIONS", "1")

from main import _normalize_output_type, run_trendpilot

TESTS_DIR = Path(os.environ.get("TRENDPILOT_TESTS_DIR", Path(__file__).parent / "tests"))

# (no, topic, platform, tone, output type) -- taken from the assignment table
TEST_CASES = [
    (1, "YOLOv8 helmet detection", "LinkedIn", "Professional", "Post + hashtags"),
    (2, "AI internship experience", "LinkedIn", "Motivational", "Post"),
    (3, "Python learning journey", "Instagram", "Funny", "Reel script"),
    (4, "Machine learning project", "X (Twitter)", "Short and catchy", "Short post"),
    (5, "Data annotation struggles", "LinkedIn", "Humorous", "Post"),
    (6, "Model failed in production", "Instagram", "Meme style", "Reel script"),
    (7, "Final year project", "LinkedIn", "Professional", "Portfolio post"),
    (8, "Computer vision project", "YouTube Shorts", "Exciting", "Video script"),
    (9, "Debugging FastAPI", "X (Twitter)", "Funny", "Short post"),
    (10, "Open-source contribution", "LinkedIn", "Inspirational", "Post"),
]


class Tee(io.StringIO):
    """Show output live while also capturing it, so tool calls can be recorded."""

    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def write(self, text):
        self.stream.write(text)
        return super().write(text)


def judge(status, score):
    """Automatic first judgement. Read the outputs and correct it by hand if you disagree."""
    if status == "APPROVED":
        return "Yes"
    if score is not None and score >= 75:
        return "Partial"
    return "No"


def check_output_contract(result):
    """Verify that the selected output mode produced and saved its outputs."""
    issues = []
    output_type = _normalize_output_type(result.get("output_type"))

    if output_type in ("Post", "Post + Reel Script"):
        content = result.get("content")
        if not isinstance(content, str) or not content.strip():
            issues.append("Expected a post caption, but none was generated.")

    if output_type in ("Reel Script", "Post + Reel Script"):
        reel_script = result.get("reel_script")
        if not isinstance(reel_script, str) or not reel_script.strip():
            issues.append("Expected a reel script, but none was generated.")

    saved_file = result.get("saved_file")
    if not saved_file or not Path(saved_file).is_file():
        issues.append("The main result file was not saved.")

    return issues


def run_case(case):
    no, topic, platform, tone, output_type = case
    print(f"\n{'#' * 60}\nTEST {no}: {topic} | {platform} | {tone} | {output_type}\n{'#' * 60}")

    tee = Tee(sys.__stdout__)
    started = time.time()
    record = {
        "no": no, "topic": topic, "platform": platform, "tone": tone,
        "output_type": output_type,
        "prompt": f"Topic: {topic} | Platform: {platform} | Tone: {tone} | Output: {output_type}",
    }

    try:
        with redirect_stdout(tee):
            result = run_trendpilot(topic, platform, tone, output_type)

        tools = list(dict.fromkeys(re.findall(r"\[Tool Called\]: (.+)", tee.getvalue())))
        status_match = re.search(r"Status: (APPROVED|NEEDS IMPROVEMENT)", result["review"])
        status = status_match.group(1) if status_match else "UNKNOWN"
        score = result["analysis"]["quality_score"]
        contract_issues = check_output_contract(result)
        useful = judge(status, score)
        if contract_issues:
            useful = "No"

        record.update({
            "tools_used": tools,
            "status": status,
            "score": score,
            "output_contract_passed": not contract_issues,
            "output_contract_issues": contract_issues,
            "revisions": result.get("revisions", 0),
            "useful": useful,
            "saved_file": str(result.get("saved_file", "")),
            "content_idea": result.get("content_idea", ""),
            "hook": result.get("hook", ""),
            "caption": result.get("content", ""),
            "reel_script": result.get("reel_script", ""),
            "title": result.get("title", ""),
            "thumbnail_text": result.get("thumbnail_text", ""),
            "review": result.get("review", ""),
            "error": None,
        })
    except Exception as error:
        traceback.print_exc()
        record.update({
            "tools_used": list(dict.fromkeys(re.findall(r"\[Tool Called\]: (.+)", tee.getvalue()))),
            "status": "ERROR", "score": None, "revisions": 0, "useful": "No",
            "output_contract_passed": False,
            "output_contract_issues": ["TrendPilot generation failed."],
            "saved_file": "", "error": f"{type(error).__name__}: {error}",
        })

    record["seconds"] = round(time.time() - started)
    return record


def build_report(records):
    lines = [
        "# TrendPilot Test Cases",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"Model: {os.getenv('OLLAMA_MODEL', 'gemma3:4b')}  ",
        f"Cases run: {len(records)}",
        "",
        "> The *Useful?* column is an automatic first judgement (Yes = approved, "
        "Partial = score 75+ but not approved, No = low score or error). "
        "Read each output below and correct it by hand where you disagree.",
        "",
        "## Summary",
        "",
        "| No. | Topic | Platform | Tone | Output | Score | Status | Contract | Revisions | Useful? |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        score = "-" if r["score"] is None else f"{r['score']}/100"
        lines.append(
            f"| {r['no']} | {r['topic']} | {r['platform']} | {r['tone']} | {r['output_type']} "
            f"| {score} | {r['status']} | "
            f"{'Pass' if r.get('output_contract_passed') else 'FAIL'} "
            f"| {r['revisions']} | {r['useful']} |"
        )

    lines += ["", "## Test Details", ""]
    for r in sorted(records, key=lambda x: x["no"]):
        lines += [
            f"### Test {r['no']}: {r['topic']}",
            "",
            f"- **Input prompt:** {r['prompt']}",
            f"- **Tools used:** {', '.join(r['tools_used']) or 'none recorded'}",
            f"- **Saved file path:** {r['saved_file'] or 'not saved'}",
            f"- **Score / status:** {r['score']} / {r['status']} (revisions: {r['revisions']}, {r['seconds']}s)",
            f"- **Useful?:** {r['useful']}",
        ]
        if r.get("output_contract_issues"):
            lines.append(
                f"- **Output contract issues:** "
                f"{'; '.join(r['output_contract_issues'])}"
            )
        if r["error"]:
            lines += [f"- **Error:** `{r['error']}`", ""]
            continue
        lines += [
            f"- **Content idea:** {r['content_idea']}",
            f"- **Hook:** {r['hook']}",
            f"- **Title / thumbnail:** {r['title']} / {r['thumbnail_text']}",
            "",
            "**Final caption:**",
            "",
            "```",
            r["caption"],
            "```",
            "",
            "**Reel / video script:**",
            "",
            "```",
            r["reel_script"],
            "```",
            "",
            "**Review:**",
            "",
            "```",
            r["review"],
            "```",
            "",
        ]

    weak = [
        r for r in records
        if (
            r["status"] != "APPROVED"
            or r["revisions"] > 0
            or not r.get("output_contract_passed", False)
        )
    ]
    lines += [
        "## Candidates for the Error Analysis Table",
        "",
        "See [error_analysis.md](error_analysis.md) for five evidence-based examples "
        "from earlier saved runs and the corrective changes.",
        "",
        "| Test | What happened | Possible reason | Fix applied |",
        "|---|---|---|---|",
    ]
    for r in sorted(weak, key=lambda x: x["no"]):
        if r["error"]:
            what = f"Crashed: {r['error']}"
        else:
            what = f"{r['status']} with score {r['score']}, {r['revisions']} revision(s)"
        lines.append(
            f"| {r['no']}. {r['topic']} | {what} | "
            "See `error_analysis.md` for root cause and fix. |"
        )
    if not weak:
        lines.append("| - | All cases approved on the first attempt. Look for weak content by reading the outputs. | | |")

    return "\n".join(lines) + "\n"



def main():
    wanted = {int(a) for a in sys.argv[1:] if a.isdigit()}
    cases = [c for c in TEST_CASES if not wanted or c[0] in wanted]

    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = TESTS_DIR / "test_cases.md"
    json_path = TESTS_DIR / "test_results.json"

    # Load previously saved results
    by_no = {}

    if json_path.exists():
        try:
            by_no = {
                r["no"]: r
                for r in json.loads(
                    json_path.read_text(encoding="utf-8")
                )
            }
        except (ValueError, KeyError):
            by_no = {}

    # Track only the cases executed in this run
    current_records = []

    for case in cases:
        result = run_case(case)

        by_no[case[0]] = result
        current_records.append(result)

        records = sorted(
            by_no.values(),
            key=lambda r: r["no"]
        )

        # Save after every completed case
        report_path.write_text(
            build_report(records),
            encoding="utf-8"
        )

        json_path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # Current run summary
    current_ok = sum(
        1 for r in current_records
        if r["status"] == "APPROVED"
    )

    # Overall saved results summary
    records = sorted(
        by_no.values(),
        key=lambda r: r["no"]
    )

    overall_ok = sum(
        1 for r in records
        if r["status"] == "APPROVED"
    )

    print("\n========== TEST SUMMARY ==========")

    print(
        f"Current run: {len(current_records)} cases, "
        f"{current_ok} approved."
    )

    print(
        f"Overall saved results: {len(records)} cases, "
        f"{overall_ok} approved."
    )

    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
