# Network Intrusion Detection with Feature Selection (UNSW-NB15)

Minor project, CSE, IIIT Ranchi. Guide: Dr. Bharat Singh.

An intrusion detector trained on one day of traffic and tested on another meets a different traffic mix. This repo measures how much that costs on the **official** UNSW-NB15 split, fixes part of it without ever reading a test label, and measures the ceiling no model can pass. Five classifiers, three feature-selection methods, a label-free adaptation step, a zero-day test.

**Stack:** Python ≥ 3.10 · pandas · scikit-learn · XGBoost · matplotlib. No GPU.

---

## Run it

**1. Get the data.** Put the two official partition files in `data/`. Source: the [UNSW-NB15 page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) (folder *Training and Testing Sets*). The copies used here came from two independent GitHub mirrors whose testing files are byte-identical:

| File | Rows | MD5 |
|---|---:|---|
| `UNSW_NB15_training-set.csv` | 175,341 | `e55caabaa6cd4a8f1c06a227bcfababc` |
| `UNSW_NB15_testing-set.csv` | 82,332 | `e0beea40262e46168cdb81476dbc27b4` |

**2. Install and run** (about 15 minutes on 4 CPU cores):

```bash
pip install -e ".[dev]"
python -m ids.run --data data --out results
```

The first lines printed are the class counts. They must match `docs/research.md`.

---

## What it writes

| File | Contents |
|---|---|
| `results/improvement.csv` | The headline: XGBoost, + prior shift, + class bias, + both, for both tasks |
| `results/results.csv` | Every model on all features, and the feature-selection sweep |
| `results/ceiling.csv` | Best accuracy and macro-F1 any model can reach on the test file |
| `results/zero_day.csv` | Detection of each attack type when it was held out of training |
| `results/recall_gain_*.csv`, `per_class_recall_*.csv` | Per-class recall |
| `results/ranking_*.csv` | Feature order chosen by each selection method |
| `results/*.png` | Confusion matrices, per-class recall gain, selection curves, zero-day and conflict charts |

---

## Layout

```
ids/          data, models, adapt, ceiling, plots → metrics, selection → experiments → run
tests/        pytest on synthetic UNSW-shaped data, plus the import-boundary test
docs/         research.md (findings) · ppt-content.md (slide content) · assets/ (slide figures)
scripts/      slide_figures.py: python scripts/slide_figures.py redraws docs/assets/
notes/        summaries of the IDS papers the guide shared
```

## Before committing

```bash
ruff check . && ruff format --check . && pytest -q
```
