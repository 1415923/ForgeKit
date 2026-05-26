# Flutter Dart 命令示例

```powershell
flutter doctor
flutter pub get
flutter analyze
flutter test
flutter test integration_test
flutter build apk
flutter build web
```

## Local validation / 局部验证优先级

```powershell
flutter analyze
flutter test
flutter test integration_test
```

注意：

- `flutter pub get` 会下载依赖，先确认网络和镜像源。
- `flutter doctor` 是只读检查，但可能暴露本机 SDK 状态。
- Android/iOS build 依赖 SDK、证书、模拟器或真机环境，执行前确认。
- 修改包名、签名、图标、隐私权限、商店发布配置属于发布级动作。
