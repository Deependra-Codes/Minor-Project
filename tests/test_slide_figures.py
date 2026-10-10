from scripts.slide_figures import main


def test_every_slide_figure_is_written(tmp_path):
    main(tmp_path)
    names = {"class_distribution", "pipeline", "zero_day", "timeline"}
    assert {p.stem for p in tmp_path.glob("*.png")} == names
