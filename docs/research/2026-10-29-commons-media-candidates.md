# Media candidates — 2026-10-29 (research only)

Status: CANDIDATE_NOT_APPROVED. This is **not** a license audit, a render authorization or publication clearance. Content stays in `content/research/`; do not promote it or override existing `RESEARCH_DRAFT_UNAPPROVED` / `RIGHTS_UNVERIFIED_NO_RENDER` gates.

Candidates were identified from public Wikimedia Commons **file pages** on 2026-10-29. Page claims must be checked again against the MediaWiki API `imageinfo.extmetadata`, actual downloaded bytes, SHA256 and repository `scripts/audit_commons_licenses.py`. Attribution must appear visibly/legibly with the license URL and modifications notice; review share-alike implications for the resulting video before publication.

| Slot / subject | Commons title | Declared author; license shown on page | Review caveat |
| --- | --- | --- | --- |
| 10:00 European Constitutional Treaty and Spanish ratification | `File:Referendum Constitución europea 2005 España (3).JPG` | Falconaumanni; CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0 | Photo taken in 2015 of Spanish 2005 referendum materials; **not** the signing ceremony of 29 Oct 2004. Label as illustrative referendum material, never as contemporaneous footage. |
| 16:00 Altamira | `File:Museo Nacional y Centro de Interpretación de Altamira.jpg` | Jl FilpoC; CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0 | Photo of the **museum building**, not prehistoric pigment, bison painting or original cave interior. Further directly relevant images should be sourced separately. |
| 19:00 irrigators' court | `File:Valencia Water Court.JPG` | Martinvl; CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0 | Shows a Water Court session in Valencia; **does not** represent the separate Murcia institution. |

Commons file-page evidence:
- https://commons.wikimedia.org/wiki/File:Referendum_Constituci%C3%B3n_europea_2005_Espa%C3%B1a_(3).JPG
- https://commons.wikimedia.org/wiki/File:Museo_Nacional_y_Centro_de_Interpretaci%C3%B3n_de_Altamira.jpg
- https://commons.wikimedia.org/wiki/File:Valencia_Water_Court.JPG

Before promotion to `content/2026-10-29*.json`:
1. Fetch exact Commons title, API `LicenseShortName` / `LicenseUrl`, `Artist`, `Credit`, source URL, and bytes. Run repository gate; preserve full credits.json, SHA256 and license links. Refuse mismatched/unsupported license metadata.
2. Check image relevance and distinguish historical originals, reconstructions, museum images and modern reference photos. No invented provenance.
3. Confirm required source/fact review, no reuse of published-history topics, fitting dates and series, and a proper credit format for video and caption. Explicitly review share-alike duties.
4. Run canonical validators and render tests; perform visual review and confirm rights before making any content or render status green.

No media downloaded, no hash asserted, no approval, no video rendered, no posting.
