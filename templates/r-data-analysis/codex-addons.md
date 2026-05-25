# R Data Analysis 项目规则补充

## 代码结构

```text
R/
tests/
data-raw/
reports/
renv.lock
```

## 开发规则

- R 项目的重点是可复现性、数据来源、随机种子、报告输出和结果追踪。
- 推荐识别是否使用 renv，但不默认执行 restore。
- 数据文件、隐私数据、大型二进制和模型产物必须有 Git 策略。
- 统计模型、清洗逻辑和图表输出变化要记录假设和影响。
- reticulate、conda、venv、系统库和 Pandoc/LaTeX 依赖要分开说明。

## 测试

- R package 或函数库优先使用 testthat。
- 报告项目要验证渲染结果和关键图表/表格。
- 随机流程必须设置或记录 seed。
- 外部数据源和隐私数据测试前确认替代数据。
