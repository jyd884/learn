# 实验4：行为型设计模式分析与应用

本目录给出一个可直接在 VSCode 中复现的完整实验4实现，覆盖：

- 作业1：工艺参数字段提取与初步统计；
- 实验2：工艺表扩展字段导入、品质检验表导入；
- 实验3：定性/定量字段提取、上下界解析、`IsOK` 一致性校验；
- 实验4：8x10 相关性分析矩阵、5 个定量字段回归预测器、Word 实验报告生成。

## 目录结构

```text
实验4/
├── lab4/                  # 核心代码
├── outputs/               # 运行后自动生成
├── requirements.txt       # 依赖版本
├── run_analysis.py        # 统一入口
├── 品质检验*.xlsx
├── HT_工序纪录明细查询*.xlsx
└── 2026春-实验4行为型设计模式分析与应用-姓名-学号-周三.doc
```

## 复现步骤

1. 在 VSCode 终端进入本目录：

   ```bash
   cd /home/runner/work/learn/learn/实验4
   ```

2. 建议创建虚拟环境：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 执行实验：

   ```bash
   python run_analysis.py --data-dir . --output-dir outputs
   ```

## 主要输出

- `outputs/process_feature_table.csv`：工艺宽表；
- `outputs/quality_validation_field_summary.csv`：品质字段解析与 `IsOK` 校验汇总；
- `outputs/quality_validation_mismatches.csv`：`IsOK` 不一致明细；
- `outputs/material_purity_summary.csv`：物料品号纯度统计；
- `outputs/correlation_matrix_top10.csv`：8x10 相关性矩阵；
- `outputs/correlation_field_ranking.csv`：定量字段相关性排序；
- `outputs/correlation_by_material.csv`：按物料品号细分的相关性结果；
- `outputs/regression_metrics.csv`：5 个回归器指标；
- `outputs/regression_predictions.csv`：测试集预测明细；
- `outputs/figures/*.png`：UML 图与实验图；
- `outputs/实验4行为型设计模式分析与应用-完成版.docx`：最终实验报告。

## 设计说明

- **Template Method（模板方法）**：统一任务执行流程；
- **Strategy（策略模式）**：区分定量/定性字段校验逻辑；
- **Observer（观察者模式）**：在流水线运行中输出阶段日志与阶段回顾。
