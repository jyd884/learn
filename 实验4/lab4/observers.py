from __future__ import annotations

from abc import ABC, abstractmethod


class PipelineObserver(ABC):
    @abstractmethod
    def on_task_started(self, task_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_task_finished(self, task_name: str, review: str) -> None:
        raise NotImplementedError


class ConsoleObserver(PipelineObserver):
    def on_task_started(self, task_name: str) -> None:
        print(f"[START] {task_name}")

    def on_task_finished(self, task_name: str, review: str) -> None:
        print(f"[DONE]  {task_name}")
        print(f"[REVIEW] {review}")
