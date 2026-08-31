"""
Close agent: decides which open items (simulated tabs/docs) are safe to close.
Reads data/open_items.json. Does NOT touch any real browser/files — this is
a simulated decision-making pass.

Rules (from TAXONOMY_SPEC.md):
- status "done"        -> safe to close
- status "in_progress" -> must NOT close
- status "unclear" / task null -> needs human confirmation, never auto-close
"""

import json
from pathlib import Path

OPEN_ITEMS_FILE = Path("data/open_items.json")
RESULT_LOG = Path("trajectories/close_agent_run.json")


def load_open_items():
    with open(OPEN_ITEMS_FILE) as f:
        return json.load(f)


def decide(item: dict) -> dict:
    """Return a decision dict for one open item, with reasoning."""
    status = item.get("status")
    task = item.get("task")

    if task is None or status == "unclear":
        decision = "NEEDS_CONFIRMATION"
        reasoning = "Task is unclear or unassigned — flagging for human review rather than guessing."
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
        "reasoning": reasoning
    }


def close_agent():
    items = load_open_items()
    print(f"Evaluating {len(items)} open items.\n")

    results = []
    for item in items:
        result = decide(item)
        results.append(result)
        print(f"  [{result['decision']:20s}] {result['title']:40s} — {result['reasoning']}")

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
