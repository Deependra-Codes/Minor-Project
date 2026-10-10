# Research: Feature Selection for Network Intrusion Detection on UNSW-NB15

## 1. Problem

An **intrusion detection system (IDS)** watches network traffic and flags attacks. Signature-based IDSs only catch attacks they already have a rule for. Machine-learning IDSs learn from labelled traffic records ("flows") instead, so they can generalise to variants. Two practical problems remain:

1. **Too many features.** Each flow has dozens of statistics: bytes, packets, TTLs, jitter, connection counts. Many are redundant or noisy. Extra features slow training and prediction and can hurt accuracy. A deployed IDS has to classify flows in real time.
2. **Rare attacks get ignored.** Attack classes are heavily imbalanced. A model can score high accuracy while missing almost every rare attack, because the rare classes barely move the accuracy number.

**Question this project answers:** on the official UNSW-NB15 split, how few features can an IDS keep without losing detection quality? And which feature-selection method keeps the rare attack classes detectable?

## 2. Dataset

**UNSW-NB15** was created by Moustafa & Slay (2015) at the UNSW Canberra Cyber Range Lab. It mixes real normal traffic with synthetic modern attacks. It was built to replace the outdated KDD'99 and NSL-KDD datasets.

The official partition used here:

| | Training file | Testing file |
|---|---|---|
| Records | 175,341 | 82,332 |
| Features | 42 (39 numeric, 3 categorical: `proto`, `service`, `state`) | same |
| Labels | `label` (0 normal / 1 attack), `attack_cat` (10 classes) | same |

Class counts (the script prints these; they must match):

| Class | Train | Test |
|---|---:|---:|
| Normal | 56,000 | 37,000 |
| Generic | 40,000 | 18,871 |
| Exploits | 33,393 | 11,132 |
| Fuzzers | 18,184 | 6,062 |
| DoS | 12,264 | 4,089 |
| Reconnaissance | 10,491 | 3,496 |
| Analysis | 2,000 | 677 |
| Backdoor | 1,746 | 583 |
| Shellcode | 1,133 | 378 |
| Worms | 130 | 44 |

Worms make up 0.07% of the training rows. That is why accuracy alone is misleading on this dataset.

## 3. Literature

| Work | Method | Reported result | Note |
|---|---|---|---|
| Kasongo & Sun, *J. Big Data* 2020 | XGBoost feature importance → ANN, kNN, DT, LR, SVM | DT binary accuracy 88.13% → 90.85% after selection | Most-cited FS study on this dataset |
| Yin et al., *J. Big Data* 2023 (IGRF-RFE) | Information gain + RF filter, then RFE with MLP | 42 → 23 features; MLP multiclass accuracy 82.25% → 84.24%; weighted F1 82.85% | Hybrid filter + wrapper |
| Sarhan et al., arXiv 2101.11315 (2021) | Per-class evaluation on original UNSW-NB15 | Worms: detection 5.26%, F1 0.09; Backdoor F1 0.08 | Shows how badly rare classes fail |
| Nguyen & Park, *Electronics* 2025 (EL-GNN, guide-shared) | Graph neural network + continual learning | 96.4% accuracy on UNSW-NB15 | Heavy model; check its split before comparing |
| IIETA 2026 (XGBoost + χ²) | χ² selection + XGBoost | High multiclass scores | Pools train + test and re-splits 80/20: not comparable to the official split |

Summaries of the guide's five papers are in `notes/`.

## 4. Gap

1. **Protocols differ.** Many papers pool the two files and re-split them at random. That inflates scores, so their numbers cannot be compared with official-split numbers.
2. **Accuracy hides minority classes.** Most papers report accuracy or weighted F1. Both are dominated by Normal, Generic and Exploits.
3. **Selection methods are rarely compared head to head.** In the papers checked, each study tests one selection method under its own protocol. We found no comparison of filter methods (ANOVA-F, mutual information) and embedded methods (random-forest importance) under one fixed protocol with per-class results.

## 5. Objectives

- **O1.** Strict baselines on the official split: Logistic Regression, Decision Tree, Random Forest, Histogram Gradient Boosting, and the same with class weighting.
- **O2.** Compare three feature-ranking methods (ANOVA-F, mutual information, RF importance) at k = 5, 10, 15, 20, 30, 42 features under the same protocol.
- **O3.** Measure what selection and class weighting do to the rare classes (Worms, Backdoor, Analysis), not just to the averages.
- **O4 (phase 2, the "dynamic" angle).** Zero-day test: train with one attack category removed, then measure whether the detector still flags it as an attack. This tests the guide's "dynamic intrusion detection" theme.

## 6. Method

```
official CSVs → drop id → ordinal-encode proto/service/state (fit on train)
             → rank features on train (ANOVA-F | mutual info | RF importance)
             → keep top-k → train classifier → predict test file once
             → accuracy, macro-F1, weighted-F1, detection rate, false-alarm rate,
               per-class recall, fit time, predict time per flow
```

- **Detection rate (DR):** the share of attack flows flagged as any attack.
- **False-alarm rate (FAR):** the share of normal flows flagged as attack.
- Rankings are computed on a 20,000-row stratified sample of the training file, for speed. The final report re-runs them on all rows.
- Seed 42 everywhere, so every number can be reproduced.

Code: `ids/` (see `README.md`). Every number in the synopsis and slides comes from `results/*.csv`.

## 7. Plan

| When | Work | Output |
|---|---|---|
| Days 1–2 | Baselines + feature selection (code done) | Synopsis + first results table |
| Weeks 2–3 | Class weighting, tuning, full-data rankings | Per-class table, best k |
| Weeks 4–5 | Zero-day experiment (O4) | Unseen-attack detection table |
| Week 6 | Report, slides, live demo of `python -m ids.run` | Final submission |

## 8. Risks

- **Rare classes may stay near zero recall** even with weighting. That is still a result: we report it honestly with the per-class table.
- **Data download.** The official site and mirrors may be slow. Download once and keep a copy in Drive.
- **Ordinal encoding of `proto`** (over 100 values) is crude for Logistic Regression. Tree models are unaffected. One-hot encoding is the fallback if LogReg matters.

## References

1. N. Moustafa, J. Slay. *UNSW-NB15: a comprehensive data set for network intrusion detection systems.* MilCIS 2015. Dataset: https://research.unsw.edu.au/projects/unsw-nb15-dataset
2. S. M. Kasongo, Y. Sun. *Performance analysis of intrusion detection systems using a feature selection method on the UNSW-NB15 dataset.* J. Big Data 7, 105 (2020). https://doi.org/10.1186/s40537-020-00379-6
3. Y. Yin et al. *IGRF-RFE: a hybrid feature selection method for MLP-based network intrusion detection on UNSW-NB15 dataset.* J. Big Data 10 (2023). https://doi.org/10.1186/s40537-023-00694-8
4. M. Sarhan et al. *Towards a standard feature set for network intrusion detection system datasets.* arXiv:2101.11315 (2021).
5. T.-T. Nguyen, M. Park. *EL-GNN: a continual-learning-based graph neural network for task-incremental intrusion detection systems.* Electronics 14, 2756 (2025).
