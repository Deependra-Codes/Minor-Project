# Slide Content: Minor Project Presentation

Content only. Each slide lists the exact text, the figure to place, and speaker notes. Layout, colours and fonts are left to whoever designs the deck.

Every number here comes from `results/*.csv`, produced by `python -m ids.run` on the official UNSW-NB15 split. Figures are in `results/` and `docs/assets/`.

---

## Slide 1: Title

- **Title:** Shift-Aware Network Intrusion Detection
- **Subtitle:** Feature selection, robustness to a one-byte evasion, and adaptation to traffic shift on the official UNSW-NB15 split
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
- **RQ1:** Which of the 42 flow features does a detector need, and which can an attacker forge?
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
- **Gap 5:** Feature sets are judged on accuracy, never on whether an attacker can forge them

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
- **Reproducibility:** fixed seed 42 · one command · a pytest suite · CPU only

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

**Speaker notes:** We computed the best possible classifier: it answers each group of identical flows with the group's majority label. Even that classifier tops out at $ceil_m_acc accuracy. Its macro-F1 is only $ceil_m_f1_majority, because it maximises accuracy, not macro-F1: the best macro-F1 any classifier can reach lies between $ceil_m_f1_lo and $ceil_m_f1_hi. An earlier draft of this project wrongly called $ceil_m_f1_majority the ceiling. Binary detection has no such limit: its ceiling is $ceil_b_acc.

---

## Slide 10: Finding 1b: the error budget

- **Title:** The data caps two classes; the rest is ours to win
- **Table (best possible F1 per class vs XGBoost, all 42 features, full test file):**

$budget_table

- **Points:**
  - Analysis and Backdoor cannot pass F1 $cap_Analysis and $cap_Backdoor on these features: those losses belong to the data
  - Fuzzers, DoS, Shellcode and Worms could reach F1 $cap_Fuzzers, $cap_DoS, $cap_Shellcode and $cap_Worms, but XGBoost reaches $xf1_Fuzzers, $xf1_DoS, $xf1_Shellcode and $xf1_Worms: those gaps come from the model and the traffic shift, not from twins
- **Footnote:** each class's best F1 is reached on its own; they cannot all be reached at once

**Speaker notes:** This turns the ceiling into a to-do list. Where the gap is small, no method can help. Where it is large, it is worth working on, and the next slides go after exactly those classes.

---

## Slide 11: Finding 2: why the false alarms happen

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

## Slide 12: Finding 3: one byte blinds the detector

- **Title:** One header byte decides most verdicts
- **Figure:** `results/ttl_sweep.png`
- **Points:**
  - Rewriting the source TTL of every attack flow to $ttl_mode, the TTL of $ttl_mode_share of normal training flows, drops XGBoost detection from $xgb_clean_dr to $xgb_mode_dr, and class-balanced HistGB from $hgb_clean_dr to $hgb_mode_dr; no attack type stays above $mode_max_type
  - It is not about one value. The sweep over all 256 source TTLs shows three bands:
    - every TTL from 0 to $sweep_below: at most $sweep_xgb_max of attacks detected (XGBoost), $sweep_hgb_max (HistGB)
    - the testbed's own attack TTLs ($attack_ttls): at least $sweep_xgb_hosts (XGBoost), $sweep_hgb_hosts (HistGB)
    - every other TTL above $sweep_cut: $sweep_xgb_rest (XGBoost), $sweep_hgb_rest (HistGB)
  - So the all-feature models lean on which TTLs the testbed's attack machines used: the 39 other features, left untouched by the rewrite, detect $nottl_dr of attacks on their own (slide 15)
  - The other normal TTLs from the same training rule: $ttl_other
  - Source TTL is the top pro-attack feature for $fa_sttl_share of the $fa_count false alarms; $fa_host_share of them carry an attack-host TTL ($attack_ttls)
- **Footnote:** feature-space simulation: recorded flows are edited, no traffic is regenerated; an attacker sets the initial TTL, while the TTL seen at a sensor also depends on the hop count. `ct_state_ttl`, which UNSW-NB15 derives from the connection state and both TTLs, is re-derived after every edit by a rule learned from the training file (it reproduces $ct_match of the test file's values), so every edited flow is one the feature extractor could produce

**Speaker notes:** Flood et al. (EuroS&P 2024) report that UNSW-NB15's gap between benign and attack traffic comes partly from the TTL and protocol choices in its design; we could not access their full text, so we claim only our own measurements. What we add is the size of the effect on a real detector: one byte the attacker controls hides almost every attack, and the same byte drives the false alarms of slide 11.

---

## Slide 13: Results 1: baselines

- **Title:** No single model wins
- **Table (all 42 features, full test file):**

$baseline_table

- **Points:**
  - Binary: class-balanced HistGB is best, with $hgb_b_acc accuracy and $hgb_b_far false alarms, and no labels at all
  - 10-class: XGBoost has the best macro-F1 ($xgb_m_f1), so it is the base for the rest of the project; class balancing there raises false alarms to $hgb_m_far

**Speaker notes:** Class balancing makes a model assume a 50/50 traffic mix. The test file is $attack_test attack, far closer to 50/50 than the training file's $attack_train. That single change removes more false alarms than any change of model, which is strong evidence for Finding 2: the traffic mix, not the model, drives the false alarms.

---

## Slide 14: Results 2: feature selection

- **Title:** $fs_k features do the work of $fs_n_full
- **Points:**
  - Top $fs_k features by $fs_method: 10-class macro-F1 $fs_k_f1, accuracy $fs_k_acc
  - All $fs_n_full features: macro-F1 $full_f1_lo to $full_f1_hi, accuracy $full_acc_lo to $full_acc_hi (the spread comes from feature order alone)
  - The $fs_k features: $fs_top. All describe flow size and rate; none is a TTL field
  - At $fs_k features the method matters: $fs_k_all
- **Figure:** `results/selection_multiclass.png`

**Speaker notes:** Fewer features mean less to collect per flow and a model that is easier to explain. ANOVA's top $fs_k are all connection counters ($anova_top), which carry little on their own; mutual information picks features that are informative individually.

---

## Slide 15: Results 2b: feature selection for robustness

- **Title:** Dropping three TTL fields buys robustness, not fewer false alarms
- **Table (binary XGBoost unless stated, full test file):**

$robust_table

- **Points:**
  - Without the three TTL fields the detector is immune to the TTL rewrite by construction; the forgery rows show what an attacker would have to forge instead
  - False alarms do not fall ($far_all with TTL, $far_nottl without): the other 39 features still recognise the testbed's attack hosts (AUC $proxy_auc)
  - Without TTL, $far_nottl_hosts of normal flows that carry an attack-host TTL are flagged, against $far_nottl_rest of the other normal flows

**Speaker notes:** Feature selection is usually judged on accuracy alone. Here the question is what an attacker can forge. Removing TTL costs little and removes the one-byte evasion, but it does not remove the false alarms, because the testbed's fingerprint is spread across many features. Like the baseline table, this table scores all 82,332 test flows; the improvement ladder scores only the $eval_rows flows no analyst labelled, which is why the same XGBoost baseline reads $far_all here and $b_base_far there.

---

## Slide 16: Results 3: the improvement

- **Title:** False alarms down, macro-F1 up
- **Table (scored on the $eval_rows test flows no analyst labelled):**

$ladder_table

- **Headline, 10-class:** macro-F1 $m_base_f1 → $m_fb_f1, false alarms $m_base_far → $m_fb_far, accuracy $m_base_acc → $m_fb_acc
- **Headline, binary:** false alarms $b_base_far → $b_fb_far ($b_far_cut fewer), accuracy $b_base_acc → $b_fb_acc
- Cost: $labels_used analyst labels, $label_share of the test traffic
- **Figure:** `results/feedback.png`

**Speaker notes:** The label-free steps already raise macro-F1 and cut false alarms. Analyst feedback brings the biggest cut in false alarms and the biggest gain in accuracy, because each round asks about the flows the model is least sure of; the rare-class bias brings the biggest gain in macro-F1. Binary false alarms by round: $curve_points. In binary the rare-class bias settles at zero and changes nothing, and the class-balanced model from slide 13 remains the best binary detector without labels.

---

## Slide 17: Results 4: rare classes

- **Title:** Rare attacks become visible
- **Table (10-class recall, baseline vs final):**

$gain_table

- **Figure:** `results/recall_gain_multiclass.png`

**Speaker notes:** Worms rises from $g_Worms_base to $g_Worms_final, Analysis from $g_Analysis_base to $g_Analysis_final, DoS from $g_DoS_base to $g_DoS_final. Exploits falls from $g_Exploits_base to $g_Exploits_final: with identical twins across classes (slide 9), raising some classes' recall must lower others'. Backdoor stays low ($g_Backdoor_final), as the ceiling predicts.

---

## Slide 18: Results 5: zero-day attacks

- **Title:** Most attack types are caught even when never seen
- **Table (binary detector, one attack type removed from training each time):**

$zero_table

- **Point:** $zero_n_high of 9 attack types are still detected at 90% or more without a single training example; the hardest is $zero_worst ($zero_worst_v)
- **Figure:** `results/zero_day.png` · concept: `docs/assets/zero_day.png`

**Speaker notes:** This is the dynamic-detection test. A detector that only memorised attack signatures would fail here. Most types are still flagged, because they behave unlike normal traffic. Fuzzers is the exception, and it is also what the false alarms are read as (slide 11): it is the attack that looks most like normal traffic.

---

## Slide 19: Conclusion

- **Title:** What this project shows
- The traffic mix drives the false alarms: class balancing alone cuts HistGB's binary false alarms from $hgb_plain_b_far to $hgb_b_far, with no labels
- Some classes have a hard ceiling: no model passes $ceil_m_acc 10-class accuracy or about $ceil_m_f1_hi macro-F1, and Analysis and Backdoor are capped near F1 $cap_Analysis
- One header byte decides most verdicts: rewriting the source TTL hides all but $xgb_mode_dr of attacks from XGBoost; a 39-feature detector without TTL resists it at little cost
- Final 10-class system: macro-F1 $m_base_f1 → $m_fb_f1, Worms recall $g_Worms_base → $g_Worms_final, false alarms $m_base_far → $m_fb_far
- $fs_k flow-size and rate features carry almost all the signal of $fs_n_full

**Speaker notes:** The practical message for a security team: measure the ceiling first, adapt to the traffic you see, and spend analyst time on the flows the model is least sure about.

---

## Slide 20: Limitations and next steps

- **Title:** Limitations and next steps
- One dataset; next is a cross-dataset test, for example CIC-IDS2017
- Analyst feedback is simulated with the true test labels, and its settings (weight 20, 200 flows per round) were fixed by hand
- One split and one seed; feature order alone moves 10-class macro-F1 by about ±0.01
- The TTL rewrite is a feature-space simulation, and the forgery test changes at most two features without checking that the forged flow still works as an attack
- Some design choices (the TTL rule, the round size) were made after earlier looks at the test file
- Next, for the major project: feedback on top of the class-balanced model, a drift alarm on real traffic streams, constrained adversarial flows, and a second dataset such as NSL-KDD or CIC-IDS2017

**Speaker notes:** These are honest limits, not hidden ones. Each next step extends the same pipeline.

---

## Slide 21: References

1. N. Moustafa and J. Slay, "UNSW-NB15: A comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set)," in *Proc. MilCIS*, 2015.
2. S. M. Kasongo and Y. Sun, "Performance analysis of intrusion detection systems using a feature selection method on the UNSW-NB15 dataset," *Journal of Big Data*, vol. 7, art. 105, 2020.
3. Y. Yin *et al.*, "IGRF-RFE: A hybrid feature selection method for MLP-based network intrusion detection on UNSW-NB15 dataset," *Journal of Big Data*, vol. 10, 2023.
4. M. Sarhan, S. Layeghy and M. Portmann, "Towards a standard feature set for network intrusion detection system datasets," arXiv:2101.11315, 2021.
5. T.-T. Nguyen and M. Park, "EL-GNN: A continual-learning-based graph neural network for task-incremental intrusion detection systems," *Electronics*, vol. 14, art. 2756, 2025.
6. M. Saerens, P. Latinne and C. Decaestecker, "Adjusting the outputs of a classifier to new a priori probabilities: a simple procedure," *Neural Computation*, vol. 14, no. 1, 2002.
7. T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. ACM SIGKDD*, 2016.
8. B. Settles, "Active learning literature survey," Computer Sciences Technical Report 1648, University of Wisconsin–Madison, 2009.
9. R. Flood, G. Engelen, D. Aspinall *et al.*, "Bad design smells in benchmark NIDS datasets," in *Proc. IEEE European Symposium on Security and Privacy (EuroS&P)*, 2024, pp. 658–675.

---

## Slide 22: Thank you

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

**Is the TTL finding new?** The TTL artefact in UNSW-NB15 is known (Flood et al., 2024). What we add is the measured evasion on the official split, the attribution of the false alarms, and the measured cost of a detector without TTL.

**What is new here?** A corrected ceiling with a per-class error budget, a one-byte evasion test with its fix, a diagnosis of where the false alarms come from, and two adaptation steps, all under the official protocol.
