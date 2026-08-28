from pathlib import Path

from tools.sdd.check import main


def test_sdd_contract_is_complete():
    assert main() == 0


def test_domain_governance_docs_exist():
    assert Path("docs/domain/invariants.md").is_file()
    assert Path("docs/domain/lifecycle-map.md").is_file()
