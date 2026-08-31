# Sorting & Closing Taxonomy Spec

## Folder schema
Sorted files are placed at: `/Sorted/{TaskName}/{Date}/{filename}`

Date format: `YYYY-MM-DD` (based on the file's creation date), e.g. `/Sorted/Tax Filing/2026-08-12/W2_Statement_2025.pdf`

Task names (fixed set for v1):
- Client Proposal
- Tax Filing
- Website Redesign
- Conference Prep

Files that cannot be confidently classified go to: `/Sorted/_Needs_Review/{filename}`
(no date subfolder for review items, since the point is a human looks at them directly)

## Signals used for classification
- Filename (primary signal — keywords, naming patterns)
- File creation date (secondary signal — used to determine the date subfolder, and to help break ties on task when filename is ambiguous)
- File content is NOT used in v1 (test files are empty placeholders)

## Confidence threshold
If the agent cannot confidently assign a file to one of the 4 tasks, it must route the file to `_Needs_Review` rather than guessing. "Confidently" means the agent returns a reasoning string explaining its decision — this is what gets logged in trajectories.

## Close-agent status logic
- status: "done" → safe to close
- status: "in_progress" → must NOT close
- status: "unclear" / task: null → must ask for human confirmation before closing (per hackathon ground rule on human approval for consequential actions)

## Baseline (for comparison)
The baseline sorts using ONLY file extension + creation date (no filename keyword reasoning) into `/Sorted_Baseline/{Extension}/{Date}/filename`, mimicking default OS file explorer sort behavior. It has no concept of "task" and no _Needs_Review fallback — it always makes a decision.

## Model choice
The agent uses gemini-3.5-flash-lite rather than gemini-3.5-flash. This was a deliberate choice after observing gemini-3.5-flash's free-tier daily quota (20 requests/day) repeatedly blocked iterative testing during development. flash-lite has a separate, more workable quota for a project of this scale, and showed no observable difference in classification accuracy or reasoning quality on this task during side-by-side testing (both achieved 100% accuracy on the same test files).
