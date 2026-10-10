# Minor-Project

Medicinal leaf classification: EfficientNetB0 features + feature selection + classic ML.

## Run on Google Colab
1. Download the dataset: https://data.mendeley.com/datasets/nnytj2v3n5/1 -> "Download All" (zip).
2. In Colab, upload the zip and `leaf_fs.py` (Files panel on the left).
3. Run:
   ```
   !unzip -q *.zip -d data
   !python leaf_fs.py data
   ```
4. Check the printed class list: it should show 30 species, about 1,800 images.
5. Outputs in `results/`: `results.csv` (accuracy, macro F1, timing per setup) and `fs_plot.png`.
