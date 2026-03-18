本文档记录了如何配置一套在 **Arch Linux** 下基于 **CMake + VS Code** 的专业的现代化开发环境,相比传统的 Keil 环境，这套方案拥有更快的编译速度和更现代的代码补全体验且全面拥抱开源社区不受 keil 和 jlink 的商业化影响

环境参数:
- os:arch
- 开发方式: stm 32 标准库
- VSCode
- clangd
- daplink
## 环境软件安装 (Arch Linux)
在 Linux 下，我们需要安装交叉编译器和调试工具链：

|**工具名称**|**包名 (pacman)**|**功能描述**|
|---|---|---|
|**编译器**|`arm-none-eabi-gcc`|将 C 代码编译为 ARM 指令|
|**标准库**|`arm-none-eabi-newlib`|提供底层 C 标准库支持|
|**构建工具**|`cmake` `make`|管理编译流程与多文件依赖|
|**烧录工具**|`openocd`|连接 DAPLink 进行程序下载与调试|
|**调试器**|`arm-none-eabi-gdb`|用于在线断点调试|
## 安装编译器和调试器 
sudo pacman -S arm-none-eabi-gcc arm-none-eabi-newlib arm-none-eabi-gdb arm-none-eabi-binutils # 安装烧录工具 (DAPLink 核心) sudo pacman -S openocd # 安装用于生成 Clangd 索引的工具 sudo pacman -S bear

---

### 二、 工程目录结构
为了保持代码整洁，采用以下结构：

```Plaintext
.
├── CORE/                # 启动文件 (.s) 与内核核心文件
├── FWLIB/               # STM32 标准外设库文件 (.c/.h)
├── HARDWARE/            # 自定义硬件驱动 (LED, LCD 等)
│   ├── inc/             # 存放 .h 头文件
│   └── src/             # 存放 .c 源文件
├── SYSTEM/              # 系统基础驱动 (delay, sys, usart)
│   ├── inc/             #
│   └── src/             #
├── USER/                # main.c, 中断处理函数
├── cmake/               # 存放交叉编译工具链脚本 (.cmake)
├── build/               # 编译输出目录
├── STM32F407XX_FLASH.ld # 链接脚本
└── CMakeLists.txt       # 项目核心配置文件
```

---

本教程是基于STM32F407 标准库模板进行的迭代升级所以其默认是在完成其的基础上进行的修改具体内容如下
USER 目录只保留:
main. c    stm 32 f 4 xx_conf. h  system_stm 32 f 4 xx. c
main. h    stm 32 f 4 xx. h       system_stm 32 f 4 xx. h
my_reg. c  stm 32 f 4 xx_it. c
my_reg. h  stm 32 f 4 xx_it. h
**根目录下**：
- `OBJ/` (空文件夹或 Keil 输出，Linux 习惯使用 `build/`)
- `TOOLS/keilkill.bat` (这是 Windows 批处理)
替换：启动文件:
- 删除现有的 `CORE/startup_stm32f40_41xxx.s`

- 去官方固件库的 `Libraries/CMSIS/Device/ST/STM32F4xx/Source/Templates/gcc/` 目录下找同名文件复制过来。

### 取舍：FWLIB (标准库)

为了缩短编译时间和减少干扰，建议进行筛选：

- **保留核心**：`misc.c`, `stm32f4xx_rcc.c`, `stm32f4xx_gpio.c`。
    
- **剔除不匹配硬件**：`stm32f4xx_fmc.c`（F407 只有 FSMC，没有 FMC，留着会报重复定义错误）。
    
- **其他随意**：你可以保留剩下的，但在 `Makefile` 中只包含你用到的 `.c` 文件，或者干脆全部保留，通过 Makefile 的 `filter-out` 排除掉报错的即可。
#### . 获取链接脚本 (.ld)

这是告诉编译器 Flash 和 RAM 开始地址的文件。你可以通过 `yay -S stm32cubemx` 安装官方工具，生成一个 F407 的 Makefile 工程，然后把里面的 `.ld` 文件拷贝过来改名为 `STM32F407VGTx_FLASH.ld`**

文件类型`temp_f407` 中的位置目标位置 (正式工程)说明**工具链文件**`cmake/gcc-arm-none-eabi.cmake``cmake/`告诉 CMake 如何调用交叉编译器**链接脚本**`STM32F407XX_FLASH.ld`根目录内存分配核心文件**启动文件**`startup_stm32f407xx.s``CORE/`GCC 格式的汇编启动代码
### 三、 核心配置：CMakeLists.txt

这是 Linux 下开发的核心，替代了 Keil 的 `.uvprojx` 工程文件：

1. **指定头文件路径**：必须明确指出所有包含 `.h` 的子目录。
    
2. **递归收集源码**：使用 `file(GLOB_RECURSE ...)` 自动搜索所有 `.c` 文件。
    
3. **生成编译数据库**：添加 `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` 以支持 `clangd` 补全。
    
4. **添加自定义烧录目标**：

    CMake

    ```
    add_custom_target(flash
        COMMAND openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c "program ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.elf verify reset exit"
        DEPENDS ${PROJECT_NAME}
    )
    ```
cmake_minimum_required(VERSION 3.20)

  

## 1. 指定工具链

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/gcc-arm-none-eabi.cmake")



project(STM32_Linux_Template C ASM)



set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

## 2. 设置编译参数

set(CPU_PARAMETERS

-mcpu=cortex-m4

-mthumb

-mfpu=fpv4-sp-d16

-mfloat-abi=hard

)



## 这里使用全局编译选项没问题

add_compile_options(${CPU_PARAMETERS} -Wall -fdata-sections -ffunction-sections)



## 3. 宏定义

add_definitions(-DSTM32F40_41xxx -DUSE_STDPERIPH_DRIVER)



## 4. 头文件搜索路径 (全局)

include_directories(

USER

CORE

SYSTEM/inc

HARDWARE/inc

FWLIB/inc

)



## 5. 收集源文件

file(GLOB_RECURSE SOURCES

"USER/*.c"

"SYSTEM/*.c"

"HARDWARE/*.c"

"FWLIB/src/*.c"

"CORE/system_stm32f4xx.c"

)

list(FILTER SOURCES EXCLUDE REGEX "stm32f4xx_fmc.c")

set(STARTUP_ASM "CORE/startup_stm32f407xx.s")



## 6. 【关键】先生成可执行文件

add_executable(${PROJECT_NAME} ${SOURCES} ${STARTUP_ASM})



## 2. 【核心修复】仅在这里配置链接参数，确保没有其他地方设置 -T 参数

target_link_options(${PROJECT_NAME} PRIVATE

${CPU_PARAMETERS}

## -T "${CMAKE_CURRENT_SOURCE_DIR}/STM32F407XX_FLASH.ld" <-- 删除或注释掉这一行

-Wl,-Map=${PROJECT_BINARY_DIR}/${PROJECT_NAME}.map

-Wl,--cref

-Wl,--gc-sections

)



## 8. 编译后处理 (hex, bin, size)

set(HEX_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.hex)

set(BIN_FILE ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.bin)



add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD

COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${HEX_FILE}

COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${BIN_FILE}

COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>

COMMENT "Building ${HEX_FILE} \nBuilding ${BIN_FILE}"

)




## 添加自定义烧录目标 (针对 ZET6 和 DAPLink)

add_custom_target(flash

COMMAND openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c "program ${PROJECT_BINARY_DIR}/${PROJECT_NAME}.elf verify reset exit"

DEPENDS ${PROJECT_NAME}

WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

COMMENT "正在通过 DAPLink 烧录固件到 STM32F407ZET6..."

)


---

### 四、 智能补全优化 (Clangd)

为了解决 Keil 补全慢且不准的问题，我们使用 `clangd`：

1. **生成数据库**：在 `build` 文件夹运行 `cmake ..` 生成 `compile_commands.json`。
    
2. **配置 `.clangd` 文件**：在项目根目录创建，用于屏蔽 ARM 编译器误报并关联 `build` 目录。
    
3. **刷新索引**：若出现红线报错，按 `F1` 执行 `Clangd: Restart language server`。
## cSpell:disable

CompileFlags:

Add: [

"-I", "D:/Program/Development/Keil_v5/ARM/ARMCC/include",

"--target=arm-none-eabi",

"-mcpu=cortex-m4",

"-DSTM32F40_41xxx",

"-DUSE_STDPERIPH_DRIVER",

"-fms-extensions",

"-fms-compatibility",

"-fdeclspec",

"-D__CC_ARM",

"-D__ARMCC_VERSION=5060000",

"-D__STATIC_INLINE=static inline",

"-D__inline=inline",

"-D__forceinline=inline",

"-D__asm(x)=",

"-D__asm=",

"-Dasm=",

"-D__ALIGNED(x)=",

"-D__task=",

"-D__declspec(x)=",

"-D__value_in_regs=",

"-D__breakpoint(x)=",

"-Wno-invalid-noreturn",

"-Wno-unused-parameter",

"-Wno-missing-declarations",

"-Wno-implicit-function-declaration"

]



Index:

Background: Build



Diagnostics:

UnusedIncludes: None

Suppress: [

"ms_attributes_not_enabled",

"unknown_typename",

"pp_hash_error",

"fatal_too_many_errors"

]

---

### 五、 烧录与调试流程 (主流方案)

#### 1. 编译与一键烧录

- **编译**：`cd build && make -j$(nproc)`
    
- **烧录**：`make flash` (依赖于我们在 CMake 中定义的自定义目标)
    

#### 2. VS Code 在线调试 (F5)

配置 `.vscode/launch.json`：

- **servertype**: `openocd`
    
- **configFiles**: 引用 `cmsis-dap.cfg` 和 `stm32f4x.cfg`。
    
- **svdFile**: 关联 `STM32F407.svd` 即可在侧边栏实时查看寄存器。
    

---

### 六、 坑点总结 (Arch 专属)

1. **路径乱码**：避免在工程路径中使用中文字符，否则链接器可能报错“找不到文件”。
    
2. **文件系统**：建议放在 Linux 原生分区（如 `/home`）， `/mnt/WindowsD` 等挂载盘可能存在符号链接权限问题。
    
3. **Flash 大小**：ZET6 务必在 `.ld` 文件中将 `FLASH` 长度改为 `512K`，防止溢出。

## `launch.json`

在你的项目根目录下，进入 `.vscode` 文件夹（如果没有就建一个），新建或修改 **`launch.json`**：

JSON

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "STM32 Debug (DAPLink)",
            "cwd": "${workspaceFolder}",
            "executable": "${command:cmake.launchTargetPath}", // 自动获取 CMake 生成的 elf 路径
            "request": "launch",
            "type": "cortex-debug",
            "runToEntryPoint": "main", // 启动后自动停在 main 函数开头
            "servertype": "openocd",
            "configFiles": [
                "interface/cmsis-dap.cfg",
                "target/stm32f4x.cfg"
            ],
            // 如果你的 gdb 路径不同，可以显式指定
            "gdbPath": "arm-none-eabi-gdb",
            // 选填：SVD 文件路径，用于查看寄存器（见下文）
            "svdFile": "${workspaceFolder}/STM32F407.svd" 
        }
    ]
}
```

---

## 3. 进阶：寄存器查看 (SVD 文件)

在 Keil 中我们可以方便地看 `GPIOA->ODR` 的值，在 VS Code 中通过 **SVD 文件** 也可以实现。

1. **下载 SVD**：去 ST 官网或 [CMSIS-SVD 开源库](https://www.google.com/search?q=https://github.com/cmsis/cmsis-svd) 下载 `STM32F407.svd`。
    
2. **放置文件**：将其放在你的工程根目录下。
    
3. **配置**：在上面的 `launch.json` 中指向这个文件。
    

这样在你调试时，侧边栏会出现一个 **"Peripherals"** 视图，你可以直接看到所有外设寄存器的实时状态。

## 一键烧录（非调试模式）

如果你只是想快速烧录，不想进入调试界面，可以在 **`.vscode/tasks.json`** 里加一个任务：

JSON

```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Flash Device",
            "type": "shell",
            "command": "openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c \"program build/STM32_Linux_Template.elf verify reset exit\"",
            "group": {
                "kind": "build",
                "isDefault": false
            },
            "problemMatcher": []
        }
    ]
}
```

这样你通过 `Ctrl + Shift + B` 就能看到 **Flash Device** 选项，像点鼠标一样方便。

### 放置位置建议

建议将其放置在你的**工程根目录**下。

- **路径**：`••/STM32/STM32_CMake_Template/STM32F407.svd`
    
- **理由**：放在根目录下最方便在 `launch.json` 中使用相对路径引用。如果你打算以后做多个项目，也可以在根目录下建一个 `SVD` 文件夹统一管理，但在单个模板工程里，直接放根目录是最简单的。
    

### 2. 更新 `launch.json` 配置

你需要修改 `.vscode/launch.json` 文件，添加 `svdFile` 字段指向这个文件。修改后的配置如下：

JSON

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "STM32 Debug (DAPLink)",
            "cwd": "${workspaceFolder}",
            "executable": "./build/STM32_Linux_Template.elf",
            "request": "launch",
            "type": "cortex-debug",
            "servertype": "openocd",
            "device": "STM32F407VGT6", // 明确指定芯片型号
            "configFiles": [
                "interface/cmsis-dap.cfg",
                "target/stm32f4x.cfg"
            ],
            // 【关键步骤】指向你刚才上传并放置的文件
            "svdFile": "${workspaceFolder}/STM32F407.svd",
            "runToEntryPoint": "main"
        }
    ]
}
```

### 3. 如何使用

配置完成后，按 **F5** 进入调试模式：

1. 在 VS Code 左侧的调试面板中，除了原有的“变量（Variables）”和“监视（Watch）”外，你会看到一个新的 **“PERIPHERALS（外设）”** 窗格。
    
2. 点击展开它，你会看到 `ADC`、`GPIO`、`RCC` 等所有外设。
    
3. 继续展开某个寄存器（如 `GPIOA -> ODR`），你就能实时看到每一位的状态变化了。