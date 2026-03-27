import json
import re
from pathlib import Path

from .utap_phase0_data import OFFICIAL_CATALOG_PATH, REPO_ROOT


OFFICIAL_BASE_PATH = REPO_ROOT / "test/testfile/official"
OFFICIAL_QUERY_EXPECTATIONS_PATH = OFFICIAL_BASE_PATH / "query_expectations.json"


def _extract_newxta_flag(message: str):
    match = re.search(r"newxta=(true|false)", message)
    return None if match is None else (match.group(1) == "true")


def _load_catalog():
    return json.loads(OFFICIAL_CATALOG_PATH.read_text(encoding="utf-8"))


def _load_query_expectations():
    return json.loads(OFFICIAL_QUERY_EXPECTATIONS_PATH.read_text(encoding="utf-8"))


_CATALOG = _load_catalog()
_CATALOG_BY_PATH = {item["path"]: item for item in _CATALOG["files"]}
_QUERY_EXPECTATIONS = _load_query_expectations()

OFFICIAL_QUERY_CASES = tuple(
    (
        item["path"],
        item["context_path"],
        _extract_newxta_flag(_CATALOG_BY_PATH[item["context_path"]]["message"]),
    )
    for item in _CATALOG["files"]
    if item["parse_kind"] == "QUERY_PROPERTY_FILE"
)

REPRESENTATIVE_PROPERTY_QUERY = "linked/uppaal.org/casestudies/smc/lmac6.q"
REPRESENTATIVE_PROPERTY_CONTEXT = "linked/uppaal.org/casestudies/smc/lmac6.xml"

REPRESENTATIVE_TIGA_QUERY = "linked/uppaal.org/casestudies/smc/consmc/manual-models/concur/concur05-game.q"
REPRESENTATIVE_TIGA_CONTEXT = "linked/uppaal.org/casestudies/smc/consmc/manual-models/concur/concur05-game.xml"

REPRESENTATIVE_MIXED_QUERY = "linked/uppaal.org/casestudies/smc/consmc/consmc-models/concur/concur05-consmc.q"
REPRESENTATIVE_MIXED_CONTEXT = "linked/uppaal.org/casestudies/smc/consmc/consmc-models/concur/concur05-consmc.xml"

LINE_ENDING_SENSITIVE_PROPERTY_QUERY = (
    "linked/www.it.uu.se/research/group/darts/uppaal/benchmarks/hddi/hddi_input_02.q"
)
LINE_ENDING_SENSITIVE_PROPERTY_CONTEXT = (
    "linked/www.it.uu.se/research/group/darts/uppaal/benchmarks/hddi/hddi_input_02.ta"
)


def resolve_official_path(relative_path: str) -> Path:
    return OFFICIAL_BASE_PATH / relative_path


def query_expectation(relative_path: str):
    return _QUERY_EXPECTATIONS["files"][relative_path]
