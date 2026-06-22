# MITRE ATLAS Matrix for AI Systems

This document is the VulnoraIQ planning matrix for MITRE ATLAS tactics, techniques, and sub-techniques. It is designed to help add ATLAS coverage into VulnoraIQ modules, safe test assets, fixtures, reports, and dashboards over time.

> **Current status:** planning and traceability document. The checked-in table is a planning snapshot. The source-driven generator in `scripts/generate_mitre_atlas_matrix.py` must be used to regenerate the full official matrix from `mitre-atlas/atlas-data` before implementation work is marked complete.

> **Mapping rule:** if a tactic or technique cannot be confidently mapped to OWASP or a VulnoraIQ coverage area, it must still be listed and marked `Unmapped / map later`. No ATLAS item should disappear just because it is not mapped yet.

## Official source alignment

Use the official MITRE ATLAS sources:

- Site: `https://atlas.mitre.org`
- Data repository: `https://github.com/mitre-atlas/atlas-data`
- Current generator default: `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml`
- Generator: `scripts/generate_mitre_atlas_matrix.py`

## Regenerate the full matrix

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md
```

Check for drift:

```bash
vulnoraiq-generate-atlas-matrix \
  --source https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.05.yaml \
  --output docs/MITRE_ATLAS_AI_MATRIX.md \
  --check
```

## Required generated columns

| Column | Meaning |
| --- | --- |
| Tactic ID / Technique ID | Official ATLAS identifier. |
| Tactic / Technique | Official ATLAS name. |
| Tactic(s) | Official tactic relationship where available. |
| Maturity | Official ATLAS maturity field where available. |
| Platform(s) | Official ATLAS platform list where available. |
| OWASP mapping | Candidate OWASP LLM mapping, or `Unmapped / map later`. |
| VulnoraIQ coverage area | Candidate VulnoraIQ area, or `Unmapped / map later`. |
| Implementation status | Candidate, working starter, production validated, or `Unmapped / map later`. |
| Planning notes | What needs to be added before implementation can be claimed. |

## Drift-control rule

Future changes must not manually remove generated tactic or technique rows. Update the official source version or generator, regenerate this file, then update VulnoraIQ configuration against the regenerated IDs. Unmapped entries must stay visible until deliberately mapped or excluded with documented rationale.
