from string import Template

from scripts.slide_content import TEMPLATE, values

# classes the fake data does not have, so their per-class placeholders stay empty
ABSENT = ("Analysis", "Backdoor", "DoS", "Fuzzers", "Generic", "Reconnaissance", "Shellcode")


def test_every_placeholder_is_filled_from_a_fresh_run(results_dir):
    """Catches a results column the slide script reads but the pipeline no longer writes."""
    filled = values(results_dir)
    wanted = set(Template(TEMPLATE.read_text()).get_identifiers())
    assert {k for k in wanted - filled.keys() if not any(c in k for c in ABSENT)} == set()
