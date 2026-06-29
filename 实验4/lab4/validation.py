from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(slots=True)
class ValidationOutcome:
    actual_pass: bool | None
    rule_source: str


class ValidationStrategy(ABC):
    @abstractmethod
    def applies(self, row: pd.Series) -> bool:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, row: pd.Series) -> ValidationOutcome:
        raise NotImplementedError


class QuantitativeValidationStrategy(ValidationStrategy):
    def applies(self, row: pd.Series) -> bool:
        return row.get("field_type") == "quantitative"

    def evaluate(self, row: pd.Series) -> ValidationOutcome:
        value = row.get("numeric_value")
        if pd.isna(value):
            return ValidationOutcome(actual_pass=None, rule_source="missing_numeric_value")

        lower = row.get("lower_bound")
        upper = row.get("upper_bound")
        if pd.notna(lower) and pd.notna(upper):
            return ValidationOutcome(actual_pass=bool(lower <= value <= upper), rule_source="range")
        if pd.notna(lower):
            return ValidationOutcome(actual_pass=bool(value >= lower), rule_source="lower_bound")
        if pd.notna(upper):
            return ValidationOutcome(actual_pass=bool(value <= upper), rule_source="upper_bound")
        exact = row.get("exact_target")
        if pd.notna(exact):
            return ValidationOutcome(actual_pass=bool(abs(value - exact) <= 1e-9), rule_source="exact")
        return ValidationOutcome(actual_pass=None, rule_source="no_numeric_rule")


class QualitativeValidationStrategy(ValidationStrategy):
    POSITIVE_VALUES = {"ok", "pass", "true", "合格", "是"}
    NEGATIVE_VALUES = {"ng", "fail", "false", "不合格", "否"}

    def applies(self, row: pd.Series) -> bool:
        return row.get("field_type") == "qualitative"

    def evaluate(self, row: pd.Series) -> ValidationOutcome:
        value = normalize_text(row.get("检验值"))
        if value in self.POSITIVE_VALUES:
            return ValidationOutcome(actual_pass=True, rule_source="qualitative_value")
        if value in self.NEGATIVE_VALUES:
            return ValidationOutcome(actual_pass=False, rule_source="qualitative_value")
        expected_text = normalize_text(row.get("expected_text"))
        if value and expected_text:
            return ValidationOutcome(actual_pass=value == expected_text, rule_source="expected_text")
        return ValidationOutcome(actual_pass=None, rule_source="no_qualitative_rule")


def normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip().replace(" ", "")
    return text.casefold()
