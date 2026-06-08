# FPGA Vivado / Vitis 命令示例

命令按项目实际脚本调整。不要在未确认时直接运行长耗时流程。

## 只读检查

```powershell
Get-ChildItem $env:XILINX_VIVADO
Get-ChildItem $env:XILINX_VITIS
Get-ChildItem $env:XILINX_HLS
```

## HLS

```powershell
vitis_hls -f scripts/run_hls.tcl
```

Local validation / 推荐把项目脚本拆成局部阶段：

```powershell
vitis_hls -f scripts/csim.tcl
vitis_hls -f scripts/csynth.tcl
vitis_hls -f scripts/cosim.tcl
```

## Vivado

```powershell
vivado -mode batch -source scripts/build.tcl
```

推荐把项目脚本拆成局部阶段：

```powershell
vivado -mode batch -source scripts/check_project.tcl
vivado -mode batch -source scripts/synth.tcl
vivado -mode batch -source scripts/impl.tcl
```

注意：

- 运行前通常需要加载 Xilinx 环境脚本。
- `vitis_hls`、`vivado` 批处理属于 C/D 级命令，先确认。
- GUI、板卡连接、bitstream 下载必须先确认。
- 优先跑仿真和检查脚本；完整综合、实现和 bitstream 生成属于长耗时流程，必须确认。
