"""Fill slide_content_template.md with numbers from results/ and write docs/ppt-content.md.

python scripts/slide_content.py [results_dir] [out_file]

Every number on the slides comes from here, so `python -m ids.run` followed by this script regenerates
the deck text. A placeholder with no value raises KeyError (string.Template.substitute).
"""

import sys
from pathlib import Path
from string import Template

import pandas as pd

TEMPLATE = Path(__file__).with_name("slide_content_template.md")
METHOD = {
    "anova_f": "ANOVA F-test",
    "mutual_info": "mutual information",
    "rf_importance": "Random-Forest importance",
}
VARIANTS = {
    "base": "XGBoost baseline",
    "+prior shift": "+ prior shift (no labels)",
    "+class bias": "+ rare-class bias (no labels)",
    "+prior shift +class bias": "+ prior shift + rare-class bias (no labels)",
    "+feedback": "+ analyst feedback (1,000 labels)",
    "+feedback +prior shift": "+ analyst feedback + prior shift",
    "+feedback +prior shift +class bias": "+ analyst feedback + prior shift + rare-class bias",
}
FINAL = "+feedback +prior shift +class bias"


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}%"


def f3(value: float) -> str:
    return f"{value:.3f}"


def table(header: list[str], rows: list[list[str]]) -> str:
    align = ["---"] + ["---:"] * (len(header) - 1)
    lines = [header, align, *rows]
    return "\n".join("| " + " | ".join(str(cell) for cell in line) + " |" for line in lines)


def dataset(counts: pd.DataFrame) -> dict:
    n_train, n_test = counts["train"].sum(), counts["test"].sum()
    return {
        "attack_train": pct(1 - counts.loc["Normal", "train"] / n_train),
        "attack_test": pct(1 - counts.loc["Normal", "test"] / n_test),
        "worms_test": int(counts.loc["Worms", "test"]),
        "worms_cost": pct(counts.loc["Worms", "test"] / n_test, 2),
    }


def baselines(res: pd.DataFrame) -> dict:
    base = res[res["selection"] == "none"].set_index(["task", "model"])
    rows = []
    for model in base.loc["binary"].index:
        b, m = base.loc[("binary", model)], base.loc[("multiclass", model)]
        rows.append(
            [
                model,
                pct(b["accuracy"], 2),
                pct(b["false_alarm_rate"]),
                pct(m["accuracy"], 2),
                f3(m["macro_f1"]),
            ]
        )
    header = ["Model", "Binary accuracy", "Binary false alarms", "10-class accuracy", "10-class macro-F1"]
    xgb_b, xgb_m = base.loc[("binary", "XGBoost")], base.loc[("multiclass", "XGBoost")]
    return {
        "baseline_table": table(header, rows),
        "xgb_b_dr": pct(xgb_b["detection_rate"]),
        "xgb_b_far": pct(xgb_b["false_alarm_rate"]),
        "xgb_m_f1": f3(xgb_m["macro_f1"]),
        "hgb_plain_b_far": pct(base.loc[("binary", "HistGB"), "false_alarm_rate"]),
        "hgb_b_acc": pct(base.loc[("binary", "HistGB-balanced"), "accuracy"], 2),
        "hgb_b_far": pct(base.loc[("binary", "HistGB-balanced"), "false_alarm_rate"]),
        "hgb_m_far": pct(base.loc[("multiclass", "HistGB-balanced"), "false_alarm_rate"]),
    }


def ladder(improvement: pd.DataFrame, curve: pd.DataFrame, n_test: int) -> dict:
    lad = improvement.set_index(["task", "variant"])
    rows = []
    for key, name in VARIANTS.items():
        b, m = lad.loc[("binary", key)], lad.loc[("multiclass", key)]
        rows.append([name, pct(b["accuracy"], 2), pct(b["false_alarm_rate"]), pct(m["accuracy"], 2)])
        rows[-1] += [f3(m["macro_f1"]), pct(m["false_alarm_rate"])]
    header = ["Variant", "Binary accuracy", "Binary false alarms", "10-class accuracy", "10-class macro-F1"]
    labels = int(improvement["labels_used"].iloc[0])
    out = {
        "ladder_table": table([*header, "10-class false alarms"], rows),
        "eval_rows": f"{int(improvement['eval_rows'].iloc[0]):,}",
        "labels_used": f"{labels:,}",
        "label_share": pct(labels / n_test),
        "curve_points": " → ".join(pct(v) for v in curve[curve["task"] == "binary"]["false_alarm_rate"]),
    }
    for task, t in (("binary", "b"), ("multiclass", "m")):
        base, final = lad.loc[(task, "base")], lad.loc[(task, FINAL)]
        out |= {f"{t}_base_acc": pct(base["accuracy"], 2), f"{t}_base_far": pct(base["false_alarm_rate"])}
        out |= {f"{t}_base_f1": f3(base["macro_f1"]), f"{t}_fb_f1": f3(final["macro_f1"])}
        out |= {f"{t}_fb_acc": pct(final["accuracy"], 2), f"{t}_fb_far": pct(final["false_alarm_rate"])}
    cut = 1 - lad.loc[("binary", FINAL), "false_alarm_rate"] / lad.loc[("binary", "base"), "false_alarm_rate"]
    return out | {"b_far_cut": pct(cut, 0)}


def ceiling(ceil: pd.DataFrame) -> dict:
    out = {
        "ceil_m_acc": pct(ceil.loc["multiclass", "accuracy_ceiling"], 2),
        "ceil_m_f1": f3(ceil.loc["multiclass", "macro_f1_ceiling"]),
        "ceil_b_acc": pct(ceil.loc["binary", "accuracy_ceiling"], 2),
    }
    return out | {
        f"conf_{c}": pct(ceil.loc["multiclass", f"conflict_{c}"], 0)
        for c in ("Analysis", "Backdoor", "DoS", "Exploits", "Worms")
    }


def diagnosis(diag: pd.Series, ttl: pd.DataFrame) -> dict:
    shares = ttl.pivot(index="sttl", columns="split", values="attack_share")
    rows = [[value, pct(row["train"]), pct(row["test"])] for value, row in shares.iterrows()]
    header = ["Source TTL (sttl)", "Attack share in training file", "Attack share in test file"]
    return {
        "ttl_table": table(header, rows),
        "normal_count": f"{int(diag['normal_flows']):,}",
        "fa_count": f"{int(diag['false_alarms']):,}",
        "fa_read_as": diag["fa_read_as"],
        "fa_read_share": pct(diag["fa_read_as_share"], 0),
        "fa_nb": pct(diag["fa_train_neighbour_attack_share"], 0),
        "ok_nb": pct(diag["ok_train_neighbour_attack_share"], 0),
    }


def selection(res: pd.DataFrame, rank: pd.DataFrame) -> dict:
    """Smallest k whose 10-class macro-F1 is within 0.01 of the weakest all-feature run."""
    sel = res[(res["task"] == "multiclass") & (res["selection"] != "none")]
    full = sel[sel["n_features"] == sel["n_features"].max()]
    lo = full["macro_f1"].min()
    best = (
        sel[sel["macro_f1"] >= lo - 0.01]
        .sort_values(["n_features", "macro_f1"], ascending=[True, False])
        .iloc[0]
    )
    k = int(best["n_features"])
    same_k = sel[sel["n_features"] == k].set_index("selection")["macro_f1"]
    return {
        "fs_k": k,
        "fs_n_full": int(sel["n_features"].max()),
        "fs_method": METHOD[best["selection"]],
        "fs_k_f1": f3(best["macro_f1"]),
        "fs_k_acc": pct(best["accuracy"], 2),
        "full_f1_lo": f3(lo),
        "full_f1_hi": f3(full["macro_f1"].max()),
        "full_acc_lo": pct(full["accuracy"].min(), 2),
        "full_acc_hi": pct(full["accuracy"].max(), 2),
        "fs_k_all": " · ".join(f"{METHOD[m]} {f3(f)}" for m, f in same_k.items()),
        "fs_top": ", ".join(f"`{f}`" for f in rank[best["selection"]].head(k)),
        "anova_top": ", ".join(f"`{f}`" for f in rank["anova_f"].head(k)),
    }


def rare_classes(gain: pd.DataFrame) -> dict:
    rows = [[c, f3(r["base"]), f3(r["final"])] for c, r in gain.sort_values("base").iterrows()]
    out = {"gain_table": table(["Class", "Baseline recall", "Final recall"], rows)}
    for c, r in gain.iterrows():
        out |= {f"g_{c}_base": f3(r["base"]), f"g_{c}_final": f3(r["final"])}
    return out


def zero_day(zero: pd.DataFrame) -> dict:
    zero = zero.sort_values("detection_unseen")
    header = [
        "Attack type held out",
        "Test flows",
        "Detected when seen in training",
        "Detected when never seen",
    ]
    rows = [
        [r["held_out"], f"{int(r['test_rows']):,}", pct(r["detection_seen"]), pct(r["detection_unseen"])]
        for _, r in zero.iterrows()
    ]
    return {
        "zero_table": table(header, rows),
        "zero_n_high": int((zero["detection_unseen"] >= 0.9).sum()),
        "zero_worst": zero.iloc[0]["held_out"],
        "zero_worst_v": pct(zero.iloc[0]["detection_unseen"]),
    }


def main(results: Path, out: Path) -> None:
    read = lambda name, **kw: pd.read_csv(results / f"{name}.csv", **kw)  # noqa: E731
    counts, res = read("class_counts", index_col=0), read("results")
    values = dataset(counts) | baselines(res)
    values |= ladder(read("improvement"), read("feedback_curve"), int(counts["test"].sum()))
    values |= ceiling(read("ceiling", index_col=0))
    values |= diagnosis(read("diagnosis").iloc[0], read("ttl_shift"))
    values |= selection(res, read("ranking_multiclass", index_col=0))
    values |= rare_classes(read("recall_gain_multiclass", index_col=0))
    values |= zero_day(read("zero_day"))
    out.write_text(Template(TEMPLATE.read_text()).substitute(values))
    print(f"wrote {out} ({len(values)} values)")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(Path(args[0] if args else "results"), Path(args[1] if len(args) > 1 else "docs/ppt-content.md"))
