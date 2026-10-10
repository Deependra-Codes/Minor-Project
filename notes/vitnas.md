# VitNas — Multimedia Tools & Appl. 2025 (Springer, s11042-025-21013-8)
- Problem: medicinal plant ID fails on real-world (field) photos; lab datasets too clean.
- Dataset: own REMEDS, 8,000 images, 15 classes, field conditions. Not public. Also tested on Mendeley Indian medicinal leaves (Pushpa G 2023) and Kaggle Indian medicinal plant set.
- Method: ensemble of ViT-B32 + NASNet-Large (transfer learning) + LLM layer that prints medicinal uses of predicted plant.
- Accuracy: 99.7% on REMEDS test.
- Gaps: dataset private; two large backbones = heavy, not mobile-friendly.
