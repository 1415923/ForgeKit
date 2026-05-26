# C++ CMake 项目规则补充

## 代码结构

```text
include/
src/
tests/
cmake/
third_party/
```

## 开发规则

- 默认使用 CMake，但不默认指定 Conan/vcpkg，先识别项目已有依赖管理。
- 使用 out-of-source build，避免污染源码目录。
- 编译器、生成器、C++ 标准、运行时库和 Debug/Release 模式必须明确。
- 公共头文件、ABI、导出符号、平台宏和链接方式变化需要记录兼容影响。
- 第三方 SDK、静态/动态链接、字符集和路径编码是高风险点。

## 测试

- 基线支持 CTest。
- 具体测试框架可为 GoogleTest、Catch2、doctest 或项目已有方案。
- 性能、数值精度、线程安全和跨平台行为需要专门验证。
- 硬件、设备、驱动或外部 SDK 测试前确认环境。
