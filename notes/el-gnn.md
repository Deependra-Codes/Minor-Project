# EL-GNN — Electronics 2025, 14, 2756 (MDPI, open access)
- Problem: GNN-based IDS forgets old attacks when trained on new ones (catastrophic forgetting).
- Dataset: CIC-IDS2017, UNSW-NB15.
- Method: flows -> graph (node = flow ID, edge = shared src/dst IP, correlation-selected). GCN + weight-penalty continual learning (EWC-style).
- Accuracy: 95.9% (CIC-IDS2017), 96.4% (UNSW-NB15), 85.7% in task-incremental setting.
- Gaps: future work = newer datasets and evolving attacks. Graph + CL code is advanced for a minor project.
