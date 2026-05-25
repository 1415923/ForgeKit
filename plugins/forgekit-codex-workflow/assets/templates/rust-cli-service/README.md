# Rust CLI / Service 模板

适用于 Rust CLI、系统工具、高性能服务、SDK、后台组件和安全/性能敏感模块。

不适用于第一版就处理大型 unsafe/FFI、内核/驱动、嵌入式 no_std 或复杂跨平台安装器；这些需要单独确认工具链和发布方式。

## Codex 启动建议

- 推荐启动目录：包含 `Cargo.toml` 的 crate 或 workspace 根目录。
- 初始化前必须确认：CLI、service、library 还是 workspace；是否 async；目标平台；发布二进制还是库。
- 优先阅读：`Cargo.toml`、`Cargo.lock`、`src/main.rs`、`src/lib.rs`、`src/bin/`、`tests/`、`benches/`。
- Ignore guidance / 避免默认读取：`target/`、发布二进制、覆盖率产物、生成代码、大日志。

## 符号搜索 / LSP

- 优先使用 rust-analyzer 识别类型、trait 实现、引用和宏展开。
- CLI 中按 crate、module、trait、enum、error type、command、handler 搜索。
- 常用关键词：`fn main`、`Result<`、`thiserror`、`anyhow`、`tokio::main`、`clap`、`serde`、`panic!`、`unsafe`。
- 修改 public API、trait、error type、async runtime、unsafe 或 FFI 前，先查调用方和测试。

## 局部验证

- 修改单个模块：运行相关测试或 crate 测试。
- 修改 CLI 输出：确认输出兼容性和快照/集成测试。
- 修改 service 行为：检查配置、日志、信号处理、健康检查和 shutdown。
- 修改依赖或 features：先确认网络和 feature matrix，再运行 clippy/test。
