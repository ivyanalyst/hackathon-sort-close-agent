"""
Evaluates baseline vs. agent sorting against ground truth.
Baseline has no concept of "task" at all, so it's scored differently:
we check if it's even possible to find the file without opening every folder.
Agent is scored on exact task-match accuracy, including correct handling
of the 2 ambiguous (null) ground-truth cases.
"""

import json
from pathlib import Path

GROUND_TRUTH = Path("data/ground_truth.json")
AGENT_DIR = Path("data/Sorted_Agent")
BASELINE_DIR = Path("data/Sorted_Baseline")


def load_ground_truth():
    with open(GROUND_TRUTH) as f:
        return json.load(f)


def find_file_task_agent(filename: str) -> str | None:
    """Return the task-folder a file landed in under Sorted_Agent, or None if not found."""
    for path in AGENT_DIR.rglob(filename):
        # path looks like Sorted_Agent/{Task}/{Date}/{filename} or Sorted_Agent/_Needs_Review/{filename}
        relative = path.relative_to(AGENT_DIR)
        top_folder = relative.parts[0]
        return top_folder  # task name, or "_Needs_Review"
    return "NOT_FOUND"


def find_file_in_baseline(filename: str) -> str:
    """Baseline has no task concept — just confirm the file exists somewhere."""
    for path in BASELINE_DIR.rglob(filename):
        return str(path.relative_to(BASELINE_DIR))
    return "NOT_FOUND"


def evaluate():
    ground_truth = load_ground_truth()

    agent_correct = 0
    agent_total = 0
    agent_results = []

    for filename, true_task in ground_truth.items():
        agent_location = find_file_task_agent(filename)

        if true_task is None:
            # Ambiguous case — correct behavior is landing in _Needs_Review
            is_correct = (agent_location == "_Needs_Review")
            expected = "_Needs_Review"
        else:
            is_correct = (agent_location == true_task)
            expected = true_task

        agent_total += 1
        if is_correct:
            agent_correct += 1

        agent_results.append({
            "file": filename,
            "expected": expected,
            "agent_placed_in": agent_location,
            "correct": is_correct
        })

    print("=" * 70)
    print("AGENT RESULTS")
    print("=" * 70)
    for r in agent_results:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} {r['file']:40s} expected={r['expected']:20s} got={r['agent_placed_in']}")

    print(f"\nAgent accuracy: {agent_correct}/{agent_total} ({100*agent_correct/agent_total:.1f}%)")

    print("\n" + "=" * 70)
    print("BASELINE (extension+date only — no task awareness)")
    print("=" * 70)
    print("Baseline has no concept of 'task', so it cannot be scored on task accuracy.")
    print("It groups files purely by file type, mixing unrelated tasks together.")
    print("This is the qualitative cost of the baseline approach vs. the agent's")
    print(f"{100*agent_correct/agent_total:.1f}% task-classification accuracy shown above.")

    with open("eval/eval_results.json", "w") as f:
        json.dump({
            "agent_accuracy": agent_correct / agent_total,
            "agent_correct": agent_correct,
            "agent_total": agent_total,
            "details": agent_results
        }, f, indent=2)

    print(f"\nResults saved to eval/eval_results.json")


if __name__ == "__main__":
    evaluate()
