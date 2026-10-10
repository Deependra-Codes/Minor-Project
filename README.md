# Network Intrusion Detection with Feature Selection (UNSW-NB15)

Minor project, CSE, IIIT Ranchi. Guide: Dr. Bharat Singh.

An intrusion detector trained on one day of traffic and tested on another meets a different traffic mix. This repo measures how much that costs on the **official** UNSW-NB15 split, fixes part of it without reading a test label, cuts false alarms further with a small analyst-feedback loop, and measures the ceiling no model can pass. Six classifiers, three feature-selection methods, label-free adaptation, analyst feedback, a zero-day test.

**Stack:** Python ≥ 3.10 · pandas · scikit-learn · XGBoost · matplotlib. No GPU.

---

## Run it

**1. Get the data.** Put the two official partition files in `data/`. Source: the [UNSW-NB15 page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) (folder *Training and Testing Sets*). The copies used here came from two independent GitHub mirrors whose testing files are byte-identical:

| File | Rows | MD5 |
|---|---:|---|
| `UNSW_NB15_training-set.csv` | 175,341 | `e55caabaa6cd4a8f1c06a227bcfababc` |
| `UNSW_NB15_testing-set.csv` | 82,332 | `e0beea40262e46168cdb81476dbc27b4` |

**2. Install and run** (about 25 minutes on 4 CPU cores):

```bash
pip install -e ".[dev]"
python -m ids.run --data data --out results
```

The first lines printed are the class counts. They must match:

| | Normal | Generic | Exploits | Fuzzers | DoS | Reconnaissance | Analysis | Backdoor | Shellcode | Worms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 56,000 | 40,000 | 33,393 | 18,184 | 12,264 | 10,491 | 2,000 | 1,746 | 1,133 | 130 |
| test | 37,000 | 18,871 | 11,132 | 6,062 | 4,089 | 3,496 | 677 | 583 | 378 | 44 |

**3. Regenerate the slide text** (every number comes from `results/`):

```bash
python scripts/slide_content.py
```

---

## What it writes

| File | Contents |
|---|---|
| `results/improvement.csv` | The headline: XGBoost, + prior shift, + class bias, + both, + analyst feedback, for both tasks; all scored on the test flows no analyst labelled |
| `results/feedback_curve.csv` | Scores after each round of 200 analyst labels |
| `results/results.csv` | Every model on all features, and the feature-selection sweep |
| `results/ceiling.csv` | Best accuracy and macro-F1 any model can reach on the test file |
| `results/zero_day.csv` | Detection of each attack type when it was held out of training |
| `results/recall_gain_*.csv`, `per_class_recall_*.csv` | Per-class recall |
| `results/ranking_*.csv` | Feature order chosen by each selection method |
| `results/*.png` | Confusion matrices, per-class recall gain, selection curves, feedback, zero-day and conflict charts |

---

## Layout

```
ids/          data, models, adapt, ceiling, plots → metrics, selection → experiments → run
tests/        pytest on synthetic UNSW-shaped data, plus the import-boundary test
docs/         ppt-content.md (slide text and speaker notes) · assets/ (slide figures)
scripts/      slide_figures.py redraws docs/assets/ · slide_content.py fills docs/ppt-content.md from results/
notes/        summaries of the IDS papers the guide shared
```

## Before committing

```bash
ruff check . && ruff format --check . && pytest -q
```
