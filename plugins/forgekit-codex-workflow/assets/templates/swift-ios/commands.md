# Swift iOS 命令示例

```powershell
swift --version
swift test
xcodebuild -list
xcodebuild test -scheme <SchemeName> -destination "platform=iOS Simulator,name=iPhone 15"
```

## Local validation / 局部验证优先级

```powershell
swift test
xcodebuild -list
xcodebuild test -scheme <SchemeName> -destination "platform=iOS Simulator,name=iPhone 15"
```

注意：

- `xcodebuild` 需要 macOS/Xcode 环境；Windows 上只能记录命令，不直接运行。
- 签名、Team ID、证书、Provisioning Profile、App Store 上传前必须确认。
- 修改 Info.plist、entitlements、权限、bundle id 和图标属于发布级动作。
- 不默认安装 Xcode、改 Apple 账号或写系统钥匙串。
