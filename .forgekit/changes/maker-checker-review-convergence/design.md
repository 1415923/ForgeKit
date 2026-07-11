# 设计

## 最小机制

1. proposal 冻结 Scope、Trust Boundary、Non-goals、Stage Authorization。
2. verification 用轻量 Frozen Acceptance Matrix 表达合同、正例、关键拒绝反例和证据；medium/high 使用，规模按风险裁剪。
3. Checker 首审按冻结合同和有限的 Critical consequence override 分类；矩阵外其余建议为 follow-up。
4. re-review 默认只闭合上一轮 blocking findings；仅新发现的 Critical consequence 可例外阻塞。
5. 一轮正常修复后仍有多个 Major 时返回设计阶段，而非无限小补丁。
6. review pass 只授权 proposal 声明的下一阶段。

## 管理边界

- ForgeKit 管理：change `_template`、治理协议、usage playbook、生成入口、review skill 指令、迁移元数据。
- 项目维护：实际 change 内容、业务规则、项目定制 AGENTS/usage/review 指令。
- 升级仅自动替换与已知 baseline 相同的文件；不同内容保留并进入 review-needed/manual merge。
