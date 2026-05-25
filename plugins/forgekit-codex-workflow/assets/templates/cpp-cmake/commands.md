# C++ CMake 命令示例

```powershell
cmake --version
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

## Local validation / 局部验证优先级

```powershell
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

注意：

- Windows 下生成器差异很大，Visual Studio、Ninja、Makefiles 不可混写。
- `build/` 应作为 out-of-source 构建目录，不把生成文件写入源码目录。
- Conan/vcpkg/系统包管理器会下载或改依赖，先确认。
- 安装、打包、写系统目录、刷设备、交叉编译和发布二进制前必须确认。
