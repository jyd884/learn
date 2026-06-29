from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from lab4.config import AnalysisPaths
from lab4.observers import PipelineObserver


@dataclass
class AnalysisContext:
    paths: AnalysisPaths
    data: dict[str, Any] = field(default_factory=dict)
    reviews: list[tuple[str, str]] = field(default_factory=list)


class AnalysisTask(ABC):
    name: str

    def run(self, context: AnalysisContext) -> None:
        review = self.execute(context)
        context.reviews.append((self.name, review))

    @abstractmethod
    def execute(self, context: AnalysisContext) -> str:
        raise NotImplementedError


@dataclass
class AnalysisPipeline:
    tasks: list[AnalysisTask]
    observers: list[PipelineObserver]

    def run(self, context: AnalysisContext) -> None:
        context.paths.ensure()
        for task in self.tasks:
            for observer in self.observers:
                observer.on_task_started(task.name)
            task.run(context)
            review = context.reviews[-1][1]
            for observer in self.observers:
                observer.on_task_finished(task.name, review)
