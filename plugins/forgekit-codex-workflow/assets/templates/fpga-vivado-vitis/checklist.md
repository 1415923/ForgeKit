# FPGA Vivado / Vitis 检查清单

## 开发前

- [ ] 目标板卡和芯片型号明确。
- [ ] 时钟、复位、接口协议明确。
- [ ] 输入输出数据格式明确。
- [ ] 资源、延迟、吞吐目标明确。

## 开发中

- [ ] HLS pragma 变更有理由。
- [ ] 定点位宽和溢出行为已考虑。
- [ ] AXI / stream / memory 接口一致。
- [ ] 测试数据和 golden reference 一致。

## 开发后

- [ ] csim 或等价仿真已运行。
- [ ] csynth 报告已查看。
- [ ] timing/utilization 变化已记录。
- [ ] 软件端接口文档已同步。
- [ ] 未经确认没有操作板卡或下载 bitstream。
