本文档记录了如何配置一套专业的现代化开发环境。相比传统 Keil，该方案拥有更快的编译速度、更精准的代码补全，且全面拥抱开源社区，摆脱商业版权限制

- 环境参数
	- **操作系统 (OS)**：Arch Linux
	- **IDE (编辑器)**：VS Code
	- **MCU 型号**：STM32F407ZET6
	- **开发方式**：标准外设库 (StdPeriph_Lib)
	- **编译器**：arm-none-eabi-gcc
	- **构建系统**：CMake + Make
	- **语言服务器**：Clangd
	- **调试/烧录**：OpenOCD + DAPLink
## 环境软件安装
在 Linux 下，使用 `pacman` 安装交叉编译器及相关调试工具：

|**工具名称**|**包名 (pacman)**|**功能描述**|
|---|---|---|
|**编译器**|`arm-none-eabi-gcc`|将 C 代码编译为 ARM 指令|
|**标准库**|`arm-none-eabi-newlib`|提供底层 C 标准库支持|
|**构建工具**|`cmake` `make`|管理编译流程与多文件依赖|
|**烧录工具**|`openocd`|连接 DAPLink 进行下载与调试|
|**调试器**|`arm-none-eabi-gdb`|在线断点调试|
|**索引工具**|`bear`|(可选) 辅助生成 Clangd 索引|

**安装命令：**
```bash
sudo pacman -S arm-none-eabi-gcc arm-none-eabi-newlib arm-none-eabi-gdb arm-none-eabi-binutils openocd cmake make
```

---

## 工程目录

为了保持代码整洁并适配 Linux 环境，建议采用以下结构：
```Plaintext
.
├── CORE/                # 关键：存入从官方库复制的 GCC 格式启动文件 (.s)
├── FWLIB/               # 标准外设库 (.c/.h)
├── HARDWARE/            # 自定义硬件驱动
│   ├── inc/             # 存放 .h
│   └── src/             # 存放 .c
├── SYSTEM/              # 系统基础驱动
│   ├── inc/             
│   └── src/             
├── USER/                # 业务逻辑 (main.c, stm32f4xx_it.c 等)
├── cmake/               # 存放 gcc-arm-none-eabi.cmake 工具链文件
├── build/               # 编译输出目录
├── STM32F407XX_FLASH.ld # 链接脚本
├── STM32F407.svd        # 寄存器定义文件
└── CMakeLists.txt       # 项目核心配置文件
```

## 工程迁移
本教程基于 **STM32F407 标准库模板** 进行迭代升级。迁移重心在于剔除 Windows/Keil 依赖，并从官方工具（如 STM32CubeMX）生成的 **CMake 工程** 中提取适配 GCC 的底层“素材”
### 清理阶段
- **USER 目录**：仅保留以下 10 个核心文件，其余（如 `.uvprojx`）全部删除。
    - **源文件**：`main.c`, `stm32f4xx_it.c`, `system_stm32f4xx.c`, `my_reg.c`
    - **头文件**：`main.h`, `stm32f4xx_it.h`, `system_stm32f4xx.h`, `my_reg.h`, `stm32f4xx.h`, `stm32f4xx_conf.h`
- **根目录清理**：
    - 删除 `OBJ/` 文件夹（Linux 环境统一使用 `build/`）。
    - 删除 `TOOLS/keilkill.bat`（Windows 脚本）
### 取与替换（素材库应用）

使用 STM32CubeMX 生成一个临时的 CMake 或 Makefile 工程作为**素材库**，提取以下关键文件：
- **启动文件替换**：删除 Keil 版 `CORE/startup_stm32f40_41xxx.s`。从素材库中获取 **GCC 格式** 的 `startup_stm32f407xx.s` 放入 `CORE/`。
- **链接脚本 (.ld)**：从素材库拷贝 `.ld` 文件至项目根目录。
- **标准库 (FWLIB) 取舍**：
    - **保留核心**：`misc.c`, `stm32f4xx_rcc.c`, `stm32f4xx_gpio.c`。
    - **强制剔除**：必须删除 `stm32f4xx_fmc.c`。F407 仅支持 FSMC，保留 FMC 驱动会导致定义冲突。

> [!tip] 建议将提取出的 `.ld` 和 GCC 版启动文件妥善保存，作为今后新建工程的通用底层素材。

### 三、 核心配置：CMakeLists.txt
替代 Keil 工程文件的核心，负责指定编译规则与路径

```CMake
cmake_minimum_required(VERSION 3.20)

  

# 1. 指定工具链

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/gcc-arm-none-eabi.cmake")

  

project(STM32_Linux_Template C ASM)

  

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 2. 设置编译参数

set(CPU_PARAMETERS

-mcpu=cortex-m4

-mthumb

-mfpu=fpv4-sp-d16

-mfloat-abi=hard

)

  

# 这里使用全局编译选项没问题

add_compile_options(${CPU_PARAMETERS} -Wall -fdata-sections -ffunction-sections)

  

# 3. 宏定义

add_definitions(-DSTM32F40_41xxx -DUSE_STDPERIPH_DRIVER)

  

# 4. 头文件搜索路径 (全局)

include_directories(

USER

CORE

SYSTEM/inc

HARDWARE/inc

FWLIB/inc

)

  

# 5. 收集源文件

file(GLOB_RECURSE SOURCES

"USER/*.c"

"SYSTEM/*.c"

"HARDWARE/*.c"

"FWLIB/src/*.c"

"CORE/system_stm32f4xx.c"

)

list(FILTER SOURCES EXCLUDE REGEX "stm32f4xx_fmc.c")

set(STARTUP_ASM "CORE/startup_stm32f407xx.s")

  

# 6. 【关键】先生成可执行文件

add_executable(${PROJECT_NAME} ${SOURCES} ${STARTUP_ASM})

  

# 2. 【核心修复】仅在这里配置链接参数，确保没有其他地方设置 -T 参数

target_link_options(${PROJECT_NAME} PRIVATE

${CPU_PARAMETERS}

# -T "${CMAKE_CURRENT_SOURCE_DIR}/STM32F407XX_FLASH.ld" <-- 删除或注释掉这一行

-Wl,-Map=${PROJECT_BINARY_DIR}/${PROJECT_NAME}.map

-Wl,--cref

-Wl,--gc-sections

)

  

# 8. 编译后处理 (hex, bin, size)

set(HEX_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.hex)

set(BIN_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.bin)

  

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD

COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${HEX_FILE}

COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${BIN_FILE}

COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>

COMMENT "Building ${HEX_FILE} \nBuilding ${BIN_FILE}"

)

  
  

# 添加自定义烧录目标 (针对 ZET6 和 DAPLink)

add_custom_target(flash

COMMAND openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c "program ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.elf verify reset exit"

DEPENDS ${PROJECT_NAME}

WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

COMMENT "正在通过 DAPLink 烧录固件到 STM32F407ZET6..."

)
```

---

### 智能补全优化
在根目录创建 `.clangd` 文件。**注意：此处为 YAML 格式，用于模拟 GCC 环境并关联编译数据库。**

```YAML
cmake_minimum_required(VERSION 3.20)

  

# 1. 指定工具链

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/gcc-arm-none-eabi.cmake")

  

project(STM32_Linux_Template C ASM)

  

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 2. 设置编译参数

set(CPU_PARAMETERS

-mcpu=cortex-m4

-mthumb

-mfpu=fpv4-sp-d16

-mfloat-abi=hard

)

  

# 这里使用全局编译选项没问题

add_compile_options(${CPU_PARAMETERS} -Wall -fdata-sections -ffunction-sections)

  

# 3. 宏定义

add_definitions(-DSTM32F40_41xxx -DUSE_STDPERIPH_DRIVER)

  

# 4. 头文件搜索路径 (全局)

include_directories(

USER

CORE

SYSTEM/inc

HARDWARE/inc

FWLIB/inc

)

  

# 5. 收集源文件

file(GLOB_RECURSE SOURCES

"USER/*.c"

"SYSTEM/*.c"

"HARDWARE/*.c"

"FWLIB/src/*.c"

"CORE/system_stm32f4xx.c"

)

list(FILTER SOURCES EXCLUDE REGEX "stm32f4xx_fmc.c")

set(STARTUP_ASM "CORE/startup_stm32f407xx.s")

  

# 6. 【关键】先生成可执行文件

add_executable(${PROJECT_NAME} ${SOURCES} ${STARTUP_ASM})

  

# 2. 【核心修复】仅在这里配置链接参数，确保没有其他地方设置 -T 参数

target_link_options(${PROJECT_NAME} PRIVATE

${CPU_PARAMETERS}

# -T "${CMAKE_CURRENT_SOURCE_DIR}/STM32F407XX_FLASH.ld" <-- 删除或注释掉这一行

-Wl,-Map=${PROJECT_BINARY_DIR}/${PROJECT_NAME}.map

-Wl,--cref

-Wl,--gc-sections

)

  

# 8. 编译后处理 (hex, bin, size)

set(HEX_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.hex)

set(BIN_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.bin)

  

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD

COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${HEX_FILE}

COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${BIN_FILE}

COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>

COMMENT "Building ${HEX_FILE} \nBuilding ${BIN_FILE}"

)

  
  

# 添加自定义烧录目标 (针对 ZET6 和 DAPLink)

add_custom_target(flash

COMMAND openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c "program ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.elf verify reset exit"

DEPENDS ${PROJECT_NAME}

WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

COMMENT "正在通过 DAPLink 烧录固件到 STM32F407ZET6..."

)
```

---

## 五、 烧录与在线调试
### 编译与下载
- **手动编译**：`cd build && cmake .. && make -j$(nproc)`
- **一键烧录**：`make flash`
### 在线调试配置
存放在 `.vscode/launch.json`
```JSON
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "STM32 Debug (DAPLink)",
            "type": "cortex-debug",
            "request": "launch",
            "servertype": "openocd",
            "executable": "${command:cmake.launchTargetPath}",
            "configFiles": ["interface/cmsis-dap.cfg", "target/stm32f4x.cfg"],
            "svdFile": "${workspaceFolder}/STM32F407.svd", // 关键：查看寄存器
            "runToEntryPoint": "main"
        }
    ]
}
```

---

#### 2. 快捷任务 (`tasks.json`)

实现 `Ctrl + Shift + B` 快速烧录：


```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Flash Device",
            "type": "shell",
            "command": "make flash", // 或直接调用 openocd 命令
            "options": { "cwd": "${workspaceFolder}/build" },
            "group": "build"
        }
    ]
}
```

---

### 六、 开发者避坑指南 (Arch 专属)

1. **Flash 限制**：STM32F407 **ZET6** 的 Flash 为 **512KB**，务必修改 `.ld` 文件的 `LENGTH = 512K`，否则大程序溢出时无法在编译阶段预警。
    
2. **路径与文件系统**：强烈建议将工程放在 Linux 原生分区（Ext4/Btrfs）。在 `/mnt/WindowsD` 下，`clangd` 有时会因文件系统驱动差异导致路径解析失败。
    
3. **刷新索引**：若修改了头文件路径后仍报错，按 `F1` 键执行 `Clangd: Restart language server` 重启解析引擎。
## 五、 烧录、运行与在线调试

为完成 **“烧录到单片机并使其开始执行”** 的目标提供两个解决方法:

### 主流方案：Cortex-Debug 在线调试 (推荐)

这是 VS Code 嵌入式开发的 **绝对主流方案**。它能提供超越 Keil 的调试体验（断点、寄存器查看、变量实时监控）
#### (1) 准备工作

确保系统中已安装 GDB 调试器：
```
sudo pacman -S arm-none-eabi-gdb
```
VSCode 安装 Cortex-Debug 插件
#### (2) 核心配置文件：`launch.json`

存放在 `.vscode/launch.json`。配置后可实现 **F5** 一键“编译 + 烧录 + 自动复位 + 停在 main 函数”。
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "STM32 Debug (DAPLink)",
            "cwd": "${workspaceFolder}",
            "executable": "${command:cmake.launchTargetPath}", // 自动获取最新生成的 elf 路径
            "request": "launch",
            "type": "cortex-debug",
            "servertype": "openocd",
            "device": "STM32F407ZET6",
            "runToEntryPoint": "main", // 启动后停在 main 开头，类似 Keil 的 Run to main
            "configFiles": [
                "interface/cmsis-dap.cfg",
                "target/stm32f4x.cfg"
            ],
            "gdbPath": "arm-none-eabi-gdb",
            "svdFile": "${workspaceFolder}/STM32F407.svd" // 寄存器可视化文件
        }
    ]
}
```

#### (3) 进阶功能：寄存器查看 (SVD)
在 VS Code 中通过 **SVD 文件** 也可以实现Keil 中我们可以方便地看 `GPIOA->ODR` 的值
 - 下载 svd:去 ST 官网或 [CMSIS-SVD 开源库](https://github.com/modm-io/cmsis-svd-stm32/tree/main) 下载 `STM32F407.svd`
- **放置位置**：建议直接放在工程根目录下（例如 `STM32F407.svd`）
- **功能**：在调试模式下，VS Code 侧边栏会出现 **“PERIPHERALS（外设）”** 窗格。展开后可实时观察 `GPIOA->ODR` 等寄存器的每一位状态，排查驱动逻辑。
    

---

### 辅助方案：自动化烧录目标
适用于“不调试、只看结果”的场景
####CMake `flash` 目标

在 `CMakeLists.txt` 末尾添加的任务，支持终端执行：

```bash
make flash
```
或通过 CMake Tools 状态栏将目标从 `[all]` 切换为 `[flash]` 后点击“生成”。
#### 快捷任务 (`tasks.json`)
存放在 `.vscode/tasks.json`。实现 `Ctrl + Shift + B` 弹出菜单选择“一键烧录”：
```JSON
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Flash Device",
            "type": "shell",
            "command": "make flash",
            "options": { "cwd": "${workspaceFolder}/build" },
            "group": { "kind": "build", "isDefault": false },
            "problemMatcher": []
        }
    ]
}
```

---

### 4. 调试/烧录工作流对比总结

|**维度**|**launch.json (F5)**|**CMake flash 目标**|
|---|---|---|
|**定位**|**开发全功能 IDE 模式**|**构建系统自动化脚本**|
|**核心优势**|断点调试、变量观察、寄存器视图|速度极快、不依赖 UI、适合快速迭代|
|**交互体验**|图形化，一键全自动|命令行触发，适合“写完就跑”|
|**适用场景**|逻辑开发、排查复杂 Bug|生产线烧录、简单的功能演示|

**我的建议**：两个都要。平时开发写代码用 **F5** 调逻辑；写好了想演示结果或简单改个参数时用 **`make flash`**