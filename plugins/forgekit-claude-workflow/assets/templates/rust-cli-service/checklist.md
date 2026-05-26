# Rust CLI / Service 检查清单

- [ ] 已确认项目形态：CLI、service、library 或 workspace。
- [ ] 错误处理清楚，库代码没有随意 `panic!`。
- [ ] `unwrap()` / `expect()` 使用有明确理由。
- [ ] async runtime、feature flags 和目标平台已确认。
- [ ] `unsafe`、FFI、跨平台路径、信号处理已单独审查。
- [ ] 已运行或记录 `cargo fmt`、`cargo clippy`、`cargo test`。
- [ ] 发布二进制、安装脚本和系统目录写入前已确认。
