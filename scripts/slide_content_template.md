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
- **Big number 1:** $xgb_b_dr of attacks caught by a strong XGBoost detector
- **Big number 2:** $xgb_b_far of normal traffic wrongly flagged as attack by the same detector
- **Line:** Missing all $worms_test Worms attacks in the test set costs only $worms_cost accuracy, so accuracy hides rare attacks

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
  - Attacks are $attack_train of the training file but $attack_test of the test file
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
- **Big number:** $ceil_m_acc: the highest 10-class accuracy any model can reach on the test file
- **Points:**
  - Many test flows are feature-for-feature identical to flows of another class
  - Share of each class's test flows with such a twin: Analysis $conf_Analysis · Backdoor $conf_Backdoor · DoS $conf_DoS · Exploits $conf_Exploits · Worms $conf_Worms
  - Where twins carry different labels, recall for one class can only rise at the expense of another
  - Worms is different: rare, but almost never identical to another class
- **Figure:** `results/conflict.png`

**Speaker notes:** We computed the best possible classifier: it answers each group of identical flows with the group's majority label. Even that classifier tops out at $ceil_m_acc accuracy and $ceil_m_f1 macro-F1. Binary detection has no such limit: its ceiling is $ceil_b_acc.

---

## Slide 10: Finding 2: why the false alarms happen

- **Title:** The detector learned the testbed, and the traffic mix moved
- **Table:**

$ttl_table

- **Points:**
  - Source TTL is set by the sending host's operating system and network path, not by the attack; yet two of our three selection methods rank it the most useful feature for attack detection
  - Of $normal_count normal test flows, $fa_count are flagged; $fa_read_share of those are read as $fa_read_as
  - Among the 10 nearest training flows of each false alarm, $fa_nb are attacks; for correctly passed normal flows, $ok_nb
- **Takeaway:** most false alarms sit where the training file itself says "attack"

**Speaker notes:** This is why a better classifier alone cannot remove these false alarms. The training data labels that region of feature space as attack, while the test data labels it normal. Fixing it needs either the new traffic mix (prior shift) or new labels (analyst feedback).

---

## Slide 11: Results 1: baselines

- **Title:** No single model wins
- **Table (all 42 features, full test file):**

$baseline_table

- **Points:**
  - Binary: class-balanced HistGB is best, with $hgb_b_acc accuracy and $hgb_b_far false alarms, and no labels at all
  - 10-class: XGBoost has the best macro-F1 ($xgb_m_f1), so it is the base for the rest of the project; class balancing there raises false alarms to $hgb_m_far

**Speaker notes:** Class balancing makes a model assume a 50/50 traffic mix. The test file is $attack_test attack, far closer to 50/50 than the training file's $attack_train. That single change removes more false alarms than any change of model, which is strong evidence for Finding 2: the traffic mix, not the model, drives the false alarms.

---

## Slide 12: Results 2: feature selection

- **Title:** $fs_k features do the work of $fs_n_full
- **Points:**
  - Top $fs_k features by $fs_method: 10-class macro-F1 $fs_k_f1, accuracy $fs_k_acc
  - All $fs_n_full features: macro-F1 $full_f1_lo to $full_f1_hi, accuracy $full_acc_lo to $full_acc_hi (the spread comes from feature order alone)
  - The $fs_k features: $fs_top. All describe flow size and rate; none is a TTL field
  - At $fs_k features the method matters: $fs_k_all
- **Figure:** `results/selection_multiclass.png`

**Speaker notes:** Fewer features mean less to collect per flow and a model that is easier to explain. ANOVA's top $fs_k are all connection counters ($anova_top), which carry little on their own; mutual information picks features that are informative individually.

---

## Slide 13: Results 3: the improvement

- **Title:** False alarms down, macro-F1 up
- **Table (scored on the $eval_rows test flows no analyst labelled):**

$ladder_table

- **Headline, 10-class:** macro-F1 $m_base_f1 → $m_fb_f1, false alarms $m_base_far → $m_fb_far, accuracy $m_base_acc → $m_fb_acc
- **Headline, binary:** false alarms $b_base_far → $b_fb_far ($b_far_cut fewer), accuracy $b_base_acc → $b_fb_acc
- Cost: $labels_used analyst labels, $label_share of the test traffic
- **Figure:** `results/feedback.png`

**Speaker notes:** The label-free steps already raise macro-F1 and cut false alarms. Analyst feedback brings the biggest cut in false alarms and the biggest gain in accuracy, because each round asks about the flows the model is least sure of; the rare-class bias brings the biggest gain in macro-F1. Binary false alarms by round: $curve_points. In binary the rare-class bias settles at zero and changes nothing, and the class-balanced model from slide 11 remains the best binary detector without labels.

---

## Slide 14: Results 4: rare classes

- **Title:** Rare attacks become visible
- **Table (10-class recall, baseline vs final):**

$gain_table

- **Figure:** `results/recall_gain_multiclass.png`

**Speaker notes:** Worms rises from $g_Worms_base to $g_Worms_final, Analysis from $g_Analysis_base to $g_Analysis_final, DoS from $g_DoS_base to $g_DoS_final. Exploits falls from $g_Exploits_base to $g_Exploits_final: with identical twins across classes (slide 9), raising some classes' recall must lower others'. Backdoor stays low ($g_Backdoor_final), as the ceiling predicts.

---

## Slide 15: Results 5: zero-day attacks

- **Title:** Most attack types are caught even when never seen
- **Table (binary detector, one attack type removed from training each time):**

$zero_table

- **Point:** $zero_n_high of 9 attack types are still detected at 90% or more without a single training example; the hardest is $zero_worst ($zero_worst_v)
- **Figure:** `results/zero_day.png` · concept: `docs/assets/zero_day.png`

**Speaker notes:** This is the dynamic-detection test. A detector that only memorised attack signatures would fail here. Most types are still flagged, because they behave unlike normal traffic. Fuzzers is the exception, and it is also what the false alarms are read as (slide 10): it is the attack that looks most like normal traffic.

---

## Slide 16: Conclusion

- **Title:** What this project shows
- The traffic mix drives the false alarms: class balancing alone cuts HistGB's binary false alarms from $hgb_plain_b_far to $hgb_b_far, with no labels
- Some classes have a hard ceiling: most Analysis, Backdoor and DoS test flows have an identical twin in another class; no model passes $ceil_m_acc 10-class accuracy
- Final 10-class system: macro-F1 $m_base_f1 → $m_fb_f1, Worms recall $g_Worms_base → $g_Worms_final, false alarms $m_base_far → $m_fb_far
- $fs_k flow-size and rate features carry almost all the signal of $fs_n_full

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

**Why is class-balanced HistGB so good at binary?** Balancing assumes a 50/50 mix. The test file is $attack_test attack, close to that; the training file is $attack_train. The prior, not the model, is the main cause of the false alarms.

**Is the prior shift cheating?** No. It reads only unlabelled test features, which a deployed detector sees anyway. Test labels are used once, for scoring.

**Is the analyst feedback cheating?** It uses $labels_used test labels, which we count and report, and every score excludes those flows. That is how a detector would be maintained in practice.

**What is the ceiling?** If two flows have identical features but different labels, no model can get both right. Answering each identical group with its majority label gives the best possible score: $ceil_m_acc accuracy for 10 classes.

**What is new here?** A measured ceiling, a diagnosis of where the false alarms come from, and two adaptation steps, all under the official protocol.
