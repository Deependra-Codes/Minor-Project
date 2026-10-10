# MedPlantNet — DARU J. Pharm. Sci. 2026 (Springer, s40199-026-00624-y)
- Problem: identify medicinal plant leaves automatically.
- Dataset: Mendeley medicinal plant leaf DB, 30 classes. External test: Bangladeshi medicinal plant set, MedLeaves.
- Method: EfficientNetB0 (fine-tuned) -> 1,280-dim deep features -> custom quadratic SVM. Grad-CAM + occlusion for explainability.
- Accuracy: 99.87% val, AUC 1.0. External: 99.27%, 99.80%.
- Gaps: no feature selection (all 1,280 features to SVM). Future work they list: robustness, real-time, mobile app, XAI decision support.
