# Sort & Close Agent

## The user & the bottleneck
I frequently work across multiple tasks/projects (client proposals, tax filing, website redesign work, conference preparation) and leave files scattered unsorted in my Downloads folder, and leave documents/tabs open across sessions, due to a busy schedule. This creates two recurring problems: I can't quickly find files related to a specific project later, and I accumulate open clutter that never gets cleaned up.

## What existed before vs. what I built
- Gemini CLI was used as a coding assistant to help generate synthetic test data and draft some scripts.
- The deployed agent calls the Gemini API (gemini-3.5-flash-lite) at runtime to make sort/close decisions — this is the part being evaluated.

## The two agents
1. **Sort agent** — reads files from a Downloads-like folder, classifies each into one of 4 tasks using filename + content + date, and copies them into `/Sorted_Agent/{Task}/{Date}/filename`. Files it can't confidently classify go to `/Sorted_Agent/_Needs_Review/` rather than being guessed.
2. **Close agent** — reads a simulated set of open tabs/documents, and decides CLOSE / KEEP_OPEN / NEEDS_CONFIRMATION based on task status. For ambiguous items, it generates a human-readable one-line summary so a user can quickly decide.

## Folder structure
- `/baseline` — simple baseline: sorts by file extension + date only (no task awareness)
- `/agent` — sort_agent.py and close_agent.py (the actual agent solution)
- `/data` — synthetic test data (raw_downloads/, open_items.json, ground_truth.json, Sorted_Baseline/, Sorted_Agent/)
- `/eval` — run_eval.py and eval_results.json
- `/trajectories` — saved agent run logs (reasoning, decisions, errors)
- `TAXONOMY_SPEC.md` — the written spec defining folder schema, classification rules, and model choice

## Improvement changelog
| Stage | What I tried & why | Evidence | Decision |
|---|---|---|---|
| Baseline | Sort by extension + date only, mimicking default OS file explorer behavior | Mixes unrelated tasks together (e.g. Client Proposal and Conference Prep docs both land in the same DOCX folder) | Established the starting point — no task awareness at all |
| Agent v1 | LLM classification (gemini-3.5-flash) using filename + content, constrained to 4 fixed tasks, with a confidence-gated `_Needs_Review` fallback instead of forced guessing | 20/20 (100%) on initial 20-file test set, including correct handling of 2 ambiguous cases | Strong result, but test set may have been too easy — filenames/content were fairly explicit |
| Agent v1 (adversarial test) | Added 2 harder test files: one with a misleading filename ("Proposal_Feedback.docx" is actually about a conference talk, not a client proposal), one with genuine task overlap (a demo prep note touching both Website Redesign and Conference Prep) | 22/22 (100%) — agent correctly read content over the misleading filename, and correctly resolved the overlapping case using deadline context | Confirms the agent reasons over content, not just filename pattern-matching |
| Model switch | Hit gemini-3.5-flash's free-tier daily quota (20 requests/day) repeatedly during iterative testing, which interrupted development multiple times | Switched to gemini-3.5-flash-lite; observed identical accuracy on side-by-side comparisons | Adopted flash-lite as the project's default model going forward |

## How to run
```bash
git clone https://github.com/ivyanalyst/hackathon-sort-close-agent.git
cd hackathon-sort-close-agent
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then add your GEMINI_API_KEY
python3 baseline/sort_baseline.py
python3 agent/sort_agent.py
python3 eval/run_eval.py
python3 agent/close_agent.py
```

**Expected output:** the sort agent classifies 22 files with ~100% accuracy against ground truth; the close agent evaluates 10 open items, closing 4, keeping 4 open, and flagging 2 for human confirmation.

**Runtime:** roughly 5-6 minutes total (rate-limited to stay under free-tier API limits). **Cost:** near $0 on gemini-3.5-flash-lite's free tier for a run of this size.

## Hot take
The agent's classification reasoning was reliable from the first working version — the real failure mode I hit repeatedly wasn't model reasoning, it was **infrastructure**: free-tier API rate limits broke batch runs mid-way through multiple times, and my first error-handling attempt silently dropped failed files instead of routing them to review. This taught me that a production agent system needs to treat "the model couldn't answer" and "the API call never completed" as two different failure states — conflating them either hides real errors or falsely reports model failures that were actually just rate limits.
