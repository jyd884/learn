from __future__ import annotations

import argparse
from pathlib import Path

from lab4.analysis import (
    CorrelationAnalysisTask,
    DataPreparationTask,
    RegressionTask,
    ReportTask,
    ValidationAndSummaryTask,
)
from lab4.config import AnalysisPaths
from lab4.observers import ConsoleObserver
from lab4.pipeline import AnalysisContext, AnalysisPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="实验4综合分析入口")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="输入数据目录，默认当前实验4目录",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="输出目录",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = AnalysisPaths.from_root(args.data_dir.resolve(), args.output_dir.resolve())
    context = AnalysisContext(paths=paths)
    pipeline = AnalysisPipeline(
        tasks=[
            DataPreparationTask(),
            ValidationAndSummaryTask(),
            CorrelationAnalysisTask(),
            RegressionTask(),
            ReportTask(),
        ],
        observers=[ConsoleObserver()],
    )
    pipeline.run(context)


if __name__ == "__main__":
    main()
