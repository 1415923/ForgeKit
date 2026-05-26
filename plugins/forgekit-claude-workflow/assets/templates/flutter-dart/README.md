# Flutter Dart 模板

适用于 Flutter 跨端 App、移动端 + Web、桌面轻应用和原型到生产的客户端项目。

不适用于第一版就处理复杂原生插件、游戏引擎、重度音视频、复杂商店发布或企业 MDM 分发；这些需要单独确认平台和账号。

## Codex 启动建议

- 推荐启动目录：包含 `pubspec.yaml` 的 Flutter 项目根目录。
- 初始化前必须确认：目标平台 Android/iOS/Web/Windows/macOS/Linux；状态管理；路由；后端接口；发布渠道。
- 优先阅读：`pubspec.yaml`、`lib/main.dart`、`lib/`、`test/`、`integration_test/`、`android/`、`ios/`、`web/`。
- Ignore guidance / 避免默认读取：`build/`、`.dart_tool/`、平台生成产物、签名文件、模拟器缓存、大资源产物。

## 符号搜索 / LSP

- 优先使用 Dart Analysis Server / Flutter 插件识别 widget、provider、路由和类型问题。
- CLI 中按 widget、screen/page、state/provider/bloc、route、repository、service 搜索。
- 常用关键词：`MaterialApp`、`CupertinoApp`、`StatefulWidget`、`StatelessWidget`、`ChangeNotifier`、`Provider`、`Riverpod`、`Bloc`、`GoRouter`。
- 修改路由、状态管理、平台权限、包名、签名、原生目录前，先确认平台和发布影响。

## 局部验证

- 修改纯 Dart 逻辑：运行相关 unit test。
- 修改 UI：运行 widget test 或人工截图检查。
- 修改平台目录、权限、签名或包名：必须先确认目标平台和发布账号。
- `flutter pub get`、build、模拟器/真机运行都可能耗时或依赖本机环境，先确认。
