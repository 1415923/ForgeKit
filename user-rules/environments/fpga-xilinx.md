# 用户级环境补充：FPGA / Xilinx

仅在 FPGA、Vivado、Vitis、Vitis HLS、PYNQ、板卡项目中读取。

## 已发现环境

- Xilinx 根目录：`D:\Xilinx`
- Vivado：`D:\Xilinx\Vivado\2023.2`
- Vitis：`D:\Xilinx\Vitis\2023.2`
- Vitis HLS：`D:\Xilinx\Vitis_HLS\2023.2`
- DocNav：`D:\Xilinx\DocNav`
- Model Composer：`D:\Xilinx\Model_Composer`
- SharedData：`D:\Xilinx\SharedData`

## 使用规则

- FPGA、Vitis HLS、Vivado 相关命令通常需要先加载对应版本环境脚本，不能假设 PATH 中直接可用。
- 运行综合、仿真、导出 bitstream、调用硬件或 GUI 前，应先确认项目脚本和权限要求。
- 板卡操作、bitstream 下载、硬件连接默认需要用户确认。
