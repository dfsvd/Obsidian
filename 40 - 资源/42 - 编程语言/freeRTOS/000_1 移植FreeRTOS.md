本文档记录了在 **STM32F407** 标准库环境下，如何移植并优化 **FreeRTOS V9.0.0** 实时操作系统

---
## 移植准备
### 环境
- **MCU 型号**：STM32F407 系列 (Cortex-M4F 内核，168MHz)
- **内核架构**：ARMv7E-M (支持硬件浮点运算单元 FPU)
- **固件库**：STM32F4xx Standard Peripherals Library (标准库)
- **软件组合**：Keil uVision 5 (Compiler V5) + VSCode
### 目录结构
为了保证工程的可移植性与整洁度，建议将 FreeRTOS 源码放置于根目录 **`LIB`** 下：
```Plaintext
LIB\FreeRTOS
├───inc         # 存放核心头文件与 FreeRTOSConfig.h
├───port        # 存放硬件接口层（ARM_CM4F）
│   └───MemMang # 存放内存管理算法（heap_4.c）
└───src         # 存放内核核心源文件（tasks.c, list.c等）
```
### 准备工作
**获取裸机工程**
- 准备一个基础的 STM32F407 裸机工程（“GPIO输出—点亮LED”），确保该工程可以正常编译和运行
- **下载源码**：从 [FreeRTOS 官网](https://www.freertos.org/) 或 [SourceForge](https://sourceforge.net/projects/freertos/files/FreeRTOS/) 下载 V9.0.0 源码包
---
## 提取源码
### 核心源文件提取
- **src 文件夹**：拷贝 `FreeRTOSv9.0.0/FreeRTOS/Source` 下的所有 `.c` 文件
- **inc 文件夹**：拷贝 `FreeRTOSv9.0.0/FreeRTOS/Source/include` 下的所有 `.h` 文件
### 移植接口文件 (Portable)
- **路径**：`FreeRTOSv9.0.0/FreeRTOS/Source/portable`
- **内核相关**：拷贝 `RVDS/ARM_CM4F` 文件夹到 `port`

> [!tip] 注意
>STM 32F407 带有硬件浮点单元，必须选择 **ARM_CM 4 F**若误选 `ARM_CM3` 或 `ARM_CM4`（无 F），在进行浮点运算时会触发 `HardFault`


- **内存管理**：拷贝 `MemMang` 文件夹到 `port`，仅保留 `heap_4.c`
- 其算法支持内存碎片合并，适合大多数应用
### 获取配置文件
- **路径**：`FreeRTOSV9.0.0/FreeRTOS/Demo/CORTEX_M4F_STM32F407ZG-SK`
- **操作**：拷贝 `FreeRTOSConfig.h` 到的 `LIB/FreeRTOS/inc` 目录下

![提取源码后内容|707](images/000_1%20移植FreeRTOS/file-20260122172718913.jpg)
## 配置文件修正
### 修正编译报错与声明
原始 Demo 中只判断了 IAR 编译器 (`__ICCARM__`)使用 Keil 时需要增加对 `__CC_ARM` 的支持，否则会报错找不到 `SystemCoreClock`

```c
/* --- FreeRTOSConfig.h --- */

/* 修改前 */
#ifdef __ICCARM__ 
	#include <stdint.h> 
	extern uint32_t SystemCoreClock; 
#endif

/* 修改后 */
#if defined(__ICCARM__) || defined(__CC_ARM) || defined(__GNUC__)
    #include <stdint.h>
    extern uint32_t SystemCoreClock;
#endif
```

### 关闭未实现的钩子函数

初次移植时，若开启 Hook 但未定义回调函数，链接时会报 `L6218E: Undefined symbol` 建议初次移植时先关闭，等系统跑通后再按需开启

```c
/* --- FreeRTOSConfig.h --- */
#define configUSE_IDLE_HOOK             0  // 关闭空闲钩子
#define configUSE_TICK_HOOK             0  // 关闭时间片钩子
#define configUSE_MALLOC_FAILED_HOOK    0  // 关闭内存分配失败钩子
#define configCHECK_FOR_STACK_OVERFLOW  0  // 关闭栈溢出检查
```
### 接管内核中断
为了让 FreeRTOS 能够接管系统心跳和任务切换，需要在 `FreeRTOSConfig.h` 的末尾（`#endif` 之前）添加中断重定向映射：
```c
/* 将 FreeRTOS 的处理函数映射到 STM32 启动文件中的标准名称 */
#define vPortSVCHandler     SVC_Handler
#define xPortPendSVHandler  PendSV_Handler
#define xPortSysTickHandler SysTick_Handler
```

> [!tip]
> 由于本教程的 `FreeRTOSConfig.h` 来自 `Demo/CORTEX_M4F_STM32F407ZG-SK` 文件夹其中已经为我们完成了此设置所以可忽略这个设置
### 解决重复定义冲突
由于在配置文件中重定向了中断，Keil 会提示 `SysTick_Handler` 等符号在 `port.o` 和 `stm32f4xx_it.o` 中重复定义
- **操作**：打开 `stm32f4xx_it.c`，**删除或注释掉** 以下三个函数：
    - `void SVC_Handler(void)`
    - `void PendSV_Handler(void)`
    - `void SysTick_Handler(void)`
        
> [!caution] 风险提示
> 注释掉 `SysTick_Handler` 后，原本依赖该中断的裸机延时函数（如 `delay.h` 里的 `delay_ms`）将由于计数器不再自减而**永久卡死**建议在系统启动后全面切换为 `vTaskDelay()`

## 开发集成
### Keil MDK 工程配置
1. **添加 Group**：
    - `FreeRTOS/src`：添加 `LIB/FreeRTOS/src` 下所有 `.c` 文件
    - `FreeRTOS/port`：添加 `port.c` 和 `heap_4.c`
2. **Include Paths**：
	- 魔法棒-> `C/C++` -> `Include Paths` -> 添加 `.\LIB\FreeRTOS\inc` 和 `.\LIB\FreeRTOS\port`
### 编译器设置
由于 FreeRTOS 涉及大量底层汇编，确保 `C/C++` 选项中未开启过于激进的优化（初次调试建议使用 `Level 0` 或 `Level 1`）且要确保 C99 Mode 为开启状态
### VSCode 跨工具链环境同步
每次在 Keil 中新增文件或修改路径后，必须运行 Python 脚本更新编译数据库：
1. **终端执行**：
    ```python
    python TOOLS/keil2json.py
    ```
2. **重启服务**：`F1` -> `Clangd: Restart language server`

---
## 下载验证
为了验证 freertos内核是否已经“准备就绪”，我们需要创建两个任务来观察是否移植成功：
1. **任务 A**：每 500ms 翻转一次 LED
2. **任务 B**：每 1000ms 通过串口发送一条消息
```c
#include "stm32f4xx.h"
#include "FreeRTOS.h"
#include "task.h"
#include "led.h"
#include "uart.h"

// 任务句柄
TaskHandle_t StartTask_Handler;

// 任务函数声明
void task_led(void *pvParameters);
void task_uart(void *pvParameters);

int main(void)
{
    /* 1. 硬件初始化 */
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_4); 
    
    LED_Init();     // 初始化 LED
    UART1_Init(115200); // 初始化串口
    
    /* 2. 创建任务 */
    // 创建 LED 闪烁任务
    xTaskCreate((TaskFunction_t )task_led,     // 任务函数
                (const char* )"task_led",      // 任务名称
                (uint16_t       )128,          // 堆栈大小
                (void* )NULL,                  // 传递参数
                (UBaseType_t    )2,            // 优先级
                (TaskHandle_t* )NULL);         // 任务句柄

    // 创建 串口打印任务
    xTaskCreate((TaskFunction_t )task_uart, 
                (const char* )"task_uart", 
                (uint16_t       )128, 
                (void* )NULL, 
                (UBaseType_t    )3,            // 优先级比 LED 高一点
                (TaskHandle_t* )NULL);

    /* 3. 启动调度器 */
    vTaskStartScheduler();          

    while(1); // 正常情况下永远不会执行到这里
}

/* LED 任务：每 500ms 闪烁一次 */
void task_led(void *pvParameters)
{
    while(1)
    {
        LED_Toggle(1); // 修改为你的 LED 翻转函数
        vTaskDelay(500); // 延时 500 个 Tick (1ms/Tick，即 500ms)
    }
}

/* UART 任务：每 1000ms 打印一次信息 */
void task_uart(void *pvParameters)
{
    while(1)
    {
        printf("FreeRTOS... \r\n");
        vTaskDelay(1000); 
    }
}

```
