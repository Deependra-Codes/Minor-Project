from ids.plots import _gain_labels


def test_each_recall_label_sits_on_the_outer_side_of_its_own_dot():
    (base_x, base_ha), (final_x, final_ha) = _gain_labels(base=0.84, final=0.62)  # recall fell
    assert base_x > 0.84 and base_ha == "left"
    assert final_x < 0.62 and final_ha == "right"
    (base_x, base_ha), (final_x, final_ha) = _gain_labels(base=0.40, final=0.81)  # recall rose
    assert base_x < 0.40 and base_ha == "right"
    assert final_x > 0.81 and final_ha == "left"
