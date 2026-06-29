from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROCESS_FEATURES = {
    "缆芯外径": "缆芯外径（mm)",
    "护套外径": "护套外径(mm)",
    "挤出内模": "挤出内模(mm)",
    "挤出外模": "挤出外模(mm)",
    "螺杆速度": "螺杆速度(rpm)-(挤塑主机速度)（转/分）",
    "螺杆电流": "螺杆电流（A）",
    "生产速度": "生产速度（米/分）",
    "实际生产速度": "实际生产速度（m/min）",
}

TOP_CORRELATION_FIELDS = 10
TOP_REGRESSION_FIELDS = 5
CORRELATION_MIN_SAMPLES = 200
MATERIAL_CORRELATION_MIN_SAMPLES = 30
RANDOM_STATE = 42


@dataclass(slots=True)
class AnalysisPaths:
    data_dir: Path
    output_dir: Path
    figure_dir: Path
    report_path: Path

    @classmethod
    def from_root(cls, data_dir: Path, output_dir: Path) -> "AnalysisPaths":
        figure_dir = output_dir / "figures"
        report_path = output_dir / "实验4行为型设计模式分析与应用-完成版.docx"
        return cls(data_dir=data_dir, output_dir=output_dir, figure_dir=figure_dir, report_path=report_path)

    def ensure(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figure_dir.mkdir(parents=True, exist_ok=True)
