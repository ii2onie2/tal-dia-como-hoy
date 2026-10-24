# P3.32R11 — Claim evidence review queue (not approved)

Date: 2026-10-18. Historical dossier date: **2026-10-17**, NOT Oct 18.

This is an audit work queue, **not** a machine-validated source-to-claim matrix. The JSON gate requires two genuinely independent, located supporting excerpts for EACH claim; absence must fail closed. No excerpt has been mechanically extracted and matched in this change.

| ID | Claim to verify | Candidate authoritative reference | Secondary review | Decision |
|---|---|---|---|---|
| IRENE-01 | 17 Oct 1991, an ETA bomb attack injured Irene Villa and her mother in Madrid | Fundación Víctimas del Terrorismo, profile discussing the attack (see P3.32R10 audit) | RTVE report; verify precise paragraphs | PENDING_HUMAN_REVIEW |
| AMNISTY-01 | Ley 46/1977 is dated 15 Oct 1977 and entered into force on the day of publication, 17 Oct | BOE, BOE-A-1977-24937, preamble/date and final provision | Second independent historical commentary; verify legal phrasing | PENDING_HUMAN_REVIEW |
| NAVARRA-01 | First academic inaugural act was on 17 Oct 1952; initial institution was established in April | Universidad de Navarra institutional history, 1952 chronology | Independent source to identify and verify | PENDING_HUMAN_REVIEW |

## Automated gate and deployment boundary

- `validate_research_dossiers.py` checks three-slot packet structure.
- `validate_claim_matrix.py` checks each claim has two independently attributed, located snippets and permanently returns **FACTUAL_APPROVAL_NO**.
- **No verification of truth** is performed by either script; a syntactically valid evidence matrix could still be wrong.
- CI is isolated to the existing draft PR, with no publication, token injection, write permissions, secrets or production data.
- GitHub scheduled workflows execute from the **default branch**. Scheduling is therefore deliberately NOT enabled on this unmerged branch; a future scheduler requires a separate reviewed, nonpublishing integration and manual approval.
- Reuse in Tu Perro Feliz remains documentation-only pending species-specific review.

Gate for next step: gather and quote exact lawful source excerpts; manually verify each claim-to-excerpt mapping and chronology; then review without ever automatically setting approval flags.
