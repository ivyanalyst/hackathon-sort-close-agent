"""
Close agent: decides which open items (simulated tabs/docs) are safe to close.
Reads data/open_items.json. Does NOT touch any real browser/files — this is
a simulated decision-making pass.

Rules (from TAXONOMY_SPEC.md):
- status "done"        -> safe to close
- status "in_progress" -> must NOT close
- status "unclear" / task null -> needs human confirmation, never auto-close
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash-lite"

OPEN_ITEMS_FILE = Path("data/open_items.json")
RESULT_LOG = Path("trajectories/close_agent_run.json")

SUMMARY_PROMPT = """A user has an open tab/document that couldn't be confidently assigned to a task. Write ONE short, human-readable sentence (max 20 words) summarizing the situation for the user, so they can quickly decide whether to close it or not.

Title: {title}
Type: {type}

Respond with ONLY the one sentence, no quotes, no preamble."""


def generate_human_summary(item: dict) -> str:
    prompt = SUMMARY_PROMPT.format(title=item.get("title"), type=item.get("type"))
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"(Could not generate summary — {str(e)[:80]})"


def load_open_items():
    with open(OPEN_ITEMS_FILE) as f:
        return json.load(f)


def decide(item: dict) -> dict:
    """Return a decision dict for one open item, with reasoning."""
    status = item.get("status")
    task = item.get("task")
    human_summary = None

    if task is None or status == "unclear":
        decision = "NEEDS_CONFIRMATION"
        reasoning = "Task is unclear or unassigned — flagging for human review rather than guessing."
        human_summary = generate_human_summary(item)
    elif status == "done":
        decision = "CLOSE"
        reasoning = f"Task '{task}' is marked done — safe to close."
    elif status == "in_progress":
        decision = "KEEP_OPEN"
        reasoning = f"Task '{task}' is still in progress — must not close."
    else:
        decision = "NEEDS_CONFIRMATION"
        reasoning = f"Unrecognized status '{status}' — flagging for human review."

    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "task": task,
        "status": status,
        "decision": decision,
        "reasoning": reasoning,
        "human_summary": human_summary if decision == "NEEDS_CONFIRMATION" else None
    }


def close_agent():
    items = load_open_items()
    print(f"Evaluating {len(items)} open items.\n")

    results = []
    for item in items:
        result = decide(item)
        results.append(result)
        print(f"  [{result['decision']:20s}] {result['title']:40s} — {result['reasoning']}")
        if result.get("human_summary"):
            print(f"      Summary for user: {result['human_summary']}")

    close_count = sum(1 for r in results if r["decision"] == "CLOSE")
    keep_count = sum(1 for r in results if r["decision"] == "KEEP_OPEN")
    confirm_count = sum(1 for r in results if r["decision"] == "NEEDS_CONFIRMATION")

    print(f"\nSummary: {close_count} to close, {keep_count} to keep open, {confirm_count} need human confirmation.")

    RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULT_LOG, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {RESULT_LOG}")
    return results


if __name__ == "__main__":
    close_agent()
