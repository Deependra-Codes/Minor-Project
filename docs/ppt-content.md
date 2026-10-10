# Slide Brief: Minor Project Synopsis Presentation

Give this whole file to the slide-making AI.

## Instructions for the slide AI

- Make **13 slides**, 16:9, clean academic style. White background, one accent color (blue `#2a78d6`), dark grey text. No clip-art, no stock photos.
- Max **5 bullets per slide**, max ~12 words per bullet. The details go in the speaker notes.
- Add **speaker notes** to every slide (3–5 sentences, simple English) so any team member can present it.
- **Do not invent numbers.** Use only the numbers written here. Where a slide says `[FROM results/...]`, leave a clearly marked placeholder box. The team will paste the real numbers and charts there.
- Diagrams: draw the pipeline on slide 7 as boxes and arrows, not as text.

---

## Slide 1: Title

- **Title:** Feature Selection for Network Intrusion Detection: Fewer Features, Same Detection, Visible Rare Attacks
- **Subtitle:** Minor Project, Department of CSE, IIIT Ranchi
- Guide: Dr. Bharat Singh, Assistant Professor, CSE
- Team: `[names, roll numbers]`
- Notes: Introduce the team and the one-line goal: find which network traffic features an intrusion detector really needs.

## Slide 2: The problem

- Cyber-attacks on networks keep growing; a firewall alone is not enough
- An Intrusion Detection System (IDS) watches traffic and flags attacks
- Rule-based IDSs miss new attack variants; ML-based IDSs learn patterns from data
- Two problems: too many features (slow, noisy), and rare attacks get ignored
- Notes: Say that each network connection has dozens of statistics. Using all of them is slow in real time. And because some attacks are very rare, a model can look 90% accurate while missing almost all of them.

## Slide 3: Research question

- On the official UNSW-NB15 split:
- How few features can an IDS keep without losing detection quality?
- Which feature-selection method keeps rare attacks detectable?
- Notes: This is the single question the whole project answers. Everything after this slide serves it.

## Slide 4: Dataset: UNSW-NB15

- Created by UNSW Canberra Cyber Range Lab (Moustafa & Slay, 2015)
- Real normal traffic + synthetic modern attacks; replaces old KDD'99 / NSL-KDD
- Official split: 175,341 training and 82,332 testing records
- 42 features (39 numeric + protocol, service, state); 9 attack types + Normal
- **Table (put on slide):**

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

- Notes: Point at the Worms row: 130 training rows out of 175,341, which is 0.07%. This imbalance is why we never report accuracy alone.

## Slide 5: Literature review

**Table (put on slide):**

| Paper | Method | Result |
|---|---|---|
| Kasongo & Sun, J. Big Data 2020 | XGBoost feature importance + DT/ANN/kNN | DT binary accuracy 88.13% → 90.85% |
| Yin et al., J. Big Data 2023 | IG + RF filter, then RFE with MLP | 42 → 23 features; multiclass 82.25% → 84.24% |
| Sarhan et al., arXiv 2021 | Per-class evaluation | Worms detection only 5.26%, F1 0.09 |
| Nguyen & Park, Electronics 2025 | Graph neural network + continual learning | 96.4% accuracy, but a heavy model |

- Notes: Feature selection is known to help on this dataset. But each paper uses its own protocol and reports one method, and rare classes like Worms are nearly undetected.

## Slide 6: Research gap

- Many papers pool train + test and re-split randomly, which inflates scores
- Accuracy and weighted F1 hide the rare attack classes
- No same-protocol comparison of filter vs embedded feature selection with per-class results
- Notes: Our contribution is a fair, reproducible comparison on the official split, with per-class reporting. "Higher accuracy than everyone" is not the claim.

## Slide 7: Objectives and proposed method

- O1: Strict baselines: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting
- O2: Compare ANOVA-F, Mutual Information, RF importance at k = 5, 10, 15, 20, 30, 42
- O3: Track rare classes (Worms, Backdoor, Analysis) with class weighting
- O4 (phase 2): Zero-day test: hide one attack type in training, check if it is still caught
- **Pipeline diagram (boxes and arrows):** Official CSVs → Drop id, encode protocol/service/state (fit on train) → Rank features on train (3 methods) → Keep top-k → Train classifier → Predict test file once → Metrics
- Notes: Explain "fit on train only". The test file is touched once, so there is no leakage.

## Slide 8: Evaluation metrics

- Macro-F1: every class counts equally, so rare attacks matter
- Detection rate: the share of attacks flagged
- False-alarm rate: the share of normal traffic wrongly flagged
- Per-class recall, plus training time and prediction time per flow
- Notes: An IDS that raises too many false alarms gets switched off by operators, so FAR matters as much as detection.

## Slide 9: First results: baselines

- `[FROM results/results.csv: rows with selection = none. Table: model, accuracy, macro-F1, DR, FAR, for binary and multiclass]`
- `[FROM results/confusion_multiclass.png]`
- Notes: Read out the best model by macro-F1, then show on the confusion matrix which classes the rare attacks get confused with.

## Slide 10: First results: feature selection

- `[FROM results/selection_multiclass.png: macro-F1 vs features kept]`
- `[FROM results/ranking_multiclass.csv: top-10 features of the best method]`
- Notes: State the smallest k whose macro-F1 is within 1 point of all 42 features. That is the headline: "k features give the same detection as 42."

## Slide 11: Rare attack classes

- `[FROM results/per_class_recall_multiclass.csv: recall of Worms, Backdoor, Analysis, Shellcode for each model]`
- Notes: Compare HistGB with HistGB-balanced. If class weighting raises rare-class recall, show it here. If not, say so honestly; that is the next phase of work.

## Slide 12: Timeline

| When | Work |
|---|---|
| Days 1–2 | Baselines + feature selection (done) → synopsis |
| Weeks 2–3 | Class weighting, tuning, full-data rankings |
| Weeks 4–5 | Zero-day / dynamic experiment |
| Week 6 | Report, final slides, live demo |

- Notes: The code is already written and tested, so the remaining weeks go into experiments and analysis.

## Slide 13: References

1. N. Moustafa, J. Slay. UNSW-NB15: a comprehensive data set for network intrusion detection systems. MilCIS 2015.
2. S. M. Kasongo, Y. Sun. Performance analysis of IDS using a feature selection method on the UNSW-NB15 dataset. J. Big Data 7, 105 (2020).
3. Y. Yin et al. IGRF-RFE: a hybrid feature selection method for MLP-based network intrusion detection on UNSW-NB15. J. Big Data 10 (2023).
4. M. Sarhan et al. Towards a standard feature set for network intrusion detection system datasets. arXiv:2101.11315 (2021).
5. T.-T. Nguyen, M. Park. EL-GNN: a continual-learning-based GNN for task-incremental intrusion detection. Electronics 14, 2756 (2025).
