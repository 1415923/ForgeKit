# Rust CLI / Service 命令示例

```powershell
rustc --version
cargo --version
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo build --release
```

## Local validation / 局部验证优先级

```powershell
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo build
```

注意：

- `cargo update` 会改依赖锁定，先确认。
- `cargo build --release` 可能耗时较长，适合发布前或性能相关变更。
- async runtime、FFI、unsafe、跨平台发布和安装脚本属于高风险变更，执行前确认。
- 不默认运行会访问真实服务、写系统目录或安装全局二进制的命令。
