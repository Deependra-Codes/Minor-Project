# Network Intrusion Detection with Feature Selection (UNSW-NB15)

Minor project, CSE, IIIT Ranchi. Guide: Dr. Bharat Singh.

Which of the 42 traffic features does an intrusion detector actually need, and what happens to the rare attack classes when you keep fewer? This repo answers that on the **official** UNSW-NB15 train/test split. It compares five classifiers and three feature-selection methods, and reports macro-F1, per-class recall, detection rate and false-alarm rate.

**Stack:** Python ≥ 3.10 · pandas · scikit-learn · matplotlib. No GPU.

---

## Run it

**1. Get the data.** Download the two official partition files from the [UNSW-NB15 page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) (folder *Training and Testing Sets*) or a Kaggle mirror. Put them in `data/`:

```
data/UNSW_NB15_training-set.csv   # 175,341 rows
data/UNSW_NB15_testing-set.csv    #  82,332 rows
```

**2. Install and run.**

```bash
pip install -e ".[dev]"
python -m ids.run --data data --out results          # both tasks
python -m ids.run --task binary                      # one task only
```

**On Google Colab:** upload the repo folder and the two CSVs, then run `!pip install -q -e .` and `!python -m ids.run`.

The first lines printed are the class counts. They must match the table in [`docs/research.md`](docs/research.md#dataset). If they don't, the files are not the official partition.

---

## What it writes

| File | Contents |
|---|---|
| `results/results.csv` | One row per (task, selection method, model, k): accuracy, macro-F1, weighted-F1, detection rate, false-alarm rate, fit time, predict time per row |
| `results/class_counts.csv` | Rows per class in train and test |
| `results/per_class_recall_{task}.csv` | Recall of every class for every model on all features |
| `results/ranking_{task}.csv` | Feature order chosen by each selection method |
| `results/confusion_{task}.png` | Confusion matrix of the best model by macro-F1 |
| `results/selection_{task}.png` | Macro-F1 against number of features kept, one line per method |

---

## Layout

```
ids/          data → selection, metrics → run   (imports go downward only; see AGENTS.md)
tests/        pytest on synthetic UNSW-shaped data, plus the import-boundary test
docs/         research.md (problem, literature, gap, plan) · ppt-content.md (slide brief) · assets/ (slide figures)
scripts/      slide_figures.py: python scripts/slide_figures.py redraws docs/assets/
notes/        one-page summaries of the papers the guide shared
```

## Before committing

```bash
ruff check . && ruff format --check . && pytest -q
```
