"""
Generates a human-readable trajectory writeup from the raw JSON logs,
highlighting representative cases: a normal classification, both
ambiguous cases, and both adversarial test cases.
"""

import json
from pathlib import Path

SORT_LOG = Path("trajectories/sort_agent_run.json")
CLOSE_LOG = Path("trajectories/close_agent_run.json")
OUTPUT = Path("trajectories/AGENT_LOGS.md")

HIGHLIGHT_FILES = [
    "Client_A_Proposal_Draft.docx",   # normal, clear-cut case
    "Notes.docx",                     # ambiguous case 1
    "Meeting_Summary.pdf",            # ambiguous case 2
    "Proposal_Feedback.docx",         # adversarial: misleading filename
    "Demo_Prep_Notes.docx",           # adversarial: genuine task overlap
]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def generate():
    sort_log = load_json(SORT_LOG)
    close_log = load_json(CLOSE_LOG)

    sort_by_file = {entry["file"]: entry for entry in sort_log if "file" in entry}

    lines = []
    lines.append("# Agent Trajectory Writeup\n")
    lines.append("This document walks through representative examples of the sort agent's ")
    lines.append("reasoning, covering a normal case, both intentionally ambiguous test cases, ")
    lines.append("and both adversarial test cases. Full raw logs for all 22 files are in ")
    lines.append("`sort_agent_run.json` and `close_agent_run.json` in this same folder.\n")

    lines.append("## Sort Agent — Instructions Given\n")
    lines.append("Every file is classified using the same prompt template: the filename, ")
    lines.append("the first 300 characters of file content, and the file's creation date are ")
    lines.append("provided, along with the fixed list of 4 valid task names. The model is told ")
    lines.append("to return `task: null` rather than guess if it isn't confident. See ")
    lines.append("`agent/sort_agent.py` (PROMPT_TEMPLATE) for the exact wording.\n")

    lines.append("## Representative Cases\n")

    for filename in HIGHLIGHT_FILES:
        entry = sort_by_file.get(filename)
        if not entry:
            continue

        lines.append(f"### `{filename}`")
        lines.append(f"- **Model output:** task = `{entry.get('task')}`, confidence = `{entry.get('confidence')}`")
        lines.append(f"- **Reasoning given:** {entry.get('reasoning')}")
        lines.append(f"- **Destination:** `{entry.get('destination')}`")
        if entry.get("model_used"):
            lines.append(f"- **Model used:** `{entry.get('model_used')}`")
        lines.append("")

    lines.append("## Close Agent — Full Run\n")
    lines.append("Unlike the sort agent, the close agent uses rule-based logic for standard ")
    lines.append("decisions (deterministic, based on task status) and only calls the LLM for ")
    lines.append("the 2 ambiguous items, to generate a human-readable summary for the user.\n")

    for entry in close_log:
        lines.append(f"### `{entry.get('title')}`")
        lines.append(f"- **Decision:** {entry.get('decision')}")
        lines.append(f"- **Reasoning:** {entry.get('reasoning')}")
        if entry.get("human_summary"):
            lines.append(f"- **Generated summary for user:** {entry.get('human_summary')}")
        lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"Trajectory writeup saved to {OUTPUT}")


if __name__ == "__main__":
    generate()
