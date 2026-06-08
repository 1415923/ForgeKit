# FPGA Vivado / Vitis 模板

适用于 FPGA、Vivado、Vitis、Vitis HLS、PYNQ、板卡验证等项目。

仅在项目涉及 FPGA / HLS / Vivado / Vitis 时加载。Java、前端、普通后端项目不要加载本模板。

## Codex 启动建议

- 推荐启动目录：硬件工程根目录，或包含 HLS/Vivado/Vitis 脚本的子目录。
- 优先阅读：`README`、`scripts/`、`src/`、`tb/`、`constraints/`、`*.tcl`、板卡说明、已有验证日志。
- Ignore guidance / 避免默认读取：`*.bit`、`*.xsa`、`*.runs/`、`*.cache/`、`*.hw/`、大型波形、综合输出、二进制输入输出。

## 符号搜索 / 工具索引

- 常规软件 LSP 不适合作为主要入口，优先依赖 Vivado/Vitis 工程脚本、Tcl、HLS top 和 testbench 建立上下文。
- HLS 优先查顶层函数、接口 pragma、testbench、脚本中的 top 设置。
- Vivado 优先查 block design、约束、IP 生成脚本、综合/实现 Tcl。
- Vitis 优先查 platform、application、linker script、kernel 配置。
- 常用关键词：`#pragma HLS`、`ap_int`、`ap_axi`、`s_axilite`、`m_axi`、`create_project`、`set_top`、`open_project`、`launch_runs`。

## 局部验证

- HLS 修改：优先跑 C simulation，再考虑 synthesis。
- RTL 或约束修改：先跑 lint/仿真/综合前检查，再跑完整综合。
- 板卡相关操作、bitstream 下载、GUI 和长耗时流程必须先确认。
- 生成物体积大，验证结果优先记录日志摘要，不把大型文件读入上下文。

环境参考：

- Xilinx 根目录：使用 `$XILINX_ROOT`、`$XILINX_VIVADO`、`$XILINX_VITIS` 或项目文档记录的安装路径。
- Windows 示例：`C:\path\to\Xilinx\Vivado\<version>`。
- Linux 示例：`/opt/Xilinx/Vivado/<version>`。
- 本机私有安装路径应写入 `user-rules/` 或项目私有文档，不写入通用模板。
