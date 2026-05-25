# Swift iOS 模板

适用于 iOS 原生 App、SwiftUI App、UIKit 维护项目和少量 Swift Package。

不适用于第一版就处理复杂 App Store 发布、企业签名、重度音视频、游戏或复杂跨平台共享代码；这些需要单独确认账号和证书。

## Codex 启动建议

- 推荐启动目录：包含 `.xcodeproj`、`.xcworkspace` 或 `Package.swift` 的项目根目录。
- 初始化前必须确认：SwiftUI 还是 UIKit；目标 iOS 版本；签名方式；测试方案；发布渠道。
- 优先阅读：`Package.swift`、`.xcodeproj`、`Sources/`、`Tests/`、`App/`、`Info.plist`、`*.entitlements`。
- Ignore guidance / 避免默认读取：`DerivedData/`、`build/`、`.xcuserdata/`、归档产物、证书、Provisioning Profile。

## 符号搜索 / LSP

- 优先使用 Xcode SourceKit / Swift LSP 识别类型、引用、preview 和测试。
- CLI 中按 View、ViewModel、Observable、Coordinator、Controller、Service、Package target 搜索。
- 常用关键词：`@main`、`SwiftUI`、`UIViewController`、`Observable`、`@State`、`@Binding`、`XCTest`、`Swift Testing`。
- 修改签名、entitlements、Info.plist、权限、bundle id 或发布配置前，必须确认账号和目标环境。

## 局部验证

- 修改 Swift Package：运行 package tests。
- 修改 App UI：优先运行相关 unit/UI tests 或人工设备验证。
- 修改权限、签名、bundle id、图标、隐私声明：作为发布级动作确认。
- Xcode build/test 依赖本机 Xcode 和模拟器环境，先确认。
