# FPGA Vivado / Vitis 项目规则补充

## 适用范围

- Vivado 工程。
- Vitis / Vitis HLS 工程。
- C/C++ HLS kernel。
- RTL、IP、block design、bitstream。
- PYNQ / Zynq / ZCU / KV260 等板卡相关项目。

## 开发规则

- 先确认目标板卡、芯片型号、时钟、接口协议和资源约束。
- 不默认运行综合、实现、bitstream 生成；这些命令耗时长且会生成大量文件。
- HLS 修改需要明确：
  - 输入输出接口。
  - 数据类型和定点位宽。
  - pipeline、unroll、dataflow 等 pragma 目标。
  - 资源、延迟、吞吐约束。
- RTL 或 block design 修改需要明确时钟域、复位、AXI 接口和约束文件。
- 板卡操作、下载 bitstream、访问硬件前必须确认。

## 目录建议

```text
hardware/
├─ hls/
├─ rtl/
├─ vivado/
├─ vitis/
├─ constraints/
├─ scripts/
└─ reports/
```

## 报告与验证

- HLS csim、csynth、cosim 结果需要记录。
- Vivado timing、utilization、DRC 需要记录。
- 修改接口或数据格式时，同步更新软件端文档。
