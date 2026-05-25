# Flutter Dart 项目规则补充

## 代码结构

```text
lib/
├─ main.dart
├─ app/
├─ features/
├─ shared/
└─ services/
test/
integration_test/
```

## 开发规则

- 先确认目标平台，不把 Web、移动端、桌面行为混为一谈。
- 状态管理不默认站队，优先尊重项目已有 Provider/Riverpod/Bloc/GetX 等方案。
- Widget 保持职责清晰，复杂业务放 state/service/repository。
- 平台权限、原生插件、签名、包名和图标修改属于高风险动作。
- assets、字体和图片要检查 `pubspec.yaml`，避免包体积失控。

## 测试

- 纯逻辑用 unit test。
- UI 组件用 widget test。
- 关键流程用 integration test，但需确认模拟器/真机/浏览器环境。
- 跨平台差异需要分别验证，不用单个平台结果代表全部平台。
