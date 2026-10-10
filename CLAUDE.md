# Minor Project — IIIT Ranchi CSE

Guide: Dr. Bharat Singh (Asst. Prof., CSE). Guide keywords: medicinal plant identification,
medicinal leaf classification, feature selection + ML, dynamic intrusion detection.

## LOCKED TARGET
Topic: network intrusion detection on the official UNSW-NB15 split; feature selection + ML; label-free adaptation to traffic shift.
Findings (results/, run from df55a06): 93.60% 10-class accuracy ceiling (identical flows, different labels;
Analysis 91%, Backdoor 90% have twins). Attack share 68.1% train vs 55.1% test drives ~26% false alarms; 73% of them
are read as Fuzzers and 70% of their training neighbours are attacks. Class-balanced HistGB alone: binary FAR 15.7%.
Final (XGBoost + rare-class bias + EM prior shift + 1,000 analyst labels): 10-class macro-F1 0.506 -> 0.575, FAR 23.9% -> 18.4%;
binary FAR 25.3% -> 18.4%. Top-5 mutual-information features ~ all 42. Zero-day: 8 of 9 attack types >= 90%, Fuzzers 41%.
Macro-F1 ceiling is a bracket 0.785-0.788 (0.765 is only the accuracy oracle's). TTL: rewriting attack sttl to 31
(70.5% of training normals) drops XGBoost detection 98.2% -> 0.23%; sweep bands: TTL 0-61 <= 0.23%, attack TTLs 62/254 >= 98.3%,
others ~77%. sttl is the top pro-attack feature for 96% of the 9,693 false alarms. TTL-free (39 features): detection 97.9%,
immune to the rewrite, FAR 26.6% vs 26.2%, macro-F1 0.493 vs 0.505. Edits re-derive ct_state_ttl (rule matches 99.83% of test).
Method: XGBoost + EM prior shift (no test labels) + macro-F1 class bias (out-of-fold train) + analyst feedback (5x200 least-certain flows). Zero-day = leave-one-attack-out.
Code: `ids/` (rules in AGENTS.md). Gate: `ruff check . && ruff format --check . && pytest -q`. Full run: `python -m ids.run` (~25 min), then `python scripts/slide_content.py`.
Data: data/UNSW_NB15_{training,testing}-set.csv, gitignored, MD5s in README. Official site, Zenodo, HF, Kaggle blocked here; GitHub mirrors work.
Deliverables: results/ (numbers + figures), docs/ppt-content.md (slide text only, no design; every number from results/), docs/assets/ (slide figures).

Paper sources: ScienceDirect, IEEE Xplore, MDPI.

## Default mode
Use `caveman` for chat replies, `ponytail` for code, and superpowers `test-driven-development`,
`systematic-debugging`, `verification-before-completion` for all code work. All in `.claude/skills/`.

## Token rules
- PDFs go in `papers/` (gitignored: publisher copyright). Never read a PDF whole into context.
- Extract once: `pdftotext -layout papers/X.pdf papers/txt/X.txt`, then grep/read only needed parts.
- Write one short summary per paper in `notes/X.md` (problem, dataset, method, features, accuracy, gaps).
- Later sessions read `notes/`, not PDFs.
