# AGENTS.md

Engineering rules for this repo. Ruff and pytest enforce most of them. The rest are written here because no tool can check them.

## Where things live

| Module | Owns | May import from `ids` |
|---|---|---|
| `ids/data.py` | Reading the two official CSVs, schema check, target, encoding | nothing |
| `ids/models.py` | Classifier factory and every hyperparameter | nothing |
| `ids/plots.py` | Report figures and their colors | nothing |
| `ids/metrics.py` | Scores for one prediction | `data` |
| `ids/selection.py` | Feature ranking methods | `data` |
| `ids/run.py` | CLI, experiment order, writing `results/` | all of the above |

`scripts/slide_figures.py` draws the slide visuals that need no results into `docs/assets/`. It imports nothing from `ids`.

Imports go downward only. `tests/test_boundaries.py` fails the build on an upward import. A new module gets a row here and in that test, or the test fails.

## Non-negotiable

- **Official split only.** Train on `UNSW_NB15_training-set.csv`, test on `UNSW_NB15_testing-set.csv`. Never pool and re-split them: random re-splits inflate scores and make the numbers incomparable with the literature.
- **Everything fitted is fitted on train only:** encoders, scalers, feature rankings. The test file is used once, for prediction.
- **`id` is never a feature.** It is a row number.
- **Report macro-F1 and per-class recall, never accuracy alone.** Accuracy hides Worms (130 training rows) and Backdoor.
- **Seed 42 everywhere.** A number that changes on re-run is not a result.
- **Every result number in a slide, the synopsis or the report comes from `results/*.csv` made by committed code.** No hand-typed numbers.

## Size

300 lines per file, 60 per function. A file outgrowing these is usually doing two jobs.

## Reuse

Prefer duplication over the wrong abstraction. Abstract on the third instance, not the second.

## Proving a rule

After adding a rule, break it on purpose, watch the check fail and name the rule, then restore. The boundary test was proven this way: an upward import in `data.py` and a plain `import ids.plots` in `metrics.py` both failed it.

## Before calling work done

```bash
ruff check . && ruff format --check . && pytest -q
```

The gate runs **before** the commit, not after it.
