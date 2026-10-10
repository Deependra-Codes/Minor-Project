# Minor Project — IIIT Ranchi CSE

Guide: Dr. Bharat Singh (Asst. Prof., CSE). Guide keywords: medicinal plant identification,
medicinal leaf classification, feature selection + ML, dynamic intrusion detection.

## LOCKED TARGET
Topic: medicinal leaf classification with deep features + feature selection + classic ML.
Claim: same accuracy with far fewer features, faster prediction. Not "higher accuracy" (papers already ~99.8%).
Data: Mendeley Medicinal Leaf Dataset, Roopashree & Anitha 2020, DOI 10.17632/nnytj2v3n5.1, 30 species, ~1,800 images, CC BY 4.0.
Same data as MedPlantNet (notes/medplantnet.md, 99.87%), so direct comparison.
Code: `leaf_fs.py` (EfficientNetB0 ImageNet features -> ANOVA-F / mutual info / PCA -> SVM; plus KNN, RF, LogReg on all features).
First deliverable (2 days from 2026-10-10): synopsis + first result.
Network: data.mendeley.com blocked in cloud env; run on Colab or ask user to allow host.

Paper sources: ScienceDirect, IEEE Xplore, MDPI.

## Default mode
Use `caveman` skill for chat replies and `ponytail` skill for code, every session.
Both live in `.claude/skills/`.

## Token rules
- PDFs go in `papers/` (gitignored: publisher copyright). Never read a PDF whole into context.
- Extract once: `pdftotext -layout papers/X.pdf papers/txt/X.txt`, then grep/read only needed parts.
- Write one short summary per paper in `notes/X.md` (problem, dataset, method, features, accuracy, gaps).
- Later sessions read `notes/`, not PDFs.
