# R Data Analysis 命令示例

```powershell
R --version
Rscript -e "sessionInfo()"
Rscript -e "renv::status()"
Rscript -e "testthat::test_dir('tests')"
Rscript -e "rmarkdown::render('report.Rmd')"
```

## Local validation / 局部验证优先级

```powershell
Rscript -e "sessionInfo()"
Rscript -e "renv::status()"
Rscript -e "testthat::test_dir('tests')"
```

注意：

- `renv::restore()` 会下载依赖并改本地库，先确认。
- 报告渲染可能依赖 Pandoc、LaTeX、系统库或外部数据。
- 大型数据、隐私数据、模型产物和随机结果写入前必须确认。
- 如果项目用 Python/reticulate/conda，先确认环境边界。
