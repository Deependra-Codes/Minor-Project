# Slide Content: Minor Project Presentation

Content only. Each slide lists the exact text, the figure to place, and speaker notes. Layout, colours and fonts are left to whoever designs the deck.

Every number here comes from `results/*.csv`, produced by `python -m ids.run` on the official UNSW-NB15 split. Figures are in `results/` and `docs/assets/`.

---

## Slide 1: Title

- **Title:** Shift-Aware Network Intrusion Detection
- **Subtitle:** Feature selection, label-free adaptation and analyst feedback on the official UNSW-NB15 split
- Minor Project · Department of Computer Science & Engineering · IIIT Ranchi
- Guide: Dr. Bharat Singh, Assistant Professor
- Presented by: [Name, Roll No.] · [Name, Roll No.] · [Name, Roll No.]

**Speaker notes:** Our project asks why intrusion detectors that look accurate still flood analysts with false alarms, and how much of that can be fixed. We answer it on UNSW-NB15, using its official train/test split.

---

## Slide 2: The problem in two numbers

- **Title:** Accurate on paper, noisy in practice
- **Big number 1:** 98.2% of attacks caught by a strong XGBoost detector
- **Big number 2:** 26.2% of normal traffic wrongly flagged as attack by the same detector
- **Line:** Missing all 44 Worms attacks in the test set costs only 0.05% accuracy, so accuracy hides rare attacks

**Speaker notes:** The detector catches almost every attack, but it also flags roughly one normal flow in four. In a real network, that buries the analyst in alerts. The second point is why we never report accuracy alone.

---

## Slide 3: Research questions

- **Title:** Five questions
- **RQ1:** Which of the 42 flow features does a detector actually need?
- **RQ2:** Why does a strong model still fail on the official test set?
- **RQ3:** How much can be recovered without a single test label?
- **RQ4:** How much does a small amount of analyst feedback add?
- **RQ5:** Can the detector catch an attack type it has never seen?

**Speaker notes:** RQ1 is the feature-selection question. RQ2 is diagnosis. RQ3 and RQ4 are the fixes. RQ5 tests the dynamic side of intrusion detection: attacks the model was never trained on.

---

## Slide 4: Dataset

- **Title:** UNSW-NB15: modern attacks, an official train/test split
- **Points:**
  - 175,341 training flows · 82,332 test flows · 42 features per flow
  - 9 attack types + Normal; Worms has only 130 training flows
  - Attacks are 68.1% of the training file but 55.1% of the test file
  - Built at the UNSW Canberra Cyber Range Lab (Moustafa & Slay, 2015)
- **Figure:** `docs/assets/class_distribution.png`

**Speaker notes:** The class mix changes between the two files. That change is a central theme of the project: a deployed detector always meets a different traffic mix than the one it was trained on.

---

## Slide 5: Literature review

- **Title:** Feature selection helps, but rare attacks remain unsolved

| Study | Approach | Reported result |
|---|---|---|
| Kasongo & Sun, 2020 (J. Big Data) | XGBoost feature importance + DT, ANN, kNN, LR, SVM | Decision Tree binary accuracy 88.13% → 90.85% |
| Yin et al., 2023 (J. Big Data) | Information gain + RF filter, then RFE with an MLP | 42 → 23 features; multiclass accuracy 82.25% → 84.24% |
| Sarhan et al., 2021 (arXiv) | Per-class evaluation of NIDS feature sets | Worms detected 5.26% of the time (F1 0.09); Backdoor F1 0.08 |
| Nguyen & Park, 2025 (Electronics) | Graph neural network with continual learning | 96.4% accuracy on UNSW-NB15 |

**Speaker notes:** These studies use different preprocessing and evaluation protocols, so their numbers are not directly comparable with ours. They show two things: feature selection helps, and rare classes like Worms and Backdoor stay nearly undetected.

---

## Slide 6: Research gap

- **Title:** What the studies we reviewed leave open
- **Gap 1:** Some pool the two official files and re-split them at random, which inflates scores
- **Gap 2:** Accuracy and weighted F1 hide the rare attack classes
- **Gap 3:** None separates model error from limits in the data itself
- **Gap 4:** None adapts the detector to the shifted traffic mix at test time

**Speaker notes:** Our contribution follows these gaps: the official protocol, per-class reporting, a measured ceiling, and two adaptation steps.

---

## Slide 7: Methodology

- **Title:** One pipeline that never sees a test label
- **Figure:** `docs/assets/pipeline.png`
- **Steps:**
  1. Load the official CSVs; drop the row id; encode protocol, service and state
  2. Train XGBoost on all 42 features; keep 5-fold out-of-fold predictions on the training file
  3. Rare-class bias: one offset per class, tuned on the out-of-fold predictions to maximise macro-F1
  4. Prior shift: EM estimates the attack share of the unlabelled test traffic and re-weights the model's probabilities
  5. Analyst feedback: 5 rounds, each labelling the 200 flows the model is least sure about, then retraining
  6. Score once, on the test flows nobody labelled

**Speaker notes:** Steps 3 and 4 use no test labels. Step 4 reads only unlabelled test traffic, as a deployed detector would read live traffic. Step 5 is the one place a person helps, and we count every label.

---

## Slide 8: Experimental setup

- **Title:** Setup and metrics
- **Models:** Logistic Regression, Decision Tree, Random Forest, Histogram Gradient Boosting (plain and class-balanced), XGBoost
- **Feature selection:** ANOVA F-test, mutual information, Random-Forest importance; top 5, 10, 15, 20, 30 and all 42 features
- **Tasks:** binary (attack vs normal) and 10-class
- **Metrics:**
  - Detection rate = TP / (TP + FN): the share of attacks caught
  - False-alarm rate = FP / (FP + TN): the share of normal flows flagged
  - Macro-F1 = mean of the per-class F1 scores: every class counts equally
- **Reproducibility:** fixed seed 42 · one command · 29 automated tests · CPU only

**Speaker notes:** Attack is the positive class. We report macro-F1 because it gives Worms the same weight as Normal.

---

## Slide 9: Finding 1: a hard ceiling

- **Title:** Some attacks cannot be told apart from these features
- **Big number:** 93.60%: the highest 10-class accuracy any model can reach on the test file
- **Points:**
  - Many test flows are feature-for-feature identical to flows of another class
  - Share of each class's test flows with such a twin: Analysis 91% · Backdoor 90% · DoS 69% · Exploits 29% · Worms 2%
  - Where twins carry different labels, recall for one class can only rise at the expense of another
  - Worms is different: rare, but almost never identical to another class
- **Figure:** `results/conflict.png`

**Speaker notes:** We computed the best possible classifier: it answers each group of identical flows with the group's majority label. Even that classifier tops out at 93.60% accuracy and 0.765 macro-F1. Binary detection has no such limit: its ceiling is 99.99%.

---

## Slide 10: Finding 2: why the false alarms happen

- **Title:** The detector learned the testbed, and the traffic mix moved
- **Table:**

| Source TTL (sttl) | Attack share in training file | Attack share in test file |
| --- | ---: | ---: |
| 0 | 9.6% | 5.8% |
| 31 | 0.0% | 0.0% |
| 62 | 87.7% | 60.2% |
| 254 | 90.2% | 72.2% |

- **Points:**
  - Source TTL is set by the sending host's operating system and network path, not by the attack; yet two of our three selection methods rank it the most useful feature for attack detection
  - Of 37,000 normal test flows, 9,693 are flagged; 73% of those are read as Fuzzers
  - Among the 10 nearest training flows of each false alarm, 70% are attacks; for correctly passed normal flows, 10%
- **Takeaway:** most false alarms sit where the training file itself says "attack"

**Speaker notes:** This is why a better classifier alone cannot remove these false alarms. The training data labels that region of feature space as attack, while the test data labels it normal. Fixing it needs either the new traffic mix (prior shift) or new labels (analyst feedback).

---

## Slide 11: Results 1: baselines

- **Title:** No single model wins
- **Table (all 42 features, full test file):**

| Model | Binary accuracy | Binary false alarms | 10-class accuracy | 10-class macro-F1 |
| --- | ---: | ---: | ---: | ---: |
| LogReg | 80.44% | 39.8% | 67.19% | 0.319 |
| DecisionTree | 86.38% | 25.1% | 73.35% | 0.490 |
| RandomForest | 87.18% | 26.9% | 75.47% | 0.471 |
| HistGB | 87.31% | 26.6% | 75.97% | 0.452 |
| HistGB-balanced | 91.18% | 15.7% | 67.69% | 0.502 |
| XGBoost | 87.23% | 26.2% | 76.16% | 0.505 |

- **Points:**
  - Binary: class-balanced HistGB is best, with 91.18% accuracy and 15.7% false alarms, and no labels at all
  - 10-class: XGBoost has the best macro-F1 (0.505), so it is the base for the rest of the project; class balancing there raises false alarms to 40.4%

**Speaker notes:** Class balancing makes a model assume a 50/50 traffic mix. The test file is 55.1% attack, far closer to 50/50 than the training file's 68.1%. That single change removes more false alarms than any change of model, which is strong evidence for Finding 2: the traffic mix, not the model, drives the false alarms.

---

## Slide 12: Results 2: feature selection

- **Title:** 5 features do the work of 42
- **Points:**
  - Top 5 features by mutual information: 10-class macro-F1 0.433, accuracy 76.15%
  - All 42 features: macro-F1 0.435 to 0.451, accuracy 75.46% to 76.01% (the spread comes from feature order alone)
  - The 5 features: `sbytes`, `smean`, `sload`, `dbytes`, `dmean`. All describe flow size and rate; none is a TTL field
  - At 5 features the method matters: ANOVA F-test 0.218 · mutual information 0.433 · Random-Forest importance 0.403
- **Figure:** `results/selection_multiclass.png`

**Speaker notes:** Fewer features mean less to collect per flow and a model that is easier to explain. ANOVA's top 5 are all connection counters (`ct_dst_sport_ltm`, `ct_dst_src_ltm`, `ct_srv_dst`, `ct_src_dport_ltm`, `ct_srv_src`), which carry little on their own; mutual information picks features that are informative individually.

---

## Slide 13: Results 3: the improvement

- **Title:** False alarms down, macro-F1 up
- **Table (scored on the 81,332 test flows no analyst labelled):**

| Variant | Binary accuracy | Binary false alarms | 10-class accuracy | 10-class macro-F1 | 10-class false alarms |
| --- | ---: | ---: | ---: | ---: | ---: |
| XGBoost baseline | 87.81% | 25.3% | 76.75% | 0.506 | 23.9% |
| + prior shift (no labels) | 88.51% | 23.4% | 77.89% | 0.509 | 20.7% |
| + rare-class bias (no labels) | 87.81% | 25.3% | 75.10% | 0.544 | 25.6% |
| + prior shift + rare-class bias (no labels) | 88.51% | 23.4% | 76.27% | 0.546 | 22.2% |
| + analyst feedback (1,000 labels) | 91.34% | 18.2% | 80.03% | 0.525 | 19.3% |
| + analyst feedback + prior shift | 91.26% | 18.4% | 80.95% | 0.528 | 16.8% |
| + analyst feedback + prior shift + rare-class bias | 91.26% | 18.4% | 79.40% | 0.575 | 18.4% |

- **Headline, 10-class:** macro-F1 0.506 → 0.575, false alarms 23.9% → 18.4%, accuracy 76.75% → 79.40%
- **Headline, binary:** false alarms 25.3% → 18.4% (27% fewer), accuracy 87.81% → 91.26%
- Cost: 1,000 analyst labels, 1.2% of the test traffic
- **Figure:** `results/feedback.png`

**Speaker notes:** The label-free steps already raise macro-F1 and cut false alarms. Analyst feedback brings the biggest cut in false alarms and the biggest gain in accuracy, because each round asks about the flows the model is least sure of; the rare-class bias brings the biggest gain in macro-F1. Binary false alarms by round: 26.2% → 23.7% → 21.9% → 20.2% → 19.2% → 18.2%. In binary the rare-class bias settles at zero and changes nothing, and the class-balanced model from slide 11 remains the best binary detector without labels.

---

## Slide 14: Results 4: rare classes

- **Title:** Rare attacks become visible
- **Table (10-class recall, baseline vs final):**

| Class | Baseline recall | Final recall |
| --- | ---: | ---: |
| Backdoor | 0.073 | 0.125 |
| Analysis | 0.114 | 0.502 |
| DoS | 0.126 | 0.549 |
| Worms | 0.395 | 0.814 |
| Fuzzers | 0.549 | 0.644 |
| Normal | 0.761 | 0.816 |
| Reconnaissance | 0.815 | 0.810 |
| Shellcode | 0.834 | 0.832 |
| Exploits | 0.841 | 0.619 |
| Generic | 0.973 | 0.977 |

- **Figure:** `results/recall_gain_multiclass.png`

**Speaker notes:** Worms rises from 0.395 to 0.814, Analysis from 0.114 to 0.502, DoS from 0.126 to 0.549. Exploits falls from 0.841 to 0.619: with identical twins across classes (slide 9), raising some classes' recall must lower others'. Backdoor stays low (0.125), as the ceiling predicts.

---

## Slide 15: Results 5: zero-day attacks

- **Title:** Most attack types are caught even when never seen
- **Table (binary detector, one attack type removed from training each time):**

| Attack type held out | Test flows | Detected when seen in training | Detected when never seen |
| --- | ---: | ---: | ---: |
| Fuzzers | 6,062 | 91.6% | 41.3% |
| Analysis | 677 | 96.3% | 93.1% |
| Exploits | 11,132 | 99.5% | 98.3% |
| Shellcode | 378 | 99.5% | 99.5% |
| Reconnaissance | 3,496 | 99.9% | 99.7% |
| DoS | 4,089 | 99.9% | 99.7% |
| Generic | 18,871 | 100.0% | 99.7% |
| Backdoor | 583 | 100.0% | 100.0% |
| Worms | 44 | 100.0% | 100.0% |

- **Point:** 8 of 9 attack types are still detected at 90% or more without a single training example; the hardest is Fuzzers (41.3%)
- **Figure:** `results/zero_day.png` · concept: `docs/assets/zero_day.png`

**Speaker notes:** This is the dynamic-detection test. A detector that only memorised attack signatures would fail here. Most types are still flagged, because they behave unlike normal traffic. Fuzzers is the exception, and it is also what the false alarms are read as (slide 10): it is the attack that looks most like normal traffic.

---

## Slide 16: Conclusion

- **Title:** What this project shows
- The traffic mix drives the false alarms: class balancing alone cuts HistGB's binary false alarms from 26.6% to 15.7%, with no labels
- Some classes have a hard ceiling: most Analysis, Backdoor and DoS test flows have an identical twin in another class; no model passes 93.60% 10-class accuracy
- Final 10-class system: macro-F1 0.506 → 0.575, Worms recall 0.395 → 0.814, false alarms 23.9% → 18.4%
- 5 flow-size and rate features carry almost all the signal of 42

**Speaker notes:** The practical message for a security team: measure the ceiling first, adapt to the traffic you see, and spend analyst time on the flows the model is least sure about.

---

## Slide 17: Limitations and next steps

- **Title:** Limitations and next steps
- One dataset; next is a cross-dataset test, for example CIC-IDS2017
- Analyst feedback is simulated with the true test labels, and its settings (weight 20, 200 flows per round) were fixed by hand
- One split and one seed; feature order alone moves 10-class macro-F1 by about ±0.01
- Next: feedback on top of the class-balanced model, and streaming evaluation where feedback arrives over time

**Speaker notes:** These are honest limits, not hidden ones. Each next step extends the same pipeline.

---

## Slide 18: References

1. N. Moustafa and J. Slay, "UNSW-NB15: A comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set)," in *Proc. MilCIS*, 2015.
2. S. M. Kasongo and Y. Sun, "Performance analysis of intrusion detection systems using a feature selection method on the UNSW-NB15 dataset," *Journal of Big Data*, vol. 7, art. 105, 2020.
3. Y. Yin *et al.*, "IGRF-RFE: A hybrid feature selection method for MLP-based network intrusion detection on UNSW-NB15 dataset," *Journal of Big Data*, vol. 10, 2023.
4. M. Sarhan, S. Layeghy and M. Portmann, "Towards a standard feature set for network intrusion detection system datasets," arXiv:2101.11315, 2021.
5. T.-T. Nguyen and M. Park, "EL-GNN: A continual-learning-based graph neural network for task-incremental intrusion detection systems," *Electronics*, vol. 14, art. 2756, 2025.
6. M. Saerens, P. Latinne and C. Decaestecker, "Adjusting the outputs of a classifier to new a priori probabilities: a simple procedure," *Neural Computation*, vol. 14, no. 1, 2002.
7. T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. ACM SIGKDD*, 2016.
8. B. Settles, "Active learning literature survey," Computer Sciences Technical Report 1648, University of Wisconsin–Madison, 2009.

---

## Slide 19: Thank you

- **Title:** Thank you
- Questions and suggestions are welcome

---

## Viva preparation (for the team, not a slide)

**Why UNSW-NB15 and not NSL-KDD?** NSL-KDD derives from 1998–99 traffic. UNSW-NB15 has modern attacks and an official train/test split.

**Why not deep learning?** The question is which features matter and why the errors happen. Tree ensembles are strong on tabular data, train in minutes on a CPU, and stay explainable.

**Why is class-balanced HistGB so good at binary?** Balancing assumes a 50/50 mix. The test file is 55.1% attack, close to that; the training file is 68.1%. The prior, not the model, is the main cause of the false alarms.

**Is the prior shift cheating?** No. It reads only unlabelled test features, which a deployed detector sees anyway. Test labels are used once, for scoring.

**Is the analyst feedback cheating?** It uses 1,000 test labels, which we count and report, and every score excludes those flows. That is how a detector would be maintained in practice.

**What is the ceiling?** If two flows have identical features but different labels, no model can get both right. Answering each identical group with its majority label gives the best possible score: 93.60% accuracy for 10 classes.

**What is new here?** A measured ceiling, a diagnosis of where the false alarms come from, and two adaptation steps, all under the official protocol.
