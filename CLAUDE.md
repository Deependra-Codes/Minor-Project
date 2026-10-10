# Minor Project — IIIT Ranchi CSE

Guide: Dr. Bharat Singh (Asst. Prof., CSE). Topic not fixed yet.
Pick one keyword, read papers, pick topic:
- medicinal plant identification
- medicinal leaf classification
- feature selection + ML
- dynamic intrusion detection

Paper sources: ScienceDirect, IEEE Xplore, MDPI.

## Default mode
Use `caveman` skill for chat replies and `ponytail` skill for code, every session.
Both live in `.claude/skills/`.

## Token rules
- PDFs go in `papers/`. Never read a PDF whole into context.
- Extract once: `pdftotext -layout papers/X.pdf papers/txt/X.txt`, then grep/read only needed parts.
- Write one short summary per paper in `notes/X.md` (problem, dataset, method, features, accuracy, gaps).
- Later sessions read `notes/`, not PDFs.
