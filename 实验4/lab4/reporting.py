from __future__ import annotations

import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from lab4.config import PROCESS_FEATURES
from lab4.pipeline import AnalysisContext


def generate_report(context: AnalysisContext) -> None:
    figure_paths = generate_figures(context)
    document = Document()
    add_cover(document)
    add_purpose_section(document)
    add_method_section(document, context)
    add_results_section(document, context, figure_paths)
    add_summary_section(document)
    document.save(context.paths.report_path)


def add_cover(document: Document) -> None:
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("深圳大学实验报告\n软件体系结构与设计模式\n实验4 行为型设计模式分析与应用")
    run.bold = True
    run.font.size = document.styles["Title"].font.size

    info = document.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run(
        "\n学院：待填写\n专业：待填写\n指导教师：毛斐巧\n报告人：待填写    学号：待填写    班级：待填写\n"
        "实验时间：2026年6月3日-2026年6月26日\n"
        "实验报告提交时间：待填写\n"
    )
    document.add_page_break()


def add_purpose_section(document: Document) -> None:
    document.add_heading("一、实验目的与要求", level=1)
    for line in [
        "1. 理论联系实际理解 GoF 行为型设计模式，并将其应用于真实数据分析代码。",
        "2. 在不再处理备注信息与操作机手纯度统计的前提下，完成前置实验功能整合。",
        "3. 基于全部可用《HT_工序纪录明细查询表》和《品质检验数据表》完成相关性分析与回归预测。",
        "4. 输出可复现代码、关键结果文件、UML 图和 Word 实验报告。",
    ]:
        document.add_paragraph(line)


def add_method_section(document: Document, context: AnalysisContext) -> None:
    document.add_heading("二、实现方案与行为型设计模式", level=1)
    document.add_paragraph(
        "整体项目采用“模板方法 + 策略 + 观察者”三种行为型设计模式。"
        "模板方法统一控制任务执行顺序；策略模式区分定量与定性校验；"
        "观察者模式在流水线执行期间输出阶段日志与阶段回顾。"
    )

    table = document.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    headers = ["类名", "实验1", "实验2", "实验3", "实验4"]
    for index, text in enumerate(headers):
        table.rows[0].cells[index].text = text
    rows = [
        ("DataPreparationTask", "抽取8个工艺字段并做初步统计", "扩展导入工艺表/品质表", "为字段校验提供原始数据", "作为整体分析入口"),
        ("ValidationAndSummaryTask", "—", "—", "解析上下界并校验 IsOK", "输出纯度统计和校验汇总"),
        ("CorrelationAnalysisTask", "—", "—", "—", "计算8x10 Pearson 相关矩阵"),
        ("RegressionTask", "—", "—", "—", "训练5个随机森林回归器"),
        ("ReportTask", "汇总统计结果", "整理导入说明", "展示校验效果", "生成 UML 图与 Word 报告"),
    ]
    for row_values in rows:
        row = table.add_row().cells
        for index, text in enumerate(row_values):
            row[index].text = text

    document.add_paragraph("阶段回顾：代码结构已覆盖实验1~实验4要求，且实验4明确移除了备注信息与操作机手纯度统计。")


def add_results_section(document: Document, context: AnalysisContext, figure_paths: dict[str, Path]) -> None:
    document.add_heading("三、实践过程、结果与阶段回顾", level=1)
    reviews = document.add_paragraph()
    reviews.add_run("流水线阶段回顾：").bold = True
    for name, review in context.reviews:
        document.add_paragraph(f"{name}：{review}", style="List Bullet")

    validation_summary = context.data["validation_summary"].iloc[0].to_dict()
    document.add_paragraph(
        "数据准备与实验3校验结果："
        f"总记录数 {int(validation_summary['总记录数'])}，"
        f"可判断记录数 {int(validation_summary['可判断记录数'])}，"
        f"一致记录数 {int(validation_summary['一致记录数'])}，"
        f"不一致记录数 {int(validation_summary['不一致记录数'])}，"
        f"一致率 {validation_summary['一致率']:.4f}。"
    )

    document.add_heading("1. 8x10 相关性矩阵", level=2)
    matrix = context.data["correlation_matrix_numeric"]
    write_dataframe_table(document, matrix.reset_index().rename(columns={"index": "工艺字段"}), max_rows=9)
    document.add_paragraph(
        "说明：表中使用 Pearson 相关系数衡量线性正负相关；数值越接近 1 或 -1，相关性越强。"
        "样本来自全部可用工艺表和品质检验表，并额外输出了按物料品号细分的相关性结果。"
    )

    document.add_heading("2. 回归预测结果", level=2)
    metrics = context.data["regression_artifact"].metrics.copy()
    write_dataframe_table(document, metrics.round(4), max_rows=6)
    document.add_paragraph(
        "说明：MAE/RMSE/R² 用于度量数值预测误差，Precision/Recall/F1 通过“预测值是否落入该样本检验标准范围”"
        "来衡量预测结果在质量判定意义上的准确度。"
    )

    document.add_heading("3. UML 图与运行效果", level=2)
    for key in [
        "class_diagram",
        "activity_diagram",
        "sequence_extraction",
        "sequence_validation",
        "sequence_correlation",
        "sequence_regression",
    ]:
        document.add_paragraph(figure_paths[key].stem)
        document.add_picture(str(figure_paths[key]), width=Inches(6.5))

    document.add_heading("4. 关键编码逻辑", level=2)
    document.add_paragraph(
        "（1）工艺表先按工单号聚合，再把“项目名称-项目记录结果”透视为宽表；"
        "（2）品质检验表通过正则表达式提取上下界、定性预期文本和数值目标；"
        "（3）定量字段执行区间校验，定性字段根据 OK/NG 或文本等值判断；"
        "（4）相关性分析按检查项目逐项计算 8 个核心工艺字段的 Pearson 系数；"
        "（5）回归部分使用随机森林，同时保留物料品号与型号的类别信息。"
    )
    add_code_change_section(document, context)


def add_summary_section(document: Document) -> None:
    document.add_heading("四、实验总结与体会", level=1)
    document.add_paragraph(
        "本次实验将前置实验功能统一到同一流水线，并通过行为型设计模式降低了后续扩展的成本。"
        "与直接堆叠脚本相比，模板方法保证步骤固定，策略模式把字段校验差异从主流程中剥离，"
        "观察者模式则使阶段回顾与日志输出更清晰。实验结果表明，基于全量历史样本做相关性与回归分析，"
        "可以更稳定地定位与质量指标最相关的工艺参数。"
    )
    document.add_heading("五、成绩评定及评语", level=1)
    document.add_paragraph("1. 指导老师批阅意见：\n\n")
    document.add_paragraph("2. 成绩评定：\n\n")


def write_dataframe_table(document: Document, frame: pd.DataFrame, max_rows: int) -> None:
    limited = frame.head(max_rows)
    table = document.add_table(rows=1, cols=len(limited.columns))
    table.style = "Table Grid"
    for index, column in enumerate(limited.columns):
        table.rows[0].cells[index].text = str(column)
    for _, row in limited.iterrows():
        cells = table.add_row().cells
        for index, value in enumerate(row):
            if pd.isna(value):
                cells[index].text = ""
            elif isinstance(value, float):
                cells[index].text = f"{value:.4f}"
            else:
                cells[index].text = str(value)


def add_code_change_section(document: Document, context: AnalysisContext) -> None:
    document.add_heading("5. 代码新增与删减体现", level=2)
    document.add_paragraph("以下内容直接摘录自当前实验4源码相对基线版本的实际差异，用于体现新增与删减位置。")
    changes = collect_code_changes(context)
    if not changes:
        document.add_paragraph("当前未检测到可展示的源码新增或删减。")
        return

    for relative_path, hunks in changes:
        document.add_paragraph(f"文件：{relative_path}")
        for header, lines in hunks:
            run = document.add_paragraph().add_run(f"{header}\n" + "\n".join(lines))
            run.font.name = "Courier New"
            run.font.size = Pt(8.5)


def collect_code_changes(context: AnalysisContext) -> list[tuple[str, list[tuple[str, list[str]]]]]:
    repo_root = context.paths.data_dir.parent
    targets = [
        str((context.paths.data_dir / "lab4").relative_to(repo_root)),
        str((context.paths.data_dir / "run_analysis.py").relative_to(repo_root)),
    ]
    baseline = find_baseline_commit(repo_root, targets)
    if not baseline:
        return []

    diff_result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--unified=0", "--no-color", baseline, "--", *targets],
        capture_output=True,
        text=True,
        check=False,
    )
    if diff_result.returncode not in {0, 1} or not diff_result.stdout.strip():
        return []
    return parse_code_change_diff(diff_result.stdout)


def find_baseline_commit(repo_root: Path, targets: list[str]) -> str:
    revision_result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-list", "--reverse", "HEAD", "--", *targets],
        capture_output=True,
        text=True,
        check=False,
    )
    if revision_result.returncode != 0:
        return ""
    revisions = [line.strip() for line in revision_result.stdout.splitlines() if line.strip()]
    return revisions[0] if revisions else ""


def parse_code_change_diff(diff_text: str) -> list[tuple[str, list[tuple[str, list[str]]]]]:
    max_files = 6
    max_lines_per_file = 80
    changes: list[tuple[str, list[tuple[str, list[str]]]]] = []
    current_path = ""
    current_hunks: list[tuple[str, list[str]]] = []
    current_header = ""
    current_lines: list[str] = []
    line_count = 0

    def flush_hunk() -> None:
        nonlocal current_header, current_lines
        if current_header and current_lines:
            current_hunks.append((current_header, current_lines))
        current_header = ""
        current_lines = []

    def flush_file() -> None:
        nonlocal current_path, current_hunks, line_count
        flush_hunk()
        if current_path and current_hunks and len(changes) < max_files:
            changes.append((current_path, current_hunks))
        current_path = ""
        current_hunks = []
        line_count = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            flush_file()
            continue
        if raw_line.startswith("+++ "):
            candidate = raw_line[4:].strip().strip('"')
            if candidate.startswith("b/"):
                candidate = candidate[2:]
            current_path = candidate
            continue
        if raw_line.startswith("@@ "):
            flush_hunk()
            current_header = raw_line
            continue
        if raw_line.startswith(("+++", "---")):
            continue
        if not raw_line.startswith(("+", "-")) or line_count >= max_lines_per_file:
            continue
        current_lines.append(raw_line)
        line_count += 1

    flush_file()
    return changes


def generate_figures(context: AnalysisContext) -> dict[str, Path]:
    output_dir = context.paths.figure_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = {
        "class_diagram": output_dir / "class_diagram.png",
        "activity_diagram": output_dir / "activity_diagram.png",
        "sequence_extraction": output_dir / "sequence_extraction.png",
        "sequence_validation": output_dir / "sequence_validation.png",
        "sequence_correlation": output_dir / "sequence_correlation.png",
        "sequence_regression": output_dir / "sequence_regression.png",
    }
    draw_class_diagram(figures["class_diagram"])
    draw_activity_diagram(figures["activity_diagram"])
    draw_sequence_diagram(
        figures["sequence_extraction"],
        "Field Extraction Sequence",
        ["Runner", "Pipeline", "DataPreparationTask", "Pandas"],
        [
            (0, 1, "run()"),
            (1, 2, "execute()"),
            (2, 3, "read_excel()"),
            (3, 2, "process data"),
            (2, 1, "wide table"),
        ],
    )
    draw_sequence_diagram(
        figures["sequence_validation"],
        "Validation Sequence",
        ["Pipeline", "ValidationTask", "QuantitativeStrategy", "QualitativeStrategy"],
        [
            (0, 1, "execute()"),
            (1, 2, "quantitative row"),
            (2, 1, "pass/fail"),
            (1, 3, "qualitative row"),
            (3, 1, "pass/fail"),
        ],
    )
    draw_sequence_diagram(
        figures["sequence_correlation"],
        "Correlation Sequence",
        ["Pipeline", "CorrelationTask", "Joined Dataset", "Pearson Analyzer"],
        [
            (0, 1, "execute()"),
            (1, 2, "join numeric rows"),
            (2, 1, "group by item"),
            (1, 3, "compute corr"),
            (3, 1, "8x10 matrix"),
        ],
    )
    draw_sequence_diagram(
        figures["sequence_regression"],
        "Regression Sequence",
        ["Pipeline", "RegressionTask", "sklearn", "RandomForest"],
        [
            (0, 1, "execute()"),
            (1, 2, "train/test split"),
            (2, 3, "fit()"),
            (3, 2, "predict()"),
            (2, 1, "metrics"),
        ],
    )
    return figures


def draw_class_diagram(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis("off")
    boxes = [
        (0.06, 0.68, 0.24, 0.20, "AnalysisPipeline", ["+ tasks", "+ observers", "+ run(context)"]),
        (0.38, 0.68, 0.24, 0.20, "AnalysisTask", ["+ name", "+ run()", "+ execute()"]),
        (0.70, 0.68, 0.24, 0.20, "PipelineObserver", ["+ on_task_started()", "+ on_task_finished()"]),
        (0.10, 0.34, 0.22, 0.16, "DataPreparationTask", ["reads Excel", "builds wide table"]),
        (0.38, 0.34, 0.22, 0.16, "ValidationTask", ["Strategy based", "validates IsOK"]),
        (0.66, 0.34, 0.22, 0.16, "CorrelationTask", ["Pearson matrix", "material details"]),
        (0.26, 0.08, 0.22, 0.16, "RegressionTask", ["RandomForest", "metrics"]),
        (0.56, 0.08, 0.22, 0.16, "ReportTask", ["UML figures", "Word report"]),
    ]
    for x, y, w, h, title, lines in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, linewidth=1.5))
        ax.text(x + w / 2, y + h - 0.04, title, ha="center", va="top", fontsize=11, fontweight="bold")
        ax.plot([x, x + w], [y + h - 0.06, y + h - 0.06], color="black", linewidth=1)
        for offset, line in enumerate(lines):
            ax.text(x + 0.02, y + h - 0.09 - offset * 0.04, line, ha="left", va="top", fontsize=9)
    arrow(ax, (0.50, 0.68), (0.21, 0.50), "compose")
    arrow(ax, (0.50, 0.68), (0.49, 0.50), "compose")
    arrow(ax, (0.50, 0.68), (0.77, 0.50), "compose")
    arrow(ax, (0.82, 0.68), (0.82, 0.50), "observe")
    arrow(ax, (0.49, 0.34), (0.49, 0.24), "inherit")
    arrow(ax, (0.77, 0.34), (0.67, 0.24), "inherit")
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def draw_activity_diagram(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.axis("off")
    nodes = [
        (0.5, 0.93, "Start"),
        (0.5, 0.80, "Load Excel files"),
        (0.5, 0.67, "Build process wide table"),
        (0.5, 0.54, "Parse quality rules"),
        (0.5, 0.41, "Validate IsOK & purity"),
        (0.5, 0.28, "Compute 8x10 correlation"),
        (0.5, 0.15, "Train 5 regressors"),
        (0.5, 0.03, "Export CSV, figures, docx"),
    ]
    for x, y, label in nodes:
        ax.add_patch(plt.Rectangle((x - 0.18, y - 0.04), 0.36, 0.08, fill=False, linewidth=1.5))
        ax.text(x, y, label, ha="center", va="center", fontsize=10)
    for (_, y1, _), (_, y2, _) in zip(nodes, nodes[1:], strict=False):
        arrow(ax, (0.5, y1 - 0.04), (0.5, y2 + 0.04), "")
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def draw_sequence_diagram(path: Path, title: str, actors: list[str], messages: list[tuple[int, int, str]]) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis("off")
    x_positions = [0.12 + index * 0.25 for index in range(len(actors))]
    for x, actor in zip(x_positions, actors, strict=False):
        ax.text(x, 0.94, actor, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.plot([x, x], [0.15, 0.88], linestyle="--", color="black", linewidth=1)
    y = 0.82
    for start, end, label in messages:
        x1 = x_positions[start]
        x2 = x_positions[end]
        arrow(ax, (x1, y), (x2, y), label)
        y -= 0.12
    ax.text(0.5, 0.05, title, ha="center", va="center", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def arrow(ax, start: tuple[float, float], end: tuple[float, float], label: str) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="->", linewidth=1.4),
    )
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.02, label, ha="center", va="bottom", fontsize=9)
