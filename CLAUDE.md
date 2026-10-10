# Minor Project — IIIT Ranchi CSE

Guide: Dr. Bharat Singh (Asst. Prof., CSE). Guide keywords: medicinal plant identification,
medicinal leaf classification, feature selection + ML, dynamic intrusion detection.

## LOCKED TARGET
Topic: network intrusion detection on the official UNSW-NB15 split; feature selection + ML; label-free adaptation to traffic shift.
Findings so far: 93.6% multiclass accuracy ceiling (identical vectors, different labels); Analysis/Backdoor ~90% of test rows unidentifiable;
TTL testbed shortcut; normal share 31.9% train vs 44.9% test drives a ~26% false-alarm rate.
Method: XGBoost + EM prior shift (no test labels) + macro-F1 class bias tuned on out-of-fold train predictions. Zero-day = leave-one-attack-out.
Code: `ids/` (rules in AGENTS.md). Gate: `ruff check . && ruff format --check . && pytest -q`. Full run: `python -m ids.run` (~15 min).
Data: data/UNSW_NB15_{training,testing}-set.csv, gitignored, MD5s in README. Official site, Zenodo, HF, Kaggle blocked here; GitHub mirrors work.
Deliverables: results/ (numbers + figures), docs/ppt-content.md (slide text only, no design), docs/assets/ (slide figures).

Paper sources: ScienceDirect, IEEE Xplore, MDPI.

## Default mode
Use `caveman` for chat replies, `ponytail` for code, and superpowers `test-driven-development`,
`systematic-debugging`, `verification-before-completion` for all code work. All in `.claude/skills/`.

## Token rules
- PDFs go in `papers/` (gitignored: publisher copyright). Never read a PDF whole into context.
- Extract once: `pdftotext -layout papers/X.pdf papers/txt/X.txt`, then grep/read only needed parts.
- Write one short summary per paper in `notes/X.md` (problem, dataset, method, features, accuracy, gaps).
- Later sessions read `notes/`, not PDFs.
