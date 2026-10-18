# P3.32R12 — Offline daily audit, fail-closed

Branch-only CI is triggered on pull requests and manual dispatch. A daily GitHub cron is intentionally **not** activated because scheduled workflows operate from the default branch; this PR must not change production.

The workflow reads an optional `tools/editorial_review/evidence/YYYY-MM-DD.json` claim matrix, validates its structure, and uploads a blocked report. Without evidence it records `EVIDENCE_NOT_PROVIDED`. Even with structurally complete evidence it records `STRUCTURE_VALID_HUMAN_FACT_CHECK_REQUIRED`, never approval.

**Limitations:** This pipeline does not independently retrieve web sources, validate truth, determine image rights, produce three new factual dossiers, or publish any videos. It does not write to the repository, production datastore, or TikTok. It has `contents: read` only and uses no application secrets. Reports are retained for 14 days as ephemeral GitHub Actions artifacts.

Proposed future schedule, **not enabled**: one UTC run each day on a dedicated safe default-branch workflow after editorial review and permission controls. Before enabling, inspect workflows for implicit production side effects and separately authorize rollout. For Tu Perro Feliz, carry over only these nonpublishing validation primitives after expert-content policy review.
