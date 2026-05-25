# R Data Analysis 模板

适用于 R 数据分析、科研脚本、报表、Shiny、小型数据产品和可复现实验。

不适用于第一版就处理生产级大数据平台、受监管隐私数据、复杂 MLOps 或大型混合 Python/R 平台；这些需要单独治理。

## Codex 启动建议

- 推荐启动目录：包含 `.Rproj`、`renv.lock`、`DESCRIPTION`、`R/` 或 `reports/` 的项目根目录。
- 初始化前必须确认：分析脚本、R package、Shiny、Quarto/R Markdown 报告还是混合项目；数据来源；隐私边界。
- 优先阅读：`README.md`、`renv.lock`、`DESCRIPTION`、`R/`、`tests/`、`data-raw/`、`reports/`、`app.R`。
- Ignore guidance / 避免默认读取：`.Rhistory`、`.RData`、`renv/library/`、大型数据、隐私数据、模型产物。

## 符号搜索 / LSP

- 优先使用 R language server / RStudio 索引函数、包依赖和文档。
- CLI 中按 function、dataset、report、Shiny server/ui、testthat、renv、targets/drake 搜索。
- 常用关键词：`library(`、`renv::`、`test_that`、`shinyApp`、`render`、`set.seed`、`read_`、`write_`。
- 修改数据输入、随机种子、清洗逻辑、统计模型或报告输出前，先确认可复现性。

## 局部验证

- 修改函数：运行相关 testthat。
- 修改报告：渲染相关 R Markdown/Quarto。
- 修改依赖：确认 renv 和 R 版本。
- 修改数据文件、隐私数据或大型二进制前，先确认 Git 策略。
