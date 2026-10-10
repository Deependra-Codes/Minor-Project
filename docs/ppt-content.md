# Slide Brief: Synopsis Presentation (v2)

Give this whole file to the slide-making AI.

## Rules for the slide AI

1. Use every **On slide** line **verbatim**. Do not paraphrase. Do not add bullets, numbers, emojis or filler.
2. Follow the **Design system** exactly. Each slide has one visual anchor, described under **Visual**.
3. Put each **Speaker notes** block into that slide's notes field.
4. Slides 11 and 12 are **result frames**. Draw the empty table grid and chart area with the label *"Inserted from results/ after the run"*. Do not fill in numbers.
5. 16 slides, no more and no fewer.

---

## Design system

**Canvas.** 16:9 (13.33 × 7.5 in), 0.6 in margins, 12-column grid. Everything aligns to the grid.

**Type.**

| Role | Font | Size |
|---|---|---|
| Kicker (label above title) | Inter SemiBold, ALL CAPS, letter-spacing 1.5 pt, Blue | 12 pt |
| Slide title (a full-sentence takeaway) | Montserrat SemiBold, Navy | 28 pt |
| Body | Inter Regular, Ink | 18 pt |
| Tables | Inter, tabular figures | 14 pt |
| Captions, footer, sources | Inter, Muted | 10 pt |

Use Calibri if Inter or Montserrat is missing. Nothing goes below 10 pt.

**Color.**

| Token | Hex | Use |
|---|---|---|
| Navy | `#0B1F3A` | Title and closing backgrounds, titles, diagram outlines |
| Blue | `#2A78D6` | Main accent: key numbers, chart bars, pipeline boxes |
| Orange | `#EB6834` | **Reserved for rare attacks and the problem.** At most once per slide |
| Ink | `#1F1F1E` | Body text |
| Muted | `#6B6A64` | Captions, footer, axis labels |
| Line | `#E4E3DF` | Dividers, table rules, chart grid |
| Surface | `#F5F7FA` | Card fill |
| White | `#FFFFFF` | Content slide background |

**Components.**
- **Card:** Surface fill, 8 px corner radius, 0.25 in padding, no shadow, no border.
- **Table:** bold Navy header on Surface, 1 px Line row dividers, no vertical lines, numbers right-aligned.
- **Chart:** flat, no 3D, no gradients, no shadows. Axis and grid in Line, direct value labels, no legend box when labels suffice.
- **Icons:** one outline set (Lucide or Phosphor), 1.5 px stroke, Navy. At most 4 per slide.
- **Footer** (content slides): left "IIIT Ranchi · CSE · Minor Project 2026", right "n / 16", Muted 10 pt.
- **Bullets:** at most 4 per slide, no trailing full stops, never two lines of the same idea.

**Avoid:** clip-art, stock photos, WordArt, drop shadows, gradients, animated transitions (a simple fade is fine), centred body text.

---

## Slide 1: Title

**Layout:** Navy full-bleed. Text left-aligned on the left 8 columns. A thin vertical Blue rule beside the title.

**On slide**
- Kicker: MINOR PROJECT · SYNOPSIS
- Title: Feature Selection for Network Intrusion Detection
- Subtitle: Fewer features, full detection, evaluated on the official UNSW-NB15 split
- Department of Computer Science & Engineering, IIIT Ranchi
- Guide: Dr. Bharat Singh, Assistant Professor
- Presented by: [Name, Roll No.] · [Name, Roll No.] · [Name, Roll No.]
- October 2026

**Speaker notes**
Good morning. Our project asks a practical question: how little information does an intrusion detector need to do its job well, and what happens to the rarest attacks when we give it less? We study this on UNSW-NB15, a modern benchmark, using its official train and test split.

---

## Slide 2: Motivation

**Layout:** two columns. Left (5 cols): a big-number block. Right (7 cols): three bullets.

**Visual:** the number **0.05%** in Orange at 96 pt, caption below in Muted.

**On slide**
- Kicker: MOTIVATION
- Title: High accuracy can hide a blind spot
- Big number: 0.05%
- Caption: accuracy lost by a detector that misses every Worms attack in the UNSW-NB15 test set (44 of 82,332 records)
- Bullets:
  - An intrusion detector must judge every network flow, in real time
  - Machine-learning detectors learn attack patterns from labelled traffic
  - Accuracy is dominated by common traffic, so rare attacks can vanish from view
- Source line: Computed from the official test-set class counts

**Speaker notes**
This one number is the motivation for the whole project. A model can ignore an entire attack category and its accuracy barely moves, because that category is tiny. So a detector can look excellent on paper and still be blind to exactly the attacks that matter.

---

## Slide 3: Problem statement and research questions

**Layout:** two Cards side by side on top (problems); three numbered rows below (questions), with RQ numbers in Blue.

**On slide**
- Kicker: PROBLEM STATEMENT
- Title: Two problems, three questions
- Card 1, heading **Feature overload**: Every flow carries 42 features. Many are redundant, and each one adds cost at detection time
- Card 2, heading **Rare-attack blindness** (heading in Orange): Four attack types make up under 3% of the training data and are routinely misclassified
- RQ1: How many of the 42 features does a detector actually need?
- RQ2: Which selection method keeps detection highest: ANOVA-F, Mutual Information, or Random-Forest importance?
- RQ3: What does feature selection do to the rarest attack classes?

**Speaker notes**
The four rare types are Analysis, Backdoor, Shellcode and Worms: 5,009 of 175,341 training records, or 2.86%. Our three research questions follow directly from these two problems, and every experiment answers one of them.

---

## Slide 4: Dataset

**Layout:** left (5 cols) a 2 × 2 grid of stat tiles; right (7 cols) a horizontal bar chart. Footnote across the bottom.

**Visual:** horizontal bars of training records per class, sorted descending, **log-scale** x-axis, Blue bars, the Worms bar in Orange, a value label at each bar end. Callout near the Worms bar: "Normal : Worms = 431 : 1".

Chart data (training set):

| Class | Records |
|---|---:|
| Normal | 56,000 |
| Generic | 40,000 |
| Exploits | 33,393 |
| Fuzzers | 18,184 |
| DoS | 12,264 |
| Reconnaissance | 10,491 |
| Analysis | 2,000 |
| Backdoor | 1,746 |
| Shellcode | 1,133 |
| Worms | 130 |

**On slide**
- Kicker: DATASET
- Title: UNSW-NB15: modern attacks, an official train/test split
- Tile 1: **175,341** training records
- Tile 2: **82,332** testing records
- Tile 3: **42** flow features
- Tile 4: **9** attack types + Normal
- Footnote: Built at the UNSW Canberra Cyber Range Lab (Moustafa & Slay, 2015) to replace the outdated KDD'99 and NSL-KDD benchmarks

**Speaker notes**
UNSW-NB15 mixes real normal traffic with modern synthetic attacks. Its official split is harder than a random one: attacks are 68.1% of the training file but only 55.1% of the test file, so a model has to generalise, not memorise. Note the log scale: Worms has 130 records against 56,000 Normal.

---

## Slide 5: Literature review

**Layout:** full-width table. Limitation column in Muted.

**On slide**
- Kicker: LITERATURE REVIEW
- Title: Feature selection helps, but rare attacks remain unsolved

| Study | Approach | Key result | Limitation |
|---|---|---|---|
| Kasongo & Sun, 2020 (J. Big Data) | XGBoost feature importance with DT, ANN, kNN, LR, SVM | Decision Tree binary accuracy 88.13% → 90.85% | One selection method |
| Yin et al., 2023 (J. Big Data) | Information gain + RF filter, then RFE with an MLP | 42 → 23 features; multiclass accuracy 82.25% → 84.24% | One pipeline, tied to one classifier |
| Sarhan et al., 2021 (arXiv) | Per-class evaluation of intrusion-detection feature sets | Worms detected 5.26% of the time (F1 0.09); Backdoor F1 0.08 | Its remedy re-extracts features as NetFlow |
| Nguyen & Park, 2025 (Electronics) | Graph neural network with continual learning | 96.4% accuracy on UNSW-NB15 | Heavy model; needs flow-graph construction |

**Speaker notes**
Two lessons. First, feature selection works: Yin et al. cut 45% of the features and gained accuracy. Second, the rare classes are still failing: Sarhan et al. report that Worms is caught about one time in twenty. Each study also uses its own method and protocol, which brings us to the gap.

---

## Slide 6: Research gap

**Layout:** three equal Cards in a row, each with an icon, a number (1, 2, 3 in Blue) and a heading.

**On slide**
- Kicker: RESEARCH GAP
- Title: Three gaps this project closes
- Card 1, **Incomparable protocols**: Many studies pool the two official files and re-split them at random, which inflates scores
- Card 2, **Averages hide rare attacks**: Accuracy and weighted F1 are dominated by three classes that hold 74% of the training data
- Card 3, **No head-to-head comparison**: In the studies reviewed, filter and embedded selection methods are never compared under one protocol with per-class results

**Speaker notes**
For example, one 2026 study states that it pools the official partitions and evaluates on a fresh 80/20 split, so its numbers cannot be compared with official-split results. The three classes in card 2 are Normal, Generic and Exploits. Our contribution is not a bigger model. It is a fair, reproducible comparison that makes the rare classes visible.

---

## Slide 7: Objectives

**Layout:** four rows. Each row: an icon, a bold label in Navy, then one line of text. Thin Line dividers between rows.

**On slide**
- Kicker: OBJECTIVES
- Title: What this project will deliver
- **O1 · Reproducible baselines:** five classifiers on the official split, never re-split
- **O2 · Fair comparison:** three selection methods, 5 to 42 features, one fixed protocol
- **O3 · Rare-attack analysis:** per-class recall for every model, with and without class weighting
- **O4 · Toward dynamic detection:** a leave-one-attack-out test for unseen, zero-day attacks

**Speaker notes**
O1 to O3 answer our three research questions. O4 is the second phase: it tests whether a detector trained on known attacks can still flag a new one, which is the core challenge of dynamic intrusion detection.

---

## Slide 8: Methodology

**Layout:** six boxes left to right with arrows (Blue outline, white fill, Navy text), each with a one-line caption beneath. A Navy bracket under boxes 2–5 labelled "fitted on training data only".

**On slide**
- Kicker: PROPOSED METHODOLOGY
- Title: One pipeline, fitted on training data only
- Box 1, **Official CSVs:** 175,341 train · 82,332 test
- Box 2, **Preprocess:** drop row id; encode protocol, service, state
- Box 3, **Rank features:** ANOVA-F · Mutual Information · RF importance
- Box 4, **Select top-k:** k = 5, 10, 15, 20, 30, 42
- Box 5, **Train classifier:** LR · DT · RF · HistGB, with and without class weights
- Box 6, **Evaluate once:** on the untouched test file

**Speaker notes**
The key design rule is in the bracket. Every step that learns anything (the encoders, the feature rankings, the models) sees only training data. The test file is used once, at the end. This rules out data leakage, which is the most common reason published IDS numbers look better than they are.

---

## Slide 9: Techniques

**Layout:** left (7 cols) three stacked Cards for the selection methods; right (5 cols) a two-column table of classifiers.

**On slide**
- Kicker: TECHNIQUES
- Title: Three ways to rank a feature, five ways to classify
- Card, **ANOVA F-test · Filter:** scores how strongly a feature's mean differs between classes. Fast; captures linear separation
- Card, **Mutual Information · Filter:** measures any dependency between a feature and the class, including non-linear ones
- Card, **Random-Forest Importance · Embedded:** credits the features that most reduce impurity across 200 trees; captures interactions

| Classifier | Role |
|---|---|
| Logistic Regression | Linear baseline |
| Decision Tree | Interpretable rules |
| Random Forest | Bagged ensemble, 200 trees |
| Histogram Gradient Boosting | Boosted ensemble, fast on large tables |
| HistGB + class weights | Imbalance-aware variant |

**Speaker notes**
Filter methods judge each feature on its own, before any model is trained. The embedded method judges features by how a model actually uses them. Comparing the two families under the same protocol is exactly the gap from slide 6.

---

## Slide 10: Evaluation

**Layout:** left (6 cols) three formulas typeset with the equation editor, each with a Muted caption; right (6 cols) a two-column setup table.

**On slide**
- Kicker: EVALUATION
- Title: Measured the way a security operator would judge it
- Detection Rate = TP / (TP + FN). Caption: share of attacks caught
- False Alarm Rate = FP / (FP + TN). Caption: share of normal traffic wrongly flagged
- Macro-F1 = (1/C) · Σ F1꜀. Caption: every class weighs the same, rare or common

| Setting | Choice |
|---|---|
| Split | Official train/test, never re-split |
| Tasks | Binary (attack vs normal) and 10-class |
| Fitting | Encoders, rankings and models on training data only |
| Reproducibility | Fixed seed 42 · one command · 18 automated tests |
| Stack | Python, scikit-learn, pandas, matplotlib · CPU only |

**Speaker notes**
Here an attack is the positive class. Detection rate alone is not enough: a detector that raises too many false alarms gets switched off by the people running it. Macro-F1 is our headline metric because it gives Worms the same weight as Normal traffic.

---

## Slide 11: Results I, baselines (result frame)

**Layout:** left (7 cols) table frame; right (5 cols) image frame.

**On slide**
- Kicker: RESULTS · BASELINES
- Title: *(written after the run, in this form)* "[Best model] reaches [macro-F1] macro-F1 using all 42 features"
- Table frame with columns: Model · Accuracy · Macro-F1 · Detection Rate · False Alarm Rate. Two blocks, **Binary** and **10-class**, five rows each (LR, DT, RF, HistGB, HistGB + class weights)
- Image frame: confusion matrix (10-class), labelled "results/confusion_multiclass.png"
- Source line: results/results.csv, rows where selection = none

**Speaker notes**
*(Written after the run.)* Name the best model, read its macro-F1, and point to the confusion matrix row where a rare class leaks into a common one.

---

## Slide 12: Results II, feature selection (result frame)

**Layout:** left (7 cols) chart frame; right (5 cols) two stacked frames.

**On slide**
- Kicker: RESULTS · FEATURE SELECTION
- Title: *(written after the run, in this form)* "[k] features match the full 42-feature macro-F1 within one point"
- Chart frame: macro-F1 against features kept, one line per method, labelled "results/selection_multiclass.png"
- Frame 1: top 10 features of the best method, labelled "results/ranking_multiclass.csv"
- Frame 2: recall of Worms, Backdoor, Analysis and Shellcode, HistGB vs HistGB + class weights, labelled "results/per_class_recall_multiclass.csv"

**Speaker notes**
*(Written after the run.)* State the smallest k that holds macro-F1 within one point of the full set, which method found it, and what happened to the four rare classes.

---

## Slide 13: Next phase, dynamic detection

**Layout:** left (6 cols) a diagram: nine rounded "chips", one per attack type. One chip (Worms) is greyed, with a dashed outline labelled "held out of training", and an arrow leads to a box "Test: is it flagged as an attack?". Right (6 cols) three bullets.

**On slide**
- Kicker: NEXT PHASE
- Title: Can the detector catch an attack it has never seen?
- Leave-one-attack-out: train without one attack type, then test on it
- Repeat for all nine attack types
- Report an unseen-attack detection rate for each

**Speaker notes**
Real networks face attacks that were not in any training set. This experiment simulates that directly. If a lean, feature-selected detector still flags unseen attack types, that is strong evidence it learned general attack behaviour rather than memorising signatures.

---

## Slide 14: Plan and expected outcomes

**Layout:** left (7 cols) a four-row Gantt chart over weeks 1–6, Blue bars; the week-1 bar filled solid with the label "code complete". Right (5 cols) four outcome bullets.

**On slide**
- Kicker: PLAN
- Title: Six weeks from synopsis to final demo
- Gantt rows:
  - Week 1: Baselines and feature selection
  - Weeks 2–3: Class weighting, tuning, full-data rankings
  - Weeks 4–5: Leave-one-attack-out experiment
  - Week 6: Report, final presentation, live demo
- Expected outcomes:
  - The smallest feature subset that matches full-feature detection
  - A ranked list of the features that matter, and why
  - A per-class picture of rare-attack detection
  - An open, tested pipeline anyone can rerun with one command

**Speaker notes**
The pipeline is already written and tested, so the remaining weeks go into experiments and analysis, not setup. Every number in the final report will be regenerated by one command from the committed code.

---

## Slide 15: References

**Layout:** numbered list, 12 pt, hanging indent.

**On slide**
- Kicker: REFERENCES
- Title: References
1. N. Moustafa and J. Slay, "UNSW-NB15: A comprehensive data set for network intrusion detection systems (UNSW-NB15 network data set)," in *Proc. Military Communications and Information Systems Conf. (MilCIS)*, Canberra, 2015.
2. S. M. Kasongo and Y. Sun, "Performance analysis of intrusion detection systems using a feature selection method on the UNSW-NB15 dataset," *Journal of Big Data*, vol. 7, art. 105, 2020.
3. Y. Yin *et al.*, "IGRF-RFE: A hybrid feature selection method for MLP-based network intrusion detection on UNSW-NB15 dataset," *Journal of Big Data*, vol. 10, 2023.
4. M. Sarhan, S. Layeghy and M. Portmann, "Towards a standard feature set for network intrusion detection system datasets," arXiv:2101.11315, 2021.
5. T.-T. Nguyen and M. Park, "EL-GNN: A continual-learning-based graph neural network for task-incremental intrusion detection systems," *Electronics*, vol. 14, art. 2756, 2025.

---

## Slide 16: Thank you

**Layout:** Navy full-bleed, same layout as slide 1.

**On slide**
- Title: Thank you
- Subtitle: Questions and suggestions are welcome
- Small line: Code and results: [GitHub link]

---

## Viva prep (not slides, for the team)

**Why UNSW-NB15 and not NSL-KDD?**
NSL-KDD is derived from 1998–99 traffic. UNSW-NB15 (2015) has modern attack types and an official split, so results can be compared fairly.

**Why not deep learning?**
The question is which features matter. Tree ensembles reach strong results on tabular data, train in minutes on a CPU, and are interpretable. Deep models would hide the answer we are looking for.

**Why insist on the official split?**
Pooling and re-splitting can put near-identical records on both sides, which inflates scores. The official test file also has a different attack mix (55.1% vs 68.1%), which tests generalisation.

**Why macro-F1 over accuracy?**
Missing every Worms attack costs 0.05% accuracy, but it can cost up to one tenth of macro-F1, because Worms is one of the ten classes.

**What is new here?**
A same-protocol, per-class comparison of filter and embedded feature selection on the official split, plus a leave-one-attack-out test for unseen attacks.

**How is this "dynamic"?**
Phase 2 measures detection of attack types never seen in training, which is the defining problem of dynamic, evolving threats.
