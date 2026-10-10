"""Imports go downward only (see AGENTS.md). Break a rule here on purpose once to see it fail."""

import ast
from pathlib import Path

import pytest

ALLOWED = {
    "data": set(),
    "models": set(),
    "plots": set(),
    "adapt": set(),
    "ceiling": set(),
    "metrics": {"data"},
    "selection": {"data"},
    "evasion": {"data", "metrics", "models", "plots"},
    "experiments": {"adapt", "ceiling", "data", "metrics", "models", "plots", "selection"},
    "run": {"data", "evasion", "experiments", "plots"},
}


@pytest.mark.parametrize("module", sorted(ALLOWED))
def test_module_imports_only_lower_layers(module):
    tree = ast.parse((Path("ids") / f"{module}.py").read_text())
    names = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]
    names += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    used = {name.split(".")[1] for name in names if name.startswith("ids.")}
    assert used <= ALLOWED[module], f"ids.{module} imports {used - ALLOWED[module]}"


def test_every_module_has_a_rule():
    assert {p.stem for p in Path("ids").glob("*.py")} - {"__init__"} == set(ALLOWED)
