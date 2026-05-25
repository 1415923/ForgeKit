# Swift iOS 项目规则补充

## 代码结构

```text
App/
Sources/
Tests/
UITests/
Resources/
```

## 开发规则

- 先确认 SwiftUI、UIKit 或混合项目，不默认迁移 UI 框架。
- View、state、navigation、service、persistence 边界要保持清楚。
- 签名、entitlements、Info.plist、隐私权限和 bundle id 是高风险区域。
- Swift Package、CocoaPods、SwiftPM、XCFramework 依赖管理要先识别。
- App Store、TestFlight、企业分发都需要账号和证书确认。

## 测试

- 区分 Swift Testing、XCTest、UI Tests 和性能测试。
- 核心业务逻辑优先单元测试。
- UI、权限、推送、内购、定位、相机等需要设备或模拟器验证。
