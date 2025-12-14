# ❓ 问题：
UI 设计器 (Designer) 中图片显示正常，但在编译运行后的程序中图片丢失或无法显示。
# 💡 核心原因：
图片作为外部文件被引用，但没有通过 Qt 资源系统正确地编译到最终的可执行文件中。
# ✅ 解决方案：三步操作
### 第一步：配置资源文件 (`.qrc`)
1. **创建或编辑您的项目资源文件**（例如：`project_resources.qrc`）。
2. 确保所有需要嵌入到程序中的图片文件（如 `icon.png`）都已添加并分配了 **Prefix**（前缀）。
    - **示例 `项目资源文件.qrc`：**
    ```XML
    <RCC>
        <qresource prefix="/app_assets">  <file>images/icon.png</file>
            <file>images/background.jpg</file>
        </qresource>
    </RCC>
    ```
### 第二步：在 `CMakeLists.txt` 中配置资源编译
这是解决图片丢失问题的核心步骤。使用 Qt 提供的 CMake 函数将 `.qrc` 文件编译成 C++ 代码，并将其加入到您的可执行程序中
```cmake
qt_add_resources(RCC_SOURCES res.qrc)
target_sources(demo9_2 PRIVATE ${RCC_SOURCES})
```

1. **编译资源文件：**
将生成的 C++ 源文件添加到您的目标程序（例如：your_target_app）的编译列表
```CMake

target_sources (your_target_app PRIVATE ${RESOURCE_SOURCES})
```
_（请将 `your_target_app` 替换为您实际的可执行程序名称。）_
2. **链接到目标程序:**
将生成的 C++ 源文件添加到您的目标程序（例如：your_target_app）的编译列表
```cmake
target_sources(your_target_app PRIVATE ${RESOURCE_SOURCES})
```


### 第三步：在 UI/代码中引用**资源路径**

必须使用以 `:` 开头的资源路径，而不是直接的文件系统路径。
1. **打开 UI 设计器 (Qt Designer)。**
2. **找到设置图片的地方**（例如 `QToolBar` 上的 `QAction` 或 `QLabel`）。
3. **选择 "Choose Resource..." (选择资源...)**，然后从弹出的资源列表中选择您的图片。
    - **正确的引用格式：** `:` + `qresource prefix` + `/` + `file` 路径
    - **示例：** 如果 `qrc` 文件中前缀是 `/app_assets`，图片文件路径是 `images/icon.png`，则引用路径应为 **`:/app_assets/images/icon.png`**