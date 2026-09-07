# 验证

## Frozen Acceptance Matrix

medium/high risk change 在实现前冻结一个与风险相称的轻量矩阵。每项至少包含正常路径、关键拒绝反例和证据；不需要把普通 change 扩成大型测试规范。

| ID | Contract | Positive case | Rejection case | Evidence |
| --- | --- | --- | --- | --- |
| E01 | 要保持的可观察合同 | 合法输入或正常路径 | 最重要的非法输入或失败路径 | 正式入口、测试或运行证据 |

规则：

- Maker 将每个 acceptance ID 映射到实现和测试证据。
- 正式 CLI/API/orchestration 必须接入被测试的同一条真实路径；只验证 helper 不足以关闭对应合同。
- 矩阵外改进默认记录为 follow-up，除非它触发 review 协议定义的 Critical consequence。
- 修改冻结矩阵意味着返回设计/验收阶段，不应在 review 中悄悄扩大合同。

## 自动检查

- Command:
- Result:

## 人工检查

- Step:
- Expected:
- Result:

## 回归范围

- 可能破坏什么，以及如何检查。

## 未验证项

- 有意未验证的项目和原因。
