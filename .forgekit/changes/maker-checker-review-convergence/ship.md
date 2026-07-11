# 发布

TargetVersion: 0.44.0
AuthorizedStage: implementation-ready-for-review

## 升级路径

- 新项目从 project-template 直接获得新规则。
- 0.43.2 项目经统一入口进入 0.44.0 migration plan。
- baseline 相同文件安全替换；本地不同文件保留并进入 review-needed/manual merge。

## 回滚与限制

- migration 不覆盖项目真实 change 工件或业务规则。
- 本工件不授权 commit、tag、push、发布或对真实项目 apply。
