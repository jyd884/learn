from __future__ import annotations

import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, precision_score, r2_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from lab4.config import (
    CORRELATION_MIN_SAMPLES,
    MATERIAL_CORRELATION_MIN_SAMPLES,
    PROCESS_FEATURES,
    RANDOM_STATE,
    TOP_CORRELATION_FIELDS,
    TOP_REGRESSION_FIELDS,
)
from lab4.pipeline import AnalysisContext, AnalysisTask
from lab4.reporting import generate_report
from lab4.validation import (
    QualitativeValidationStrategy,
    QuantitativeValidationStrategy,
    ValidationOutcome,
)


RANGE_PATTERN = re.compile(r"([-+]?\d+(?:\.\d+)?)\s*≤\s*V\s*≤\s*([-+]?\d+(?:\.\d+)?)")
GE_PATTERN = re.compile(r"V\s*≥\s*([-+]?\d+(?:\.\d+)?)")
LE_PATTERN = re.compile(r"V\s*≤\s*([-+]?\d+(?:\.\d+)?)")
EQ_NUM_PATTERN = re.compile(r"V\s*=\s*([-+]?\d+(?:\.\d+)?)")
EQ_TEXT_PATTERN = re.compile(r"V\s*=\s*(.+)")


@dataclass(slots=True)
class RegressionArtifact:
    metrics: pd.DataFrame
    predictions: pd.DataFrame
    importances: pd.DataFrame


class DataPreparationTask(AnalysisTask):
    name = "数据准备"

    def execute(self, context: AnalysisContext) -> str:
        paths = context.paths
        process_files = sorted(paths.data_dir.glob("HT_*.xlsx"))
        quality_files = sorted(paths.data_dir.glob("品质检验*.xlsx"))
        process_long = pd.concat(
            [pd.read_excel(file).assign(source_file=file.name) for file in process_files],
            ignore_index=True,
        )
        quality_raw = pd.concat(
            [pd.read_excel(file).assign(source_file=file.name) for file in quality_files],
            ignore_index=True,
        )

        process_long = strip_object_columns(process_long)
        quality_raw = strip_object_columns(quality_raw)
        process_long["创建日期"] = excel_serial_to_datetime(process_long["创建日期"])
        quality_raw["生产日期"] = excel_serial_to_datetime(quality_raw["生产日期"])

        process_table = build_process_feature_table(process_long)
        quality_enriched = enrich_quality_table(quality_raw)
        process_stats = process_table[list(PROCESS_FEATURES)].describe().transpose().reset_index().rename(columns={"index": "工艺字段"})

        process_long.to_csv(paths.output_dir / "process_long_records.csv", index=False, encoding="utf-8-sig")
        process_table.to_csv(paths.output_dir / "process_feature_table.csv", index=False, encoding="utf-8-sig")
        process_stats.to_csv(paths.output_dir / "process_feature_statistics.csv", index=False, encoding="utf-8-sig")
        quality_enriched.to_csv(paths.output_dir / "quality_enriched_records.csv", index=False, encoding="utf-8-sig")

        context.data.update(
            process_long=process_long,
            quality_raw=quality_raw,
            process_table=process_table,
            quality_enriched=quality_enriched,
            process_stats=process_stats,
        )
        return "已完成工艺表/品质表导入、8个核心工艺字段抽取和前置实验所需宽表构建，符合实验1与实验2要求。"


class ValidationAndSummaryTask(AnalysisTask):
    name = "校验与汇总"

    def execute(self, context: AnalysisContext) -> str:
        paths = context.paths
        quality = context.data["quality_enriched"].copy()
        strategies = [QuantitativeValidationStrategy(), QualitativeValidationStrategy()]
        outcomes = []
        for _, row in quality.iterrows():
            outcome = ValidationOutcome(actual_pass=None, rule_source="unmatched")
            for strategy in strategies:
                if strategy.applies(row):
                    outcome = strategy.evaluate(row)
                    break
            outcomes.append(outcome)

        quality["actual_pass"] = [item.actual_pass for item in outcomes]
        quality["rule_source"] = [item.rule_source for item in outcomes]
        quality["isok_boolean"] = quality["IsOK"].map(parse_isok_flag)
        quality["isok_matches_validation"] = np.where(
            quality["actual_pass"].isna(),
            pd.NA,
            quality["isok_boolean"] == quality["actual_pass"],
        )

        material_purity = (
            quality.dropna(subset=["actual_pass"])
            .groupby("物料品名")
            .agg(
                样本数=("actual_pass", "size"),
                合格数=("actual_pass", "sum"),
            )
            .reset_index()
            .rename(columns={"物料品名": "物料品号"})
        )
        material_purity["纯度"] = material_purity["合格数"] / material_purity["样本数"]
        material_purity = material_purity.sort_values(["样本数", "纯度"], ascending=[False, False])

        validation_summary = pd.DataFrame(
            [
                {
                    "总记录数": len(quality),
                    "可判断记录数": int(quality["actual_pass"].notna().sum()),
                    "一致记录数": int((quality["isok_matches_validation"] == True).sum()),
                    "不一致记录数": int((quality["isok_matches_validation"] == False).sum()),
                    "一致率": safe_divide((quality["isok_matches_validation"] == True).sum(), quality["actual_pass"].notna().sum()),
                }
            ]
        )

        quality.to_csv(paths.output_dir / "quality_validation_results.csv", index=False, encoding="utf-8-sig")
        material_purity.to_csv(paths.output_dir / "material_purity_summary.csv", index=False, encoding="utf-8-sig")
        validation_summary.to_csv(paths.output_dir / "validation_summary.csv", index=False, encoding="utf-8-sig")

        context.data.update(
            quality_validated=quality,
            material_purity=material_purity,
            validation_summary=validation_summary,
        )
        mismatch_count = int((quality["isok_matches_validation"] == False).sum())
        return (
            f"已完成定性/定量字段解析、上下界抽取、IsOK 一致性判定与物料品号纯度统计；"
            f"共发现 {mismatch_count} 条不一致记录，符合实验3与实验4的前置要求。"
        )


class CorrelationAnalysisTask(AnalysisTask):
    name = "相关性分析"

    def execute(self, context: AnalysisContext) -> str:
        paths = context.paths
        process_table = context.data["process_table"]
        quality = context.data["quality_validated"]
        joined = build_joined_numeric_dataset(process_table, quality)

        correlation_rows: list[dict[str, object]] = []
        material_rows: list[dict[str, object]] = []
        candidates = []
        for item, group in joined.groupby("检查项目"):
            if len(group) < CORRELATION_MIN_SAMPLES:
                continue
            item_result = {"检查项目": item, "样本数": len(group)}
            max_abs_corr = -1.0
            strongest_feature = ""
            for feature in PROCESS_FEATURES:
                pair = group[[feature, "numeric_value"]].dropna()
                corr = np.nan
                pair_count = len(pair)
                if pair_count >= CORRELATION_MIN_SAMPLES and pair[feature].nunique() > 1 and pair["numeric_value"].nunique() > 1:
                    corr = pair[feature].corr(pair["numeric_value"], method="pearson")
                item_result[f"{feature}_样本数"] = pair_count
                item_result[feature] = corr
                if pd.notna(corr) and abs(corr) > max_abs_corr:
                    max_abs_corr = abs(corr)
                    strongest_feature = feature
            item_result["最大绝对相关系数"] = max_abs_corr if max_abs_corr >= 0 else np.nan
            item_result["最强相关工艺字段"] = strongest_feature
            correlation_rows.append(item_result)

        correlation_detail = pd.DataFrame(correlation_rows)
        correlation_detail = correlation_detail.dropna(subset=["最大绝对相关系数"])
        correlation_detail = correlation_detail.sort_values(
            ["最大绝对相关系数", "样本数", "检查项目"],
            ascending=[False, False, True],
        )
        top_fields = correlation_detail.head(TOP_CORRELATION_FIELDS)["检查项目"].tolist()

        matrix_numeric = correlation_detail.set_index("检查项目").loc[top_fields, list(PROCESS_FEATURES)].transpose()
        matrix_display = matrix_numeric.applymap(format_correlation)
        matrix_display.to_csv(paths.output_dir / "correlation_matrix_top10.csv", encoding="utf-8-sig")
        matrix_numeric.to_csv(paths.output_dir / "correlation_matrix_top10_numeric.csv", encoding="utf-8-sig")
        correlation_detail.to_csv(paths.output_dir / "correlation_field_ranking.csv", index=False, encoding="utf-8-sig")

        material_focus = (
            joined["物料品号"].value_counts()
            .loc[lambda s: s >= MATERIAL_CORRELATION_MIN_SAMPLES]
            .head(8)
            .index
            .tolist()
        )
        for material in material_focus:
            subset = joined[joined["物料品号"] == material]
            for item in top_fields:
                item_group = subset[subset["检查项目"] == item]
                if len(item_group) < MATERIAL_CORRELATION_MIN_SAMPLES:
                    continue
                for feature in PROCESS_FEATURES:
                    pair = item_group[[feature, "numeric_value"]].dropna()
                    if len(pair) < MATERIAL_CORRELATION_MIN_SAMPLES or pair[feature].nunique() <= 1 or pair["numeric_value"].nunique() <= 1:
                        continue
                    material_rows.append(
                        {
                            "物料品号": material,
                            "检查项目": item,
                            "工艺字段": feature,
                            "样本数": len(pair),
                            "Pearson相关系数": pair[feature].corr(pair["numeric_value"], method="pearson"),
                        }
                    )
        correlation_by_material = pd.DataFrame(material_rows)
        correlation_by_material.to_csv(paths.output_dir / "correlation_by_material.csv", index=False, encoding="utf-8-sig")

        context.data.update(
            joined_numeric=joined,
            correlation_detail=correlation_detail,
            top_correlation_fields=top_fields,
            correlation_matrix_numeric=matrix_numeric,
            correlation_by_material=correlation_by_material,
        )
        return "已基于全部可用工艺表与品质表样本完成 8x10 Pearson 相关性分析，并补充按物料品号细分的相关性结果，符合实验4第2.1项要求。"


class RegressionTask(AnalysisTask):
    name = "回归建模"

    def execute(self, context: AnalysisContext) -> str:
        paths = context.paths
        joined = context.data["joined_numeric"]
        candidate_fields = context.data["top_correlation_fields"][:TOP_REGRESSION_FIELDS]

        numeric_features = list(PROCESS_FEATURES)
        categorical_features = ["物料品号", "型号"]
        metrics_rows: list[dict[str, object]] = []
        predictions_frames = []
        importances = []

        for item in candidate_fields:
            dataset = joined[joined["检查项目"] == item].copy()
            if len(dataset) < 200:
                continue
            feature_frame = dataset[numeric_features + categorical_features]
            target = dataset["numeric_value"]
            meta = dataset[["工单号", "批号", "检查项目", "lower_bound", "upper_bound", "actual_pass", "numeric_value"]]

            x_train, x_test, y_train, y_test, meta_train, meta_test = train_test_split(
                feature_frame,
                target,
                meta,
                test_size=0.2,
                random_state=RANDOM_STATE,
            )

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
                    (
                        "cat",
                        Pipeline(
                            [
                                ("imputer", SimpleImputer(strategy="most_frequent")),
                                ("encoder", OneHotEncoder(handle_unknown="ignore")),
                            ]
                        ),
                        categorical_features,
                    ),
                ]
            )
            model = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    (
                        "regressor",
                        RandomForestRegressor(
                            n_estimators=240,
                            min_samples_leaf=2,
                            n_jobs=-1,
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            )
            model.fit(x_train, y_train)
            predictions = model.predict(x_test)

            predicted_pass = [
                classify_prediction(value, lower, upper)
                for value, lower, upper in zip(predictions, meta_test["lower_bound"], meta_test["upper_bound"], strict=False)
            ]

            metrics_rows.append(
                {
                    "检查项目": item,
                    "训练样本数": len(x_train),
                    "测试样本数": len(x_test),
                    "MAE": mean_absolute_error(y_test, predictions),
                    "RMSE": math.sqrt(mean_squared_error(y_test, predictions)),
                    "R2": r2_score(y_test, predictions),
                    "Precision": precision_score(meta_test["actual_pass"], predicted_pass, zero_division=0),
                    "Recall": recall_score(meta_test["actual_pass"], predicted_pass, zero_division=0),
                    "F1": f1_score(meta_test["actual_pass"], predicted_pass, zero_division=0),
                }
            )

            prediction_frame = meta_test.copy()
            prediction_frame["预测值"] = predictions
            prediction_frame["绝对误差"] = np.abs(predictions - y_test.to_numpy())
            prediction_frame["预测合格"] = predicted_pass
            predictions_frames.append(prediction_frame)

            feature_names = model.named_steps["preprocessor"].get_feature_names_out()
            importances.extend(
                {
                    "检查项目": item,
                    "特征": feature_name,
                    "重要性": importance,
                }
                for feature_name, importance in zip(
                    feature_names,
                    model.named_steps["regressor"].feature_importances_,
                    strict=False,
                )
            )

        metrics = pd.DataFrame(metrics_rows).sort_values("R2", ascending=False)
        prediction_results = pd.concat(predictions_frames, ignore_index=True) if predictions_frames else pd.DataFrame()
        importance_frame = (
            pd.DataFrame(importances)
            .sort_values(["检查项目", "重要性"], ascending=[True, False])
            .groupby("检查项目", group_keys=False)
            .head(12)
        )

        metrics.to_csv(paths.output_dir / "regression_metrics.csv", index=False, encoding="utf-8-sig")
        prediction_results.to_csv(paths.output_dir / "regression_predictions.csv", index=False, encoding="utf-8-sig")
        importance_frame.to_csv(paths.output_dir / "regression_feature_importance.csv", index=False, encoding="utf-8-sig")

        context.data.update(
            regression_artifact=RegressionArtifact(
                metrics=metrics,
                predictions=prediction_results,
                importances=importance_frame,
            )
        )
        return "已完成5个代表性定量字段的随机森林回归建模，并输出 MAE、RMSE、R²、Precision、Recall、F1 指标，符合实验4第2.2项要求。"


class ReportTask(AnalysisTask):
    name = "报告生成"

    def execute(self, context: AnalysisContext) -> str:
        generate_report(context)
        destination = context.paths.data_dir / context.paths.report_path.name
        shutil.copyfile(context.paths.report_path, destination)
        return "已生成 Word 实验报告、UML 图和关键结果图，报告内容覆盖实验要求、运行效果、编码逻辑与阶段回顾，符合提交要求。"


def strip_object_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.select_dtypes(include="object").columns:
        result[column] = result[column].fillna("").astype(str).str.strip()
    return result


def excel_serial_to_datetime(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    converted = pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")
    text_mask = converted.isna() & series.notna() & (series.astype(str).str.strip() != "")
    converted.loc[text_mask] = pd.to_datetime(series.loc[text_mask], errors="coerce")
    return converted


def build_process_feature_table(process_long: pd.DataFrame) -> pd.DataFrame:
    def first_non_empty(series: pd.Series) -> str | float:
        for value in series:
            if pd.notna(value) and str(value).strip() not in {"", "nan", "None"}:
                return str(value).strip()
        return np.nan

    base_columns = ["工单号", "批号", "物料品名", "物料描述", "型号", "设备名称", "工序", "生产方式", "创建日期"]
    metadata = (
        process_long[base_columns]
        .groupby("工单号", as_index=False)
        .agg(
            {
                "批号": first_non_empty,
                "物料品名": first_non_empty,
                "物料描述": first_non_empty,
                "型号": first_non_empty,
                "设备名称": first_non_empty,
                "工序": first_non_empty,
                "生产方式": first_non_empty,
                "创建日期": "max",
            }
        )
    )

    pivot = process_long.pivot_table(
        index="工单号",
        columns="项目名称",
        values="项目记录结果",
        aggfunc=first_non_empty,
    ).reset_index()
    merged = metadata.merge(pivot, on="工单号", how="left")
    merged = merged.rename(columns={"物料品名": "物料品号"})
    for feature_name, source_name in PROCESS_FEATURES.items():
        merged[feature_name] = pd.to_numeric(merged[source_name], errors="coerce")
    return merged


def enrich_quality_table(quality_raw: pd.DataFrame) -> pd.DataFrame:
    quality = quality_raw.copy()
    quality["numeric_value"] = pd.to_numeric(quality["检验值"], errors="coerce")

    parsed = quality["检验参数(标准参数为数字时无需填写)"].apply(parse_rule_text)
    quality["lower_bound"] = [item["lower_bound"] for item in parsed]
    quality["upper_bound"] = [item["upper_bound"] for item in parsed]
    quality["exact_target"] = [item["exact_target"] for item in parsed]
    quality["expected_text"] = [item["expected_text"] for item in parsed]

    numeric_standard = pd.to_numeric(quality["标准参数"], errors="coerce")
    quality.loc[quality["exact_target"].isna() & numeric_standard.notna(), "exact_target"] = numeric_standard

    quality["field_type"] = np.where(
        quality["numeric_value"].notna() | quality["lower_bound"].notna() | quality["upper_bound"].notna() | quality["exact_target"].notna(),
        "quantitative",
        "qualitative",
    )
    return quality


def parse_rule_text(value: object) -> dict[str, float | str | None]:
    text = "" if value is None else str(value).strip()
    result: dict[str, float | str | None] = {
        "lower_bound": np.nan,
        "upper_bound": np.nan,
        "exact_target": np.nan,
        "expected_text": None,
    }
    if not text or text.lower() == "nan":
        return result
    if match := RANGE_PATTERN.search(text):
        result["lower_bound"] = float(match.group(1))
        result["upper_bound"] = float(match.group(2))
        return result
    if match := GE_PATTERN.search(text):
        result["lower_bound"] = float(match.group(1))
        return result
    if match := LE_PATTERN.search(text):
        result["upper_bound"] = float(match.group(1))
        return result
    if match := EQ_NUM_PATTERN.search(text):
        result["exact_target"] = float(match.group(1))
        return result
    if match := EQ_TEXT_PATTERN.search(text):
        result["expected_text"] = match.group(1).strip()
    return result


def parse_isok_flag(value: object) -> bool | None:
    text = "" if value is None else str(value).strip()
    if text in {"1", "1.0", "True", "true"}:
        return True
    if text in {"0", "0.0", "False", "false"}:
        return False
    return None


def safe_divide(numerator: float | int, denominator: float | int) -> float | None:
    if not denominator:
        return None
    return float(numerator) / float(denominator)


def build_joined_numeric_dataset(process_table: pd.DataFrame, quality: pd.DataFrame) -> pd.DataFrame:
    numeric_quality = quality[(quality["field_type"] == "quantitative") & quality["numeric_value"].notna()].copy()
    joined = numeric_quality.merge(
        process_table[
            ["工单号", "批号", "物料品号", "型号", *PROCESS_FEATURES.keys()]
        ],
        on="工单号",
        how="inner",
        suffixes=("_quality", "_process"),
    )
    joined["批号"] = joined["批号_quality"].where(joined["批号_quality"].astype(str).str.strip() != "", joined["批号_process"])
    return joined


def format_correlation(value: float) -> str:
    if pd.isna(value):
        return ""
    if value >= 0:
        return f"正相关({value:.3f})"
    return f"负相关({value:.3f})"


def classify_prediction(prediction: float, lower: float | None, upper: float | None) -> bool:
    if pd.notna(lower) and pd.notna(upper):
        return bool(lower <= prediction <= upper)
    if pd.notna(lower):
        return bool(prediction >= lower)
    if pd.notna(upper):
        return bool(prediction <= upper)
    return True
