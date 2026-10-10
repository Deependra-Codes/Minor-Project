# Minor Project — IIIT Ranchi CSE

Guide: Dr. Bharat Singh (Asst. Prof., CSE). Guide keywords: medicinal plant identification,
medicinal leaf classification, feature selection + ML, dynamic intrusion detection.

## LOCKED TARGET (2026-10-10)
Topic: network intrusion detection, feature selection + classic ML, UNSW-NB15 official train/test split.
Claim: fair same-protocol comparison of ANOVA-F / mutual info / RF importance; fewer features, same macro-F1; per-class recall for rare attacks. Not "beat SOTA".
Code: `ids/` package, rules in AGENTS.md, gate `ruff check . && ruff format --check . && pytest -q`.
Docs: `docs/research.md` (problem, verified literature, gap, plan), `docs/ppt-content.md` (slide brief for another AI).
First deliverable (by 2026-10-12): synopsis + first result.
Data: data/UNSW_NB15_{training,testing}-set.csv, gitignored. UNSW site, Zenodo, HF, Mendeley blocked in cloud env: user uploads CSVs or runs on Colab.
Old leaf topic dropped; script in git history (a4f7faf).

Paper sources: ScienceDirect, IEEE Xplore, MDPI.

## Default mode
Use `caveman` skill for chat replies and `ponytail` skill for code, every session.
Both live in `.claude/skills/`.

## Token rules
- PDFs go in `papers/` (gitignored: publisher copyright). Never read a PDF whole into context.
- Extract once: `pdftotext -layout papers/X.pdf papers/txt/X.txt`, then grep/read only needed parts.
- Write one short summary per paper in `notes/X.md` (problem, dataset, method, features, accuracy, gaps).
- Later sessions read `notes/`, not PDFs.
