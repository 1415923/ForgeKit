# C++ CMake 模板

适用于 C++ 库、CLI、嵌入式上位机、算法模块、性能模块和需要跨平台构建的工程。

不适用于第一版就重写大型遗留构建系统、驱动/内核、复杂交叉编译工具链或闭源 SDK 集成；这些需要单独审计。

## Codex 启动建议

- 推荐启动目录：包含 `CMakeLists.txt` 或 `CMakePresets.json` 的项目根目录。
- 初始化前必须确认：库、CLI、服务还是嵌入式配套；编译器；C++ 标准；依赖管理；目标平台。
- 优先阅读：`CMakeLists.txt`、`CMakePresets.json`、`src/`、`include/`、`tests/`、`cmake/`、依赖说明。
- Ignore guidance / 避免默认读取：`build/`、`out/`、`.vs/`、生成二进制、第三方 SDK 大目录、编译产物。

## 符号搜索 / LSP

- 优先使用 clangd、Visual Studio、CLion 或 compile_commands.json 识别符号和包含路径。
- CLI 中按 class、namespace、function、target、library、include、test case 搜索。
- 常用关键词：`add_library`、`add_executable`、`target_link_libraries`、`target_include_directories`、`enable_testing`、`add_test`。
- 修改 ABI、公共头文件、编译选项、链接方式、运行时库或平台宏前，先查调用方和构建矩阵。

## 局部验证

- 修改单个库：优先构建相关 target 并运行相关测试。
- 修改 CMake：使用 out-of-source build 验证。
- 修改公共头文件/ABI：检查下游依赖、导出符号和兼容性。
- 修改依赖管理、编译器、生成器或交叉编译配置前必须确认环境。
