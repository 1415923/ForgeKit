# Rust CLI / Service 项目规则补充

## 代码结构

```text
src/
├─ main.rs
├─ lib.rs
└─ bin/
tests/
benches/
examples/
```

## 开发规则

- 先区分 binary、library、workspace，不强行改 crate 边界。
- 应用入口可以格式化错误输出；库代码不要随意 `panic!`。
- 避免滥用 `unwrap()` / `expect()`，测试和明确不变量除外。
- async runtime 必须明确，不混用 Tokio、async-std 或 smol。
- `unsafe`、FFI、跨平台路径和信号处理需要单独审查。
- public API、feature flag 和错误类型变化要记录兼容影响。

## 测试

- 基线使用 `cargo test`。
- CLI 行为可用集成测试或快照测试。
- 库代码优先覆盖错误路径和边界输入。
- 性能、并发、unsafe 和 FFI 变更需要更强验证或人工复核。
