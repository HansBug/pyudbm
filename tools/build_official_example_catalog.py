import json
import re
from pathlib import Path
from typing import Dict, Tuple


ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_DIR = ROOT / "test" / "testfile" / "official"
MANIFEST_PATH = OFFICIAL_DIR / "manifest.json"
OUTPUT_PATH = OFFICIAL_DIR / "catalog.json"


PARSE_KIND_ENUM = {
    "XML_MODEL_FILE": {
        "utap_api": "parse_XML_file",
        "extensions": [".xml"],
        "desc": "UPPAAL XML model file parsed through libutap XML loading.",
        "desc_zh": "通过 libutap XML 装载接口解析的 UPPAAL XML 模型文件。",
    },
    "TEXTUAL_MODEL_FILE": {
        "utap_api": "parse_XTA",
        "extensions": [".xta", ".ta"],
        "desc": "UPPAAL textual model file parsed through libutap XTA loading.",
        "desc_zh": "通过 libutap XTA 装载接口解析的 UPPAAL 文本模型文件。",
    },
    "QUERY_PROPERTY_FILE": {
        "utap_api": "UTAP::PropertyBuilder::parse(FILE*)",
        "extensions": [".q"],
        "desc": "UPPAAL query/property file parsed through the property parser.",
        "desc_zh": "通过性质解析器解析的 UPPAAL 查询/性质文件。",
    },
}


EXACT_SCENARIOS = {
    "2doors": ("the two-door access-control example", "双门访问控制示例"),
    "ClientServer": ("the client-server statistical model checking example", "客户端-服务器统计模型检测示例"),
    "LightContr": ("the TRON light controller example", "TRON 灯光控制器示例"),
    "SchedulingFramework": ("the scheduling framework demo", "调度框架演示示例"),
    "alp": ("the aircraft landing problem case study", "飞机着陆问题案例"),
    "ball": ("the bouncing-ball stochastic/hybrid example", "弹跳小球随机/混合示例"),
    "bando": ("the official `bando` benchmark case study", "`bando` 官方基准案例"),
    "bluetooth.cav": ("the Bluetooth protocol case study from the CAV examples", "CAV 示例中的 Bluetooth 协议案例"),
    "bocdp": ("the official `bocdp` benchmark case study", "`bocdp` 官方基准案例"),
    "bocdpFIXED": ("the fixed variant of the official `bocdp` benchmark", "`bocdp` 官方基准的 fixed 变体"),
    "bopdp": ("the official `bopdp` benchmark case study", "`bopdp` 官方基准案例"),
    "bopdpFIXED": ("the fixed variant of the official `bopdp` benchmark", "`bopdp` 官方基准的 fixed 变体"),
    "bridge": ("the bridge-crossing coordination example", "过桥协调示例"),
    "cat-and-mouse": ("the STRATEGO cat-and-mouse control example", "STRATEGO 猫鼠控制示例"),
    "cruise": ("the STRATEGO cruise-control example", "STRATEGO 巡航控制示例"),
    "csma-ca": ("the CSMA-CA protocol example", "CSMA-CA 协议示例"),
    "dice": ("the dice-based statistical example", "掷骰子统计示例"),
    "discomfort": ("the discomfort objective used in the ANOVA trade-off example", "ANOVA 权衡示例中的 discomfort 目标"),
    "ex-proba1": ("the first probability tutorial example", "第一个概率教程示例"),
    "ex-proba2": ("the second probability tutorial example", "第二个概率教程示例"),
    "firewire.cav": ("the FireWire protocol case study from the CAV examples", "CAV 示例中的 FireWire 协议案例"),
    "fischer": ("the classic Fischer mutual exclusion example", "经典 Fischer 互斥示例"),
    "fischer-stat": ("the statistical Fischer mutual exclusion variant", "Fischer 互斥的统计变体"),
    "fischer_symmetry": ("the symmetry-reduced Fischer mutual exclusion example", "带对称性约简的 Fischer 互斥示例"),
    "genosc": ("the gene-oscillation example", "基因振荡示例"),
    "genosc-hybrid": ("the hybrid gene-oscillation example", "混合基因振荡示例"),
    "interrupt": ("the interrupt-handling example", "中断处理示例"),
    "jugs2": ("the two-jugs CORA example", "两水壶 CORA 示例"),
    "leader-election": ("the leader-election statistical example", "领导者选举统计示例"),
    "lmac": ("the base LMAC protocol case study", "基础 LMAC 协议案例"),
    "lmac-bubble": ("the bubble-topology LMAC case study", "气泡拓扑 LMAC 案例"),
    "lmac-star": ("the star-topology LMAC case study", "星型拓扑 LMAC 案例"),
    "lmac6": ("the six-node LMAC protocol example", "六节点 LMAC 协议示例"),
    "lmac6-cmp": ("the comparison variant of the six-node LMAC case study", "六节点 LMAC 案例的比较变体"),
    "lmac6-power": ("the power-focused variant of the six-node LMAC case study", "六节点 LMAC 案例的功耗变体"),
    "lsc_example": ("the live sequence chart example", "LSC 现场序列图示例"),
    "lsc_train-gate_parameters": ("the parameterized live sequence chart train-gate example", "参数化的 LSC 火车-道口示例"),
    "newspaper": ("the STRATEGO newspaper-delivery example", "STRATEGO 报纸投递示例"),
    "onoff": ("the Yggdrasil on/off toggling example", "Yggdrasil 开关切换示例"),
    "oscillate": ("the oscillation tutorial example", "振荡教程示例"),
    "pareto": ("the Pareto/ANOVA trade-off example", "Pareto/ANOVA 权衡示例"),
    "philaudio": ("the official `philaudio` benchmark case study", "`philaudio` 官方基准案例"),
    "polling": ("the polling protocol example", "轮询协议示例"),
    "pollingH": ("the hierarchical polling example", "分层轮询示例"),
    "samplesmc": ("the sample statistical model checking example", "示例化统计模型检测案例"),
    "scheduling3": ("the three-task scheduling example", "三任务调度示例"),
    "scheduling4": ("the four-task scheduling example", "四任务调度示例"),
    "smc-tutorial-fig22": ("the SMC tutorial Figure 22 example", "SMC 教程图 22 示例"),
    "traffic": ("the STRATEGO traffic-control example", "STRATEGO 交通控制示例"),
    "train-gate": ("the classic train-gate example", "经典火车-道口示例"),
    "train-gate-orig": ("the original train-gate example", "原始火车-道口示例"),
    "train-gate-stat": ("the statistical train-gate variant", "火车-道口的统计变体"),
    "train-gate-strat": ("the STRATEGO train-gate strategy example", "STRATEGO 火车-道口策略示例"),
    "trig": ("the trigonometric/statistical tutorial example", "三角函数/统计教程示例"),
    "updown": ("the Yggdrasil up/down counter example", "Yggdrasil 加减计数器示例"),
    "vrptw": ("the vehicle-routing-with-time-windows case study", "带时间窗的车辆路径规划案例"),
}


def parse_kind_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".xml":
        return "XML_MODEL_FILE"
    if suffix in {".xta", ".ta"}:
        return "TEXTUAL_MODEL_FILE"
    if suffix == ".q":
        return "QUERY_PROPERTY_FILE"
    raise ValueError(f"Unsupported file suffix: {path}")


def scenario_for(stem: str) -> Tuple[str, str]:
    if stem in EXACT_SCENARIOS:
        return EXACT_SCENARIOS[stem]

    match = re.fullmatch(r"fischer_input_(\d+)", stem)
    if match:
        index = int(match.group(1))
        return (
            f"Fischer mutual exclusion benchmark instance {index}",
            f"Fischer 互斥基准的第 {index} 个实例",
        )

    match = re.fullmatch(r"csma_input_(\d+)", stem)
    if match:
        index = int(match.group(1))
        return (
            f"CSMA benchmark instance {index}",
            f"CSMA 基准的第 {index} 个实例",
        )

    match = re.fullmatch(r"hddi_input_(\d+)", stem)
    if match:
        index = int(match.group(1))
        return (
            f"HDDI benchmark instance {index}",
            f"HDDI 基准的第 {index} 个实例",
        )

    match = re.fullmatch(r"(concur05|jobshop2|traingate2)-(consmc|game|mycon-mc|mycon-smc)", stem)
    if match:
        family, variant = match.groups()
        family_desc = {
            "concur05": ("the CONCUR'05 case study", "CONCUR'05 案例"),
            "jobshop2": ("the job-shop scheduling case study", "作业车间调度案例"),
            "traingate2": ("the train-gate control case study", "火车-道口控制案例"),
        }[family]
        variant_desc = {
            "consmc": ("its ConsMC variant", "其 ConsMC 变体"),
            "game": ("its game-model variant", "其博弈模型变体"),
            "mycon-mc": ("its manual-controller model-checking variant", "其手工控制器模型检测变体"),
            "mycon-smc": ("its manual-controller statistical-checking variant", "其手工控制器统计检验变体"),
        }[variant]
        return (
            f"{family_desc[0]} in {variant_desc[0]}",
            f"{family_desc[1]}中的{variant_desc[1]}",
        )

    raise KeyError(f"No scenario description rule for stem: {stem}")


def describe_entry(relative_path: Path) -> Tuple[str, str]:
    stem = relative_path.name
    for suffix in (".xml", ".xta", ".ta", ".q"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break

    scenario_en, scenario_zh = scenario_for(stem)
    parse_kind = parse_kind_for(relative_path)

    if parse_kind == "XML_MODEL_FILE":
        return (
            f"XML model file for {scenario_en}.",
            f"{scenario_zh}的 XML 模型文件。",
        )
    if parse_kind == "TEXTUAL_MODEL_FILE":
        return (
            f"Textual model file for {scenario_en}.",
            f"{scenario_zh}的文本模型文件。",
        )
    if parse_kind == "QUERY_PROPERTY_FILE":
        return (
            f"Query/property file for {scenario_en}.",
            f"{scenario_zh}的性质/查询文件。",
        )
    raise ValueError(f"Unsupported parse kind: {parse_kind}")


def build_catalog() -> Dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = []

    for item in sorted(manifest, key=lambda x: x["local_path"]):
        local_path = Path(item["local_path"]).resolve()
        relative_path = local_path.relative_to(OFFICIAL_DIR)
        parse_kind = parse_kind_for(relative_path)
        desc, desc_zh = describe_entry(relative_path)
        entries.append(
            {
                "path": relative_path.as_posix(),
                "parse_kind": parse_kind,
                "desc": desc,
                "desc_zh": desc_zh,
            }
        )

    return {
        "version": 1,
        "base_dir": ".",
        "generated_from": "manifest.json",
        "parse_kind_enum": PARSE_KIND_ENUM,
        "files": entries,
    }


def main() -> None:
    catalog = build_catalog()
    OUTPUT_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
