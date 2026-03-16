from __future__ import annotations

import csv
import base64
import html
import io
import json
import math
import mimetypes
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from PIL import Image

SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_ROOT / "assets"
SECTION_DIR = ASSETS_DIR / "section_templates"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
RASTER_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_EMBED_IMAGE_SIZE = (1600, 1600)
JPEG_QUALITY = 82
IGNORED_OUTPUT_DIR_PREFIXES = {"report_output"}
IGNORED_FILE_NAMES = {"manifest.json"}
KNOWN_EXPERIMENT_TYPES = ("TCST", "OFT", "TST", "EPM", "FST", "NOR")
OBVIOUS_GROUP_LABELS = {
    "control",
    "ctrl",
    "model",
    "sham",
    "vehicle",
    "treated",
    "treatment",
    "drug",
    "test",
    "ko",
    "wt",
    "het",
    "tg",
}
SAMPLE_SUFFIX_PATTERNS = [
    r"_pose$",
    r"_region_dict$",
    r"_stat$",
    r"_trajectory_heatmap$",
    r"_timeseries$",
    r"_regional_atlas$",
    r"_statistics_analysis_combined$",
    r"_statistics_analysis$",
    r"_combined$",
    r"_heatmap$",
    r"_trajectory$",
    r"_atlas$",
    r"^violin_",
]

IMAGE_LINE_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")

SECTION_SPECS = [
    {
        "id": "project_summary",
        "title": "项目概况与素材",
        "section_key": "project_summary_section",
        "body_key": "project_summary_body",
        "template": "project-summary.md",
    },
    {
        "id": "overview",
        "title": "项目概述",
        "section_key": "overview_section",
        "body_key": "overview_body",
        "template": "overview.md",
    },
    {
        "id": "sample_check",
        "title": "样本与分组核对",
        "section_key": "sample_check_section",
        "body_key": "sample_check_body",
        "template": "sample-check.md",
    },
    {
        "id": "raw_trajectory",
        "title": "原始轨迹摘要",
        "section_key": "raw_trajectory_section",
        "body_key": "raw_trajectory_body",
        "template": "raw-trajectory.md",
    },
    {
        "id": "heatmap",
        "title": "热图与轨迹结果",
        "section_key": "heatmap_section",
        "body_key": "heatmap_body",
        "template": "heatmap-section.md",
        "gallery_key": "heatmap_gallery",
        "gallery_list_key": "heatmap",
    },
    {
        "id": "radar",
        "title": "雷达图结果",
        "section_key": "radar_section",
        "body_key": "radar_body",
        "template": "radar-section.md",
        "gallery_key": "radar_gallery",
        "gallery_list_key": "radar",
    },
    {
        "id": "stats",
        "title": "统计与汇总图结果",
        "section_key": "stats_section",
        "body_key": "stats_body",
        "template": "stats-section.md",
        "gallery_key": "stats_gallery",
        "gallery_list_key": "stats",
    },
    {
        "id": "cluster",
        "title": "聚类结果",
        "section_key": "cluster_section",
        "body_key": "cluster_body",
        "template": "cluster-section.md",
        "gallery_key": "cluster_gallery",
        "gallery_list_key": "cluster",
    },
    {
        "id": "single_subject",
        "title": "单样本结果概览",
        "section_key": "single_subject_section",
        "body_key": "single_subject_body",
        "template": "single-subject-section.md",
    },
    {
        "id": "integrated_interpretation",
        "title": "综合整理",
        "section_key": "integrated_interpretation_section",
        "body_key": "integrated_interpretation_body",
        "template": "integrated-interpretation.md",
    },
]

SECTION_GUIDANCE = {
    "project_summary_body": {
        "purpose": "把项目路径、核心素材、当前可分析范围和报告模式压缩成一个短节，避免报告开头堆太多元信息。",
        "write_when": "始终填写。",
        "source_fields": [
            "project_path",
            "facts.project_path_confirmation",
            "facts.input_completeness",
            "facts.materials_inventory",
            "report_mode",
            "report_mode_reason",
        ],
        "rules": [
            "控制在 3 到 5 句话内，优先让用户快速知道用了什么、缺什么、当前能写到哪一步。",
            "只点名最关键的素材目录或文件类型，不要展开成大清单。",
            "可以直接提到明显的样本数量、明显的分组前缀和当前最值得继续分析的素材。",
        ],
    },
    "overview_body": {
        "purpose": "给出项目层面的简短概览，补一句实验目的和基础流程，并先点出当前数据最显眼的结果特征。",
        "write_when": "通常填写；即使背景不完整，也要先概括当前数据的主要信号。",
        "source_fields": ["facts.overview", "report_mode", "facts.unconfirmed_items"],
        "rules": [
            "说明项目名、实验范式和当前报告用途；实验范式可来自项目名推断。",
            "如果实验范式已知，用 1 到 2 句话补充该实验通常评估什么、基本流程是什么。",
            "先给出 1 到 2 个最值得注意的结果摘要，再补充当前材料支持哪些分析。",
            "限制信息只在必要时顺带提一句，不要让整节变成方法说明。",
        ],
    },
    "sample_check_body": {
        "purpose": "核对样本数量、样本标识和分组信息，并在分组很明显时直接写出候选组别。",
        "write_when": "始终填写。",
        "source_fields": ["facts.sample_check", "facts.group_inference", "scan.detected"],
        "rules": [
            "先写样本总数和样本 ID 范围。",
            "如果文件名前缀里出现 control、model、sham、vehicle 这类明显分组，可以直接作为候选组别写出。",
            "对于明显标签，允许把 control 视为候选对照组；只有遇到含义不明确的缩写时才保留待确认。",
        ],
    },
    "raw_trajectory_body": {
        "purpose": "在只有原始骨架或轨迹数据时，基于坐标分布和路径长度给出简单的行为区域与活动模式摘要。",
        "write_when": "仅在 manifest 提供 raw trajectory summary 时填写。",
        "source_fields": ["facts.raw_trajectory_summary", "facts.group_inference", "facts.overview"],
        "rules": [
            "先写用了哪些原始轨迹文件或坐标来源，再写最明显的活动区域和运动范围特征。",
            "多样本项目优先比较组间或样本间最直观的差异，例如活动范围、主轴分布、路径长度。",
            "实验范式已知时可以直接使用该范式常见 readout 语言；如果装置朝向不明，就描述纵向/横向主轴或中心区域，不强行命名开放臂与闭合臂。",
        ],
    },
    "heatmap_body": {
        "purpose": "描述热图、轨迹图、atlas 或时序图展示的空间分布与行为模式。",
        "write_when": "仅在 manifest 含有 heatmap 图库时填写。",
        "source_fields": ["galleries.heatmap", "scan.figure_files", "facts.overview"],
        "rules": [
            "先点名使用了哪些图，再描述观察到的分布或轨迹特征。",
            "优先总结最直观、最明显的空间分布或轨迹特征。",
            "实验范式已知时，可以直接结合区域含义写出简洁总结。",
        ],
    },
    "radar_body": {
        "purpose": "概述雷达图所反映的多指标轮廓。",
        "write_when": "仅在 manifest 含有 radar 图库时填写。",
        "source_fields": ["galleries.radar", "scan.figure_files", "facts.sample_check"],
        "rules": [
            "说明图中比较的是单样本还是多组轮廓。",
            "优先概括最突出的高低特征和轮廓差异。",
            "没有可靠分组时，不写正式组间比较；但可以正常总结单样本或候选标签层面的模式。",
        ],
    },
    "stats_body": {
        "purpose": "总结具有统计表或明确统计图支持的比较结果；单样本项目也可以写数值摘要。",
        "write_when": "在 manifest 含有 stats 图库时填写；单样本项目写统计摘要，多样本项目在依据充分时写比较结果。",
        "source_fields": ["galleries.stats", "scan.data_files", "facts.sample_check"],
        "rules": [
            "先写统计依据来自哪些表或图，再写结果。",
            "没有统计表时不要写显著性结论。",
            "单样本项目可以直接总结最主要的数值特征、区域偏好或行为趋势。",
            "组别含义未完全确认时，不写正式机制性比较，但可以基于明显组名总结原始差异方向。",
        ],
    },
    "cluster_body": {
        "purpose": "描述聚类图中呈现的样本或指标结构。",
        "write_when": "仅在 manifest 含有 cluster 图库时填写。",
        "source_fields": ["galleries.cluster", "scan.figure_files", "facts.sample_check"],
        "rules": [
            "说明聚类对象是样本还是指标。",
            "只描述结构接近性或分离趋势。",
            "不要把聚类分离直接写成统计显著差异。",
        ],
    },
    "single_subject_body": {
        "purpose": "在单样本模式下总结单个个体或单条记录的核心结果。",
        "write_when": "仅在 report_mode 为 single-subject 时填写。",
        "source_fields": ["facts.single_subject_stats", "facts.raw_trajectory_summary", "scan.figure_files", "galleries.heatmap"],
        "rules": [
            "优先覆盖总时长、有效检测时长、总距离、区域停留和进入情况。",
            "如果只有原始骨架数据，也要基于轨迹分布写出该样本最突出的行动区域或运动模式。",
            "先给出一句最主要的单样本总结，再展开关键指标。",
            "不要把单样本现象写成群体规律，但应明确写出该样本最突出的行为特征。",
        ],
    },
    "integrated_interpretation_body": {
        "purpose": "跨图类整合多个结果来源，形成直接而清楚的综合总结。",
        "write_when": "仅在至少两类证据来源同时存在时填写。",
        "source_fields": ["galleries", "facts.overview", "facts.raw_trajectory_summary", "facts.unconfirmed_items", "report_mode"],
        "rules": [
            "明确综合了哪些图类、统计或原始轨迹来源。",
            "先写一段直接的综合结论，再补充支持它的图和数据。",
            "把观察事实和解释分开写，但不要把整节写成免责声明。",
            "未获授权时，不写机制性或因果性结论。",
        ],
    },
}


def ensure_project_path(project_path: str | Path) -> Path:
    path = Path(project_path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Project path does not exist or is not a directory: {path}")
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def classify_file(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    ext = path.suffix.lower()
    parent_text = " ".join(part.lower() for part in path.parts)

    if ext in {".yaml", ".yml", ".json"}:
        if "stat" in name or "summary" in name:
            return "data", "stats_json"
        return "metadata", "metadata"
    if ext == ".h5":
        return "data", "skeleton_data"
    if ext in {".csv", ".tsv", ".xlsx", ".xls"}:
        if any(token in name for token in ["pose", "skeleton", "keypoint"]) or "skeleton" in parent_text:
            return "data", "skeleton_data"
        if any(token in name for token in ["region_dict", "behavior", "summary"]):
            return "data", "behavior_summary"
        if any(token in name for token in ["stats", "stat", "pairwise", "overall", "kruskal"]):
            return "data", "stats_table"
        return "data", "table"
    if ext in IMAGE_EXTENSIONS:
        if any(token in name for token in ["clustermap", "cluster", "dendrogram"]):
            return "figure", "cluster"
        if "radar" in name:
            return "figure", "radar"
        if any(token in name for token in ["heatmap", "trajectory"]):
            return "figure", "heatmap"
        if any(token in name for token in ["violin", "boxplot", "statistics_analysis_combined", "statistics"]):
            return "figure", "stats_figure"
        if "timeseries" in name:
            return "figure", "timeseries"
        if "atlas" in name:
            return "figure", "atlas"
        return "figure", "other_figure"
    return "other", ext.lstrip(".") or "no_extension"


def normalize_sample_id(stem: str) -> str:
    sample = stem
    for pattern in SAMPLE_SUFFIX_PATTERNS:
        sample = re.sub(pattern, "", sample, flags=re.IGNORECASE)
    sample = re.sub(r"__[^_]+__[^_]+__p\d+$", "", sample, flags=re.IGNORECASE)
    return sample.strip("_- ") or stem


def infer_experiment_type(project_path: Path, stats_payload: dict[str, Any] | None) -> str | None:
    analysis_type = str((stats_payload or {}).get("analysis_type") or "").strip()
    if analysis_type:
        upper = analysis_type.upper()
        if upper in KNOWN_EXPERIMENT_TYPES:
            return upper

    candidates = [project_path.name, str(project_path)]
    pattern_map = {name: re.compile(rf"(?<![A-Za-z]){name}(?![A-Za-z])", re.IGNORECASE) for name in KNOWN_EXPERIMENT_TYPES}
    for candidate in candidates:
        for name, pattern in pattern_map.items():
            if pattern.search(candidate):
                return name
    return None


def infer_obvious_groups(sample_ids: list[str]) -> dict[str, Any]:
    sample_to_group: dict[str, str] = {}
    counts: Counter[str] = Counter()
    for sample_id in sample_ids:
        match = re.match(r"^([A-Za-z]+)", sample_id)
        if not match:
            continue
        label = match.group(1).lower()
        if label not in OBVIOUS_GROUP_LABELS:
            continue
        sample_to_group[sample_id] = label
        counts[label] += 1

    valid_labels = sorted(label for label, count in counts.items() if count >= 2)
    if len(valid_labels) >= 2:
        filtered_counts = {label: counts[label] for label in valid_labels}
        filtered_sample_map = {sample_id: label for sample_id, label in sample_to_group.items() if label in valid_labels}
        control_group = "control" if "control" in filtered_counts else None
        return {
            "status": "inferred",
            "method": "filename-prefix",
            "has_groups": True,
            "labels": valid_labels,
            "display_mapping": {label: label for label in valid_labels},
            "group_counts": filtered_counts,
            "sample_to_group": filtered_sample_map,
            "control_group": control_group,
        }

    return {
        "status": "unknown",
        "method": "none",
        "has_groups": None,
        "labels": [],
        "display_mapping": {},
        "group_counts": {},
        "sample_to_group": {},
        "control_group": None,
    }


def detect_track_columns(fieldnames: list[str]) -> tuple[str, str, str] | None:
    candidates = [
        ("back_x", "back_y", "back"),
        ("nose_x", "nose_y", "nose"),
        ("tail_x", "tail_y", "tail"),
        ("x", "y", "center"),
    ]
    available = set(fieldnames)
    for x_key, y_key, label in candidates:
        if x_key in available and y_key in available:
            return x_key, y_key, label
    return None


def summarize_track_file(path: Path) -> dict[str, Any] | None:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                return None
            track_columns = detect_track_columns(list(reader.fieldnames))
            if not track_columns:
                return None

            x_key, y_key, point_label = track_columns
            xs: list[float] = []
            ys: list[float] = []
            prev: tuple[float, float] | None = None
            path_length = 0.0
            for row in reader:
                try:
                    x_value = float(row[x_key])
                    y_value = float(row[y_key])
                except Exception:
                    continue
                xs.append(x_value)
                ys.append(y_value)
                if prev is not None:
                    path_length += math.hypot(x_value - prev[0], y_value - prev[1])
                prev = (x_value, y_value)
    except Exception:
        return None

    if not xs or not ys:
        return None

    return {
        "sample_id": normalize_sample_id(path.stem),
        "source_file": path.name,
        "point_label": point_label,
        "frame_count": len(xs),
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "mean_x": statistics.fmean(xs),
        "mean_y": statistics.fmean(ys),
        "x_span": max(xs) - min(xs),
        "y_span": max(ys) - min(ys),
        "path_length": path_length,
        "points": list(zip(xs, ys)),
    }


def build_raw_trajectory_summary(
    project_path: Path,
    scan: dict[str, Any],
    experiment_type: str | None,
    group_info: dict[str, Any],
) -> dict[str, Any] | None:
    track_summaries: list[dict[str, Any]] = []
    for item in scan["data_files"]:
        rel_path = item["path"]
        if Path(rel_path).suffix.lower() not in {".csv", ".tsv"}:
            continue
        summary = summarize_track_file(project_path / rel_path)
        if not summary:
            continue
        sample_id = summary["sample_id"]
        summary["group"] = group_info["sample_to_group"].get(sample_id)
        track_summaries.append(summary)

    if not track_summaries:
        return None

    point_label = track_summaries[0]["point_label"]
    total_frames = sum(int(item["frame_count"]) for item in track_summaries)
    group_counts = dict(group_info.get("group_counts") or {})
    highlights = [
        f"共读取 {len(track_summaries)} 个原始轨迹文件，坐标锚点为 {point_label}，累计约 {total_frames} 帧。"
    ]

    samples_by_group: dict[str, list[dict[str, Any]]] = {}
    for summary in track_summaries:
        group_name = summary.get("group") or "all"
        samples_by_group.setdefault(group_name, []).append(summary)

    per_group_metrics: dict[str, Any] = {}
    for group_name, rows in samples_by_group.items():
        per_group_metrics[group_name] = {
            "sample_count": len(rows),
            "mean_path_length": statistics.fmean(item["path_length"] for item in rows),
            "mean_x_span": statistics.fmean(item["x_span"] for item in rows),
            "mean_y_span": statistics.fmean(item["y_span"] for item in rows),
            "top_samples_by_path": [
                {
                    "sample_id": item["sample_id"],
                    "path_length": item["path_length"],
                    "x_span": item["x_span"],
                    "y_span": item["y_span"],
                }
                for item in sorted(rows, key=lambda item: item["path_length"], reverse=True)[:3]
            ],
        }

    if experiment_type == "EPM":
        all_x = [point[0] for item in track_summaries for point in item["points"]]
        all_y = [point[1] for item in track_summaries for point in item["points"]]
        center_x = statistics.median(all_x)
        center_y = statistics.median(all_y)
        arm_half_width = max(35.0, min(80.0, 0.08 * min(max(all_x) - min(all_x), max(all_y) - min(all_y))))

        for item in track_summaries:
            counts = {"center": 0, "vertical_axis": 0, "horizontal_axis": 0, "corner": 0}
            for x_value, y_value in item["points"]:
                in_vertical = abs(x_value - center_x) <= arm_half_width
                in_horizontal = abs(y_value - center_y) <= arm_half_width
                if in_vertical and in_horizontal:
                    counts["center"] += 1
                elif in_vertical:
                    counts["vertical_axis"] += 1
                elif in_horizontal:
                    counts["horizontal_axis"] += 1
                else:
                    counts["corner"] += 1
            total = max(1, len(item["points"]))
            item["epm_axis_ratios"] = {key: counts[key] / total for key in counts}

        for group_name, rows in samples_by_group.items():
            epm_rows = [item["epm_axis_ratios"] for item in rows if "epm_axis_ratios" in item]
            if not epm_rows:
                continue
            per_group_metrics[group_name]["epm_axis_ratios"] = {
                key: statistics.fmean(row[key] for row in epm_rows)
                for key in ["center", "vertical_axis", "horizontal_axis", "corner"]
            }

        overall_vertical = statistics.fmean(
            item["epm_axis_ratios"]["vertical_axis"] for item in track_summaries if "epm_axis_ratios" in item
        )
        overall_horizontal = statistics.fmean(
            item["epm_axis_ratios"]["horizontal_axis"] for item in track_summaries if "epm_axis_ratios" in item
        )
        highlights.append(
            f"从坐标主轴粗分看，轨迹整体更集中在穿过中心的纵向主轴（平均占比 {overall_vertical:.1%}），横向主轴占比约 {overall_horizontal:.1%}。"
        )

        if "control" in per_group_metrics and "model" in per_group_metrics:
            control_metrics = per_group_metrics["control"]
            model_metrics = per_group_metrics["model"]
            highlights.append(
                "按文件名前缀划分时，control 组的横向活动范围更大，"
                f"平均横向跨度约 {control_metrics['mean_x_span']:.1f} 像素，"
                f"高于 model 组的 {model_metrics['mean_x_span']:.1f} 像素。"
            )

    return {
        "source": "raw-skeleton",
        "point_label": point_label,
        "sample_count": len(track_summaries),
        "group_counts": group_counts,
        "per_group_metrics": per_group_metrics,
        "highlights": highlights,
        "samples": [
            {
                "sample_id": item["sample_id"],
                "source_file": item["source_file"],
                "group": item.get("group"),
                "frame_count": item["frame_count"],
                "path_length": item["path_length"],
                "x_span": item["x_span"],
                "y_span": item["y_span"],
            }
            for item in track_summaries
        ],
    }


def extract_group_labels_from_csv(path: Path, limit: int = 1000) -> list[str]:
    labels: set[str] = set()
    if path.suffix.lower() not in {".csv", ".tsv"}:
        return []
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames or "group" not in reader.fieldnames:
                return []
            for index, row in enumerate(reader):
                if index >= limit:
                    break
                value = (row.get("group") or "").strip()
                if value:
                    labels.add(value)
    except Exception:
        return []
    return sorted(labels)


def render_template(template_text: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        value = context.get(key, "")
        if value is None:
            return ""
        return str(value)

    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", replace, template_text)


def render_section(template_name: str, context: dict[str, Any], enabled: bool = True) -> str:
    if not enabled:
        return ""
    content = render_template(read_text(SECTION_DIR / template_name), context).strip()
    return content if content else ""


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = LINK_RE.sub(lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>', escaped)
    escaped = CODE_RE.sub(lambda match: f"<code>{html.escape(match.group(1))}</code>", escaped)
    return escaped


def markdown_to_html(markdown_text: str, image_src_transform: Callable[[str], str] | None = None) -> str:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            parts.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            parts.append("<ul>")
            for item in list_items:
                parts.append(f"<li>{inline_markdown(item)}</li>")
            parts.append("</ul>")
            list_items = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            flush_paragraph()
            flush_list()
            continue
        image_match = IMAGE_LINE_RE.match(line.strip())
        if image_match:
            flush_paragraph()
            flush_list()
            caption = image_match.group(1).strip() or "Figure"
            src = image_match.group(2).strip()
            if image_src_transform:
                src = image_src_transform(src)
            parts.append("<figure>")
            parts.append(f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" />')
            parts.append(f"<figcaption>{inline_markdown(caption)}</figcaption>")
            parts.append("</figure>")
            continue
        if line.startswith("### "):
            flush_paragraph()
            flush_list()
            parts.append(f"<h3>{inline_markdown(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            flush_paragraph()
            flush_list()
            parts.append(f"<h2>{inline_markdown(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            parts.append(f"<h1>{inline_markdown(line[2:])}</h1>")
            continue
        if line.startswith("- "):
            flush_paragraph()
            list_items.append(line[2:])
            continue
        flush_list()
        paragraph.append(line)

    flush_paragraph()
    flush_list()
    return "\n".join(parts)


def build_gallery(paths: list[str], project_path: Path) -> str:
    entries: list[str] = []
    for rel_path in paths:
        abs_path = (project_path / rel_path).resolve()
        entries.append(f"![{Path(rel_path).name}]({abs_path.as_uri()})")
    return "\n\n".join(entries)


def normalize_svg_text(text: str) -> str:
    text = text.lstrip("\ufeff").strip()
    text = re.sub(r">\s+<", "><", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text


def encode_file_as_data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".svg":
        svg_text = normalize_svg_text(read_text(path))
        payload = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{payload}"

    if suffix in RASTER_IMAGE_EXTENSIONS:
        with Image.open(path) as image:
            image.load()
            image.thumbnail(MAX_EMBED_IMAGE_SIZE)

            has_alpha = image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info)
            buffer = io.BytesIO()
            if has_alpha:
                image.save(buffer, format="PNG", optimize=True, compress_level=9)
                mime_type = "image/png"
            else:
                converted = image.convert("RGB") if image.mode != "RGB" else image
                converted.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
                mime_type = "image/jpeg"
            payload = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:{mime_type};base64,{payload}"

    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


def file_uri_to_path(src: str) -> Path | None:
    parsed = urlparse(src)
    if parsed.scheme != "file":
        return None

    raw_path = url2pathname(unquote(parsed.path))
    if parsed.netloc:
        raw_path = f"//{parsed.netloc}{raw_path}"
    return Path(raw_path)


def build_embedded_image_transform() -> Callable[[str], str]:
    cache: dict[str, str] = {}

    def transform(src: str) -> str:
        if src in cache:
            return cache[src]

        path = file_uri_to_path(src)
        if not path or not path.exists():
            cache[src] = src
            return src

        embedded = encode_file_as_data_uri(path)
        cache[src] = embedded
        return embedded

    return transform


def scan_project(project_path: Path) -> dict[str, Any]:
    files = [
        path
        for path in project_path.rglob("*")
        if path.is_file()
        and not any(part.startswith(prefix) for part in path.parts for prefix in IGNORED_OUTPUT_DIR_PREFIXES)
        and path.name not in IGNORED_FILE_NAMES
    ]
    data_files: list[dict[str, str]] = []
    figure_files: list[dict[str, str]] = []
    metadata_files: list[str] = []
    other_files: list[str] = []
    sample_ids: set[str] = set()
    group_labels: set[str] = set()

    for path in sorted(files):
        kind, subtype = classify_file(path)
        rel_path = relative_posix(path, project_path)
        record = {"path": rel_path, "subtype": subtype}
        if kind == "data":
            data_files.append(record)
            if subtype in {"skeleton_data", "behavior_summary", "stats_json"}:
                sample_ids.add(normalize_sample_id(path.stem))
            if path.suffix.lower() in {".csv", ".tsv"}:
                group_labels.update(extract_group_labels_from_csv(path))
        elif kind == "figure":
            figure_files.append(record)
            if subtype in {"heatmap", "radar", "timeseries", "atlas", "stats_figure"}:
                sample_ids.add(normalize_sample_id(path.stem))
        elif kind == "metadata":
            metadata_files.append(rel_path)
        else:
            other_files.append(rel_path)

    obvious_group_info = infer_obvious_groups(sorted(sample_ids))
    inferred_group_labels = sorted(set(obvious_group_info["labels"]))

    detected = {
        "sample_ids_detected": sorted(sample_ids),
        "sample_count_detected": len(sample_ids),
        "group_labels_detected": sorted(group_labels) or inferred_group_labels,
        "has_skeleton_data": any(item["subtype"] == "skeleton_data" for item in data_files),
        "has_behavior_summary": any(item["subtype"] == "behavior_summary" for item in data_files),
        "has_stats_tables": any(item["subtype"] in {"stats_table", "stats_json"} for item in data_files),
        "has_stats_figures": any(item["subtype"] == "stats_figure" for item in figure_files),
        "has_heatmaps": any(item["subtype"] in {"heatmap", "timeseries", "atlas"} for item in figure_files),
        "has_radar": any(item["subtype"] == "radar" for item in figure_files),
        "has_cluster_figure": any(item["subtype"] == "cluster" for item in figure_files),
        "metadata_files_found": metadata_files,
    }

    return {
        "project_path": str(project_path),
        "project_name": project_path.name,
        "files_scanned": len(files),
        "data_files": data_files,
        "figure_files": figure_files,
        "metadata_files": metadata_files,
        "other_files": other_files,
        "detected": detected,
    }


def load_single_subject_stats(project_path: Path, scan: dict[str, Any]) -> dict[str, Any] | None:
    stats_jsons = [item["path"] for item in scan["data_files"] if item["subtype"] == "stats_json"]
    for rel_path in stats_jsons:
        try:
            payload = load_json(project_path / rel_path)
        except Exception:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def determine_report_mode(
    scan: dict[str, Any],
    group_info: dict[str, Any],
    raw_summary: dict[str, Any] | None,
) -> tuple[str, str]:
    detected = scan["detected"]
    has_groups = group_info.get("has_groups") is True

    if detected["sample_count_detected"] <= 1 and not has_groups:
        return "single-subject", "当前仅检测到一个样本，且没有可靠分组信息。"
    if has_groups and (
        detected["has_stats_tables"]
        or detected["has_stats_figures"]
        or detected["has_radar"]
        or detected["has_cluster_figure"]
    ):
        return "grouped-comparison", "已确认分组信息，且存在支持组间整理的图表或统计结果。"
    if has_groups and raw_summary:
        return "grouped-raw-summary", "存在明显分组，同时可直接从原始骨架轨迹提炼组间活动差异。"
    if detected["sample_count_detected"] > 1 and not has_groups:
        return "multi-sample-no-groups", "检测到多个样本，但没有可靠分组说明。"
    if any(detected[key] for key in ["has_heatmaps", "has_radar", "has_stats_figures", "has_cluster_figure"]):
        return "figure-only-summary", "当前更适合基于现有图像结果做描述性整理。"
    if raw_summary:
        return "raw-trajectory-summary", "当前主要可依据原始骨架轨迹对活动区域和运动范围做基础总结。"
    return "data-inventory-only", "素材不足以支撑结果解读，当前只能做材料盘点。"


def build_unconfirmed_items(
    scan: dict[str, Any],
    stats_payload: dict[str, Any] | None,
    experiment_type: str | None,
    group_info: dict[str, Any],
) -> list[str]:
    detected = scan["detected"]
    items: list[str] = []

    items.append("报告用途未确认，当前按结果整理口径撰写。")
    if not experiment_type:
        inferred = stats_payload.get("analysis_type") if stats_payload else None
        if inferred:
            items.append(f"实验范式未明确，当前只能暂按 {inferred} 理解。")
        else:
            items.append("实验范式未确认。")
    if group_info.get("status") == "unknown":
        items.append("是否存在分组尚未确认。")
    if group_info.get("status") == "inferred":
        items.append("当前分组来自文件名前缀推断；如有正式分组定义，可进一步补充。")
    elif detected["group_labels_detected"]:
        items.append("检测到候选组标签，但组别含义尚未确认。")
    if group_info.get("has_groups") and not group_info.get("control_group"):
        items.append("存在分组，但对照组尚未确认。")
    items.append("是否允许写解释性结论尚未确认。")
    if stats_payload and stats_payload.get("Total Distance (pixels)"):
        items.append("总距离当前以像素表示，尚未确认是否能换算为实际长度。")
    return items


def summarize_region_stats(stats_payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    region_stats = stats_payload.get("statistics") or {}
    percent_map = stats_payload.get("percent(%)") or {}
    ordered: list[tuple[str, float, int, str]] = []

    for region, payload in region_stats.items():
        if not isinstance(payload, dict):
            continue
        stay_time = float(payload.get("Stay Time (s)", 0.0) or 0.0)
        enter_count = int(payload.get("Enter Count", 0) or 0)
        percent = str(percent_map.get(region, ""))
        ordered.append((region, stay_time, enter_count, percent))

    ordered.sort(key=lambda item: item[1], reverse=True)
    region_lines = [
        f"{region}：停留 {stay_time:g} 秒，进入 {enter_count} 次，占比 {percent or '未提供'}"
        for region, stay_time, enter_count, percent in ordered
    ]
    zero_regions = [region for region, stay_time, enter_count, _ in ordered if stay_time == 0 and enter_count == 0]
    return region_lines, zero_regions


def select_section_specs(
    report_mode: str,
    galleries: dict[str, list[str]],
    raw_summary: dict[str, Any] | None,
) -> list[dict[str, str]]:
    enabled_ids = {
        "project_summary",
        "overview",
        "sample_check",
    }
    if raw_summary:
        enabled_ids.add("raw_trajectory")
    if galleries["heatmap"]:
        enabled_ids.add("heatmap")
    if galleries["radar"]:
        enabled_ids.add("radar")
    if galleries["stats"]:
        enabled_ids.add("stats")
    if galleries["cluster"]:
        enabled_ids.add("cluster")
    if report_mode == "single-subject":
        enabled_ids.add("single_subject")
    evidence_count = sum(bool(paths) for paths in galleries.values()) + int(bool(raw_summary))
    if evidence_count >= 2:
        enabled_ids.add("integrated_interpretation")
    return [spec for spec in SECTION_SPECS if spec["id"] in enabled_ids]


def build_section_bodies(specs: list[dict[str, str]]) -> dict[str, Any]:
    section_bodies: dict[str, Any] = {}
    for spec in specs:
        guidance = SECTION_GUIDANCE[spec["body_key"]]
        section_bodies[spec["body_key"]] = {
            "section_id": spec["id"],
            "title": spec["title"],
            "purpose": guidance["purpose"],
            "write_when": guidance["write_when"],
            "source_fields": guidance["source_fields"],
            "rules": guidance["rules"],
            "body": "",
        }
    return section_bodies


def build_manifest(project_path: Path) -> dict[str, Any]:
    scan_payload = scan_project(project_path)
    stats_payload = load_single_subject_stats(project_path, scan_payload)
    detected = scan_payload["detected"]
    experiment_type = infer_experiment_type(project_path, stats_payload)
    group_info = infer_obvious_groups(detected["sample_ids_detected"])
    raw_summary = build_raw_trajectory_summary(project_path, scan_payload, experiment_type, group_info)
    report_mode, report_mode_reason = determine_report_mode(scan_payload, group_info, raw_summary)

    galleries = {
        "heatmap": [item["path"] for item in scan_payload["figure_files"] if item["subtype"] in {"heatmap", "timeseries", "atlas"}],
        "radar": [item["path"] for item in scan_payload["figure_files"] if item["subtype"] == "radar"],
        "stats": [item["path"] for item in scan_payload["figure_files"] if item["subtype"] == "stats_figure"],
        "cluster": [item["path"] for item in scan_payload["figure_files"] if item["subtype"] == "cluster"],
    }

    facts: dict[str, Any] = {
        "project_path_confirmation": {
            "project_path": str(project_path),
            "files_scanned": scan_payload["files_scanned"],
            "key_inputs_preview": (
                [item["path"] for item in scan_payload["data_files"][:3]]
                + [item["path"] for item in scan_payload["figure_files"][:3]]
                + scan_payload["metadata_files"][:2]
            ),
        },
        "input_completeness": {
            "checks": [
                {"label": "骨架或轨迹数据", "available": detected["has_skeleton_data"]},
                {"label": "行为或 summary 表", "available": detected["has_behavior_summary"]},
                {"label": "统计表", "available": detected["has_stats_tables"]},
                {"label": "热图或轨迹图", "available": detected["has_heatmaps"]},
                {"label": "雷达图", "available": detected["has_radar"]},
                {"label": "聚类图", "available": detected["has_cluster_figure"]},
            ]
        },
        "overview": {
            "project_name": scan_payload["project_name"],
            "report_mode": report_mode,
            "report_goal": "results-summary",
            "experiment_type": experiment_type,
        },
        "sample_check": {
            "sample_count_detected": detected["sample_count_detected"],
            "sample_ids_detected": detected["sample_ids_detected"],
            "has_groups": group_info.get("has_groups"),
            "group_labels_detected": group_info.get("labels") or detected["group_labels_detected"],
            "group_mapping": group_info.get("display_mapping") or {},
            "group_counts": group_info.get("group_counts") or {},
            "group_status": group_info.get("status"),
            "control_group": group_info.get("control_group"),
        },
        "group_inference": group_info,
        "materials_inventory": {
            "data_files": [item["path"] for item in scan_payload["data_files"]],
            "figure_files": [item["path"] for item in scan_payload["figure_files"]],
            "metadata_files": scan_payload["metadata_files"],
            "other_files": scan_payload["other_files"],
        },
        "unconfirmed_items": build_unconfirmed_items(scan_payload, stats_payload, experiment_type, group_info),
    }

    if stats_payload:
        region_lines, zero_regions = summarize_region_stats(stats_payload)
        facts["single_subject_stats"] = {
            "file_name": stats_payload.get("file_name"),
            "analysis_type": stats_payload.get("analysis_type"),
            "total_time_s": stats_payload.get("total_time(s)"),
            "detect_time_s": stats_payload.get("detect_time(s)"),
            "total_distance_pixels": stats_payload.get("Total Distance (pixels)"),
            "region_summary_lines": region_lines,
            "zero_regions": zero_regions,
        }
    if raw_summary:
        facts["raw_trajectory_summary"] = raw_summary

    section_specs = select_section_specs(report_mode, galleries, raw_summary)

    return {
        "manifest_version": 2,
        "project_path": str(project_path),
        "project_name": scan_payload["project_name"],
        "report_title": f"{scan_payload['project_name']} 分析报告",
        "report_goal": "results-summary",
        "scan": scan_payload,
        "report_mode": report_mode,
        "report_mode_reason": report_mode_reason,
        "facts": facts,
        "galleries": galleries,
        "section_bodies": build_section_bodies(section_specs),
    }


def extract_body_text(section_entry: Any) -> str:
    if isinstance(section_entry, dict):
        return str(section_entry.get("body", "")).strip()
    if isinstance(section_entry, str):
        return section_entry.strip()
    return ""


def assemble_render_context(manifest: dict[str, Any]) -> dict[str, Any]:
    section_bodies = manifest.get("section_bodies")
    if not isinstance(section_bodies, dict):
        raise ValueError("manifest.section_bodies must be an object.")

    galleries = manifest["galleries"]
    project_path = Path(manifest["project_path"])
    context: dict[str, Any] = {
        "report_title": manifest["report_title"],
        "project_path": manifest["project_path"],
        "report_mode": manifest["report_mode"],
        "report_goal": manifest.get("report_goal") or "results-summary",
        "heatmap_gallery": build_gallery(galleries["heatmap"], project_path),
        "radar_gallery": build_gallery(galleries["radar"], project_path),
        "stats_gallery": build_gallery(galleries["stats"], project_path),
        "cluster_gallery": build_gallery(galleries["cluster"], project_path),
    }

    for spec in SECTION_SPECS:
        entry = section_bodies.get(spec["body_key"])
        body_text = extract_body_text(entry)
        context[spec["body_key"]] = body_text

        gallery_key = spec.get("gallery_key")
        if gallery_key:
            context.setdefault(gallery_key, "")

        enabled = bool(entry) and bool(body_text or context.get(gallery_key or "", ""))
        context[spec["section_key"]] = render_section(spec["template"], context, enabled=enabled)

    return context


def render_report_markdown(manifest: dict[str, Any]) -> str:
    context = assemble_render_context(manifest)
    return render_template(read_text(ASSETS_DIR / "report_template_cn.md"), context).strip() + "\n"


def render_report_html(manifest: dict[str, Any], markdown_text: str | None = None) -> str:
    markdown_body = markdown_text or render_report_markdown(manifest)
    title_line = f"# {manifest['report_title']}"
    if markdown_body.startswith(title_line):
        markdown_body = markdown_body[len(title_line):].lstrip()

    image_src_transform = build_embedded_image_transform()

    html_context = {
        "report_title": manifest["report_title"],
        "project_path": manifest["project_path"],
        "report_mode": manifest["report_mode"],
        "report_goal": manifest.get("report_goal") or "results-summary",
        "body_html": markdown_to_html(markdown_body, image_src_transform=image_src_transform),
    }
    return render_template(read_text(ASSETS_DIR / "report_template_cn.html"), html_context)
