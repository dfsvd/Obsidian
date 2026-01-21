qtnetw 是 qt 的网络模块，只有添加了这个模块后才能使用 qt 的网络相关功能

## 基于CMake 的配置
---
### 1. 添加组件
在 CMakelilset 中的 `find_package(Qt6 6.5 REQUIRED COMPONENTS Core Widgets)` 行添加 `Network` 组件：
**修改后：**
```cmake
find_package(Qt6 6.5 REQUIRED COMPONENTS Core Widgets Network)
```

### 2. 链接库

在 target_link_libraries这一块：
```CMake
target_link_libraries(TepClient
    PRIVATE
        Qt::Core
        Qt::Widgets
)
```
添加 `Qt::Network` 库：
**修改后：**
```CMake
target_link_libraries(TepClient
    PRIVATE
        Qt::Core
        Qt::Widgets
        Qt::Network    # <-- 新增这一行
)
```