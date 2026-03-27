import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

OFFICIAL_CATALOG_RELATIVE_PATH = "test/testfile/official/catalog.json"
OFFICIAL_CATALOG_PATH = REPO_ROOT / OFFICIAL_CATALOG_RELATIVE_PATH

PHASE0_FIELD_COVERAGE = {
    "Document": (
        "globals",
        "templates",
        "processes",
        "queries",
        "options",
        "features",
        "errors",
        "warnings",
    ),
    "Template": (
        "name",
        "parameter",
        "declaration",
        "locations",
        "branchpoints",
        "edges",
        "init",
    ),
    "Process": (
        "name",
        "template_name",
        "arguments",
        "position",
    ),
    "Location": (
        "name",
        "position",
        "invariant",
        "exp_rate",
        "cost_rate",
        "nr",
    ),
    "Edge": (
        "nr",
        "control",
        "actname",
        "guard",
        "assign",
        "sync",
        "prob",
        "select",
    ),
    "Query": (
        "formula",
        "comment",
        "options",
        "expectation",
        "location",
    ),
    "ParsedQuery": (
        "line",
        "no",
        "type",
        "intermediate",
        "options",
        "result_type",
        "declaration",
        "expect",
    ),
    "expression_t": (
        "text",
        "kind",
        "position",
        "type",
        "size",
        "children",
        "is_empty",
    ),
    "type_t": (
        "kind",
        "position",
        "size",
        "text",
        "declaration",
    ),
    "symbol_t": (
        "name",
        "type",
        "position",
    ),
    "position_t": (
        "start",
        "end",
        "line",
        "column",
        "path",
    ),
}

PHASE0_SAMPLE_LAYERS = {
    "official_catalog": (OFFICIAL_CATALOG_RELATIVE_PATH,),
    "utap_model_fixtures": ("test/testfile/utap/simple_system.xml",),
    "manual_xta_fixtures": ("test/testfile/utap/minimal_ok.xta",),
    "synthetic_fixtures": (
        "test/testfile/utap/minimal_ok.xml",
        "test/testfile/utap/minimal_ok.xta",
    ),
}

EXPECTED_BUILTIN_DECLARATIONS = """const int INT8_MIN   =        -128;
const int INT8_MAX   =         127;
const int UINT8_MAX  =         255;
const int INT16_MIN  =      -32768;
const int INT16_MAX  =       32767;
const int UINT16_MAX =       65535;
const int INT32_MIN  = -2147483648;
const int INT32_MAX  =  2147483647;
typedef int[INT8_MIN,INT8_MAX]   int8_t;
typedef int[0,UINT8_MAX]         uint8_t;
typedef int[INT16_MIN,INT16_MAX] int16_t;
typedef int[0,UINT16_MAX]        uint16_t;
typedef int[INT32_MIN,INT32_MAX] int32_t;
const double FLT_MIN    = 1.1754943508222875079687365372222456778186655567720875e-38;
const double FLT_MAX    = 340282346638528859811704183484516925440.0;
const double DBL_MIN    = 2.2250738585072013830902327173324040642192159804623318e-308;
const double DBL_MAX    = 1.79769313486231570814527423731704356798070567525845e+308;
const double M_PI       = 3.141592653589793115997963468544185161590576171875;
const double M_PI_2     = 1.5707963267948965579989817342720925807952880859375;
const double M_PI_4     = 0.78539816339744827899949086713604629039764404296875;
const double M_E        = 2.718281828459045090795598298427648842334747314453125;
const double M_LOG2E    = 1.442695040888963387004650940070860087871551513671875;
const double M_LOG10E   = 0.43429448190325181666793241674895398318767547607421875;
const double M_LN2      = 0.69314718055994528622676398299518041312694549560546875;
const double M_LN10     = 2.30258509299404590109361379290930926799774169921875;
const double M_1_PI     = 0.31830988618379069121644420192751567810773849487304688;
const double M_2_PI     = 0.63661977236758138243288840385503135621547698974609375;
const double M_2_SQRTPI = 1.1283791670955125585606992899556644260883331298828125;
const double M_SQRT2    = 1.4142135623730951454746218587388284504413604736328125;
const double M_SQRT1_2  = 0.70710678118654757273731092936941422522068023681640625;
"""

MINIMAL_XML_RELATIVE_PATH = "test/testfile/utap/minimal_ok.xml"
MINIMAL_XTA_RELATIVE_PATH = "test/testfile/utap/minimal_ok.xta"
SIMPLE_SYSTEM_XML_RELATIVE_PATH = "test/testfile/utap/simple_system.xml"

MINIMAL_XML_PATH = REPO_ROOT / MINIMAL_XML_RELATIVE_PATH
MINIMAL_XTA_PATH = REPO_ROOT / MINIMAL_XTA_RELATIVE_PATH
UTAP_SIMPLE_SYSTEM_PATH = REPO_ROOT / SIMPLE_SYSTEM_XML_RELATIVE_PATH


def _load_catalog():
    return json.loads(OFFICIAL_CATALOG_PATH.read_text(encoding="utf-8"))


def _extract_newxta_flag(message: str):
    match = re.search(r"newxta=(true|false)", message)
    return None if match is None else (match.group(1) == "true")


_CATALOG = _load_catalog()
OFFICIAL_XML_MODEL_RELATIVE_PATHS = tuple(
    item["path"] for item in _CATALOG["files"] if item["parse_kind"] == "XML_MODEL_FILE"
)
OFFICIAL_TEXTUAL_MODEL_RELATIVE_PATHS = tuple(
    item["path"] for item in _CATALOG["files"] if item["parse_kind"] == "TEXTUAL_MODEL_FILE"
)
OFFICIAL_XML_MODEL_CASES = tuple(
    (
        OFFICIAL_CATALOG_PATH.parent / item["path"],
        _extract_newxta_flag(item["message"]),
    )
    for item in _CATALOG["files"]
    if item["parse_kind"] == "XML_MODEL_FILE"
)
OFFICIAL_TEXTUAL_MODEL_CASES = tuple(
    (
        OFFICIAL_CATALOG_PATH.parent / item["path"],
        _extract_newxta_flag(item["message"]),
    )
    for item in _CATALOG["files"]
    if item["parse_kind"] == "TEXTUAL_MODEL_FILE"
)
OFFICIAL_XML_MODEL_PATHS = tuple(OFFICIAL_CATALOG_PATH.parent / item for item in OFFICIAL_XML_MODEL_RELATIVE_PATHS)
OFFICIAL_TEXTUAL_MODEL_PATHS = tuple(
    OFFICIAL_CATALOG_PATH.parent / item for item in OFFICIAL_TEXTUAL_MODEL_RELATIVE_PATHS
)

INVALID_XML_MISSING_REF = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
  <declaration>clock x;</declaration>
  <template>
    <name x="0" y="0">P</name>
    <location id="id0" x="0" y="0">
      <name x="0" y="0">Init</name>
    </location>
    <init ref="missing"/>
  </template>
  <system>P1 = P();
system P1;</system>
</nta>
"""

INVALID_XTA_UNKNOWN_PROCESS = """clock x;
process P() {
state S;
init S;
}
system Missing;
"""

DUPLICATE_LOCATION_ID_WARNING_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' 'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
<nta>
  <declaration>clock x;</declaration>
  <template>
    <name x="0" y="0">P</name>
    <location id="dup" x="0" y="0">
      <name x="0" y="0">L0</name>
    </location>
    <location id="dup" x="120" y="0">
      <name x="120" y="0">L1</name>
    </location>
    <init ref="dup"/>
  </template>
  <system>P1 = P();
system P1;</system>
</nta>
"""
