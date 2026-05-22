# FPGA Vivado / Vitis 命令示例

命令按项目实际脚本调整。不要在未确认时直接运行长耗时流程。

## 只读检查

```powershell
Get-ChildItem D:\Xilinx\Vivado\2023.2
Get-ChildItem D:\Xilinx\Vitis\2023.2
Get-ChildItem D:\Xilinx\Vitis_HLS\2023.2
```

## HLS

```powershell
vitis_hls -f scripts/run_hls.tcl
```

## Vivado

```powershell
vivado -mode batch -source scripts/build.tcl
```

注意：

- 运行前通常需要加载 Xilinx 环境脚本。
- `vitis_hls`、`vivado` 批处理属于 C/D 级命令，先确认。
- GUI、板卡连接、bitstream 下载必须先确认。
