---
author: 刘鑫
cssclasses:
up: "[[../../../30 - 领域/FreeRTOS]]"
prev: "[[002_1 FreeRTOS 任务管理和时间管理]]"
next: "[[004_1 FreeRTOS 信号量]]"
---
在多任务嵌入式系统开发中，**共享资源**的并发访问控制是决定系统稳定性的基石。当多个任务（Tasks）或中断服务程序（ISRs）试图同时操作同一全局变量、硬件寄存器或缓冲区时，极易产生竞态条件（Race Condition），导致数据损坏或不可预知的逻辑错误。
本文将深入探讨 FreeRTOS 下共享资源保护的多种机制，从底层硬件原理到高层 API 应用，帮助开发者构建逻辑严密、执行可靠的嵌入式程序

---

## 共享资源保护的分类

在实时操作系统中，任务对数据的“独享权”至关重要。共享资源不仅包括全局/静态变量，还涵盖 RAM 中的复杂结构体、外设寄存器以及非重入函数。

### 保护策略
选择何种保护手段，核心逻辑取决于**代码占用资源的持续时间**（即关键代码段的执行效率）。

| **资源保护方法**                   | **核心选用前提**                 | **优缺点深度解析**                                           |
| ---------------------------- | -------------------------- | ----------------------------------------------------- |
| **开关中断 (Critical Sections)** | 访问速度极快（如简单变量赋值、寄存器读写、喂狗等）。 | **优点**：最强力的保护。**缺点**：增加中断延迟，长时间关闭会导致关键硬件响应丢失。         |
| **调度器锁 (Locking Scheduler)** | 涉及任务间的数据同步，但不涉及中断（ISR）共享。  | **优点**：不影响中断响应。**缺点**：会导致当前任务事实上变成最高优先级，违背 RTOS 抢占初衷。 |
| **信号量 (Semaphores)**         | 任务可容忍长时间等待对硬件资源的访问。        | **优点**：任务级阻塞，CPU 利用率高。**缺点**：无法解决优先级反转问题。             |
| **互斥锁 (Mutexes)**            | 存在多级任务竞争且对实时性有严格要求。        | **优点**：内置**优先级继承机制**，防止优先级反转。**缺点**：执行速度较信号量稍慢。       |

### 应用场景
为了更直观地理解选型，我们通过以下四个典型案例来分析代码实现与保护机制的有机结合：
#### 内核级极速操作（如看门狗喂狗）
喂狗操作逻辑极其简单（通常仅涉及单次寄存器写操作），且必须保证操作的**绝对原子性**。此时首选**开关中断**，因为任何任务切换或中断嵌套导致的延迟，都可能使计时器溢出导致系统复位。

```c
void vTaskWatchdogKeepAlive(void *pvParameters) {
    for(;;) {
        /* 进入临界区，屏蔽所有受控中断，保证时序绝对准确 */
        taskENTER_CRITICAL(); 
        
        // 逻辑极其简单，耗时极短
        IWDG_ReloadCounter(); 
        
        /* 立即退出，减小中断延迟 */
        taskEXIT_CRITICAL(); 
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

#### 任务间简单的全局变量操作
若任务 T1 执行 `g++`，任务 T2 执行 `a = g`。如果这些变量**仅在任务之间共享**，而不涉及任何中断服务程序（ISR），使用**调度器锁**是最合适的。它能防止 T1 在执行非原子的三步自增指令（读-改-写）时被 T2 抢占，同时不影响高优先级的硬件中断响
```c
uint32_t g_system_counter = 0;

void vTaskDataProducer(void *pvParameters) {
    for(;;) {
        /* 挂起调度器，防止其他任务抢占，但允许硬件中断运行 */
        vTaskSuspendAll();
        
        g_system_counter++; // 非原子操作，受调度器锁保护
        
        /* 恢复调度器 */
        xTaskResumeAll();
    }
}
```

#### 任务与中断（ISR）深度共享变量
若一个变量在多个任务中被操作，同时在 `USART1_IRQHandler` 串口中断中也会被写入（例如接收计数），此时调度器锁将失效，必须使用**临界区 API** 来屏蔽中断干扰，否则中断可能在变量修改的中途触发，造成逻辑空洞
```c
static volatile uint32_t g_rx_count = 0;

// 任务端代码
void vTaskMonitor(void *pvParameters) {
    uint32_t local_count;
    for(;;) {
        taskENTER_CRITICAL(); // 必须关中断，因为 ISR 会修改 g_rx_count
        local_count = g_rx_count;
        g_rx_count = 0;       // 处理后清零
        taskEXIT_CRITICAL();
    }
}

// 中断端代码
void USART1_IRQHandler(void) {
    uint32_t ulReturn;
    /* 中断嵌套保护：保存当前中断掩码 */
    ulReturn = taskENTER_CRITICAL_FROM_ISR();
    
    if(USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        g_rx_count++; // 受临界区保护，防止任务端同时清零
    }
    
    /* 恢复中断掩码 */
    taskEXIT_CRITICAL_FROM_ISR(ulReturn);
}
```

#### 长耗时外设访问
打印字符串涉及复杂的时序和较长的物理链路耗时，**严禁在关中断状态下操作**。
- **双任务竞争**：使用**信号量**。其优点是释放/获取速度极快，适用于简单的二元互斥。
- **多任务（高/中/低优先级）频繁调用**：必须使用**互斥锁**，以利用其内置的**优先级继承机制**防止中优先级的“不速之客”无限期阻塞高优先级任务。
```c
SemaphoreHandle_t xMutex_UART;

void vTaskSerialLogger(void *pvParameters) {
    xMutex_UART = xSemaphoreCreateMutex(); // 创建互斥锁
    for(;;) {
        /* 获取互斥锁，若被占用则进入阻塞态，不占用 CPU */
        if(xSemaphoreTake(xMutex_UART, portMAX_DELAY) == pdPASS) {
            // 长耗时操作，允许被中断或其他高优先级任务打断（只要它们不访问串口）
            printf("System Status: %s \r\n", (char*)pvParameters);
            
            xSemaphoreGive(xMutex_UART); // 释放锁
        }
    }
}
```
    
> [!warning] 常见坑点
>
> 1. **乱用调度器锁**：在锁住调度器的情况下执行 `delay_ms(1000)`，会导致系统所有任务停摆 1 秒，这已经严重背离了实时系统的设计初衷。
>     
> 2. **锁不对称**：如果任务 A 使用互斥锁保护 OLED，而任务 B 使用互斥锁保护 DHT11，虽然都用了“锁”，但它们本质上不是同一资源。在这种情况下使用同一个锁会导致不必要的互锁等待，降低系统效率。
>     
> 3. **死锁风险**：信号量初始化时若初值为 0，而所有任务都在“等待信号量”，系统将进入永久阻塞。
>     

---

## 临界区保护
临界区是指必须原子化执行、严禁被抢占或中断打断的代码段。FreeRTOS 通过精细化操作底层 CPU 的中断屏蔽寄存器来实现这一目标。
### Cortex-M3/M4 核心寄存器
FreeRTOS 的中断管理深度依赖于 ARM 内核的三个关键寄存器：
- **PRIMASK**：全局禁止除 NMI 和 HardFault 外的所有异常。这是最“粗鲁”的关中断方式。
- **FAULTMASK**：将优先级提升至 -1，除复位外屏蔽所有中断。
- **BASEPRI**（FreeRTOS 核心）：该寄存器允许屏蔽**低于**某一特定阈值的中断。FreeRTOS 正是通过设置 BASEPRI 来实现“只关闭受 RTOS 管理的中断，而保留高精度硬件中断响应”的特性。
### FreeRTOS 配置宏与中断分层
在 `FreeRTOSConfig.h` 中，优先级的定义至关重要：
- `configMAX_SYSCALL_INTERRUPT_PRIORITY`：定义了系统管理的最高中断优先级（假设设置为 5）。
- **中断分层逻辑**：
    - **优先级 0~4**：不受系统管理。这些中断无法被 FreeRTOS 屏蔽，响应极快，但绝对不能调用任何 `FromISR` 结尾的 API。
    - **优先级 5~15**：受系统管理。进入临界区时会被暂时屏蔽，可以安全地调用系统 API。
---
### API
#### 进入任务临界区：`taskENTER_CRITICAL`
- **函数原型**：
    ```c
    void taskENTER_CRITICAL( void );
    ```

- **功能描述**： 用于任务上下文。该函数会屏蔽所有优先级低于 `configMAX_SYSCALL_INTERRUPT_PRIORITY` 的硬件中断，并递增全局嵌套计数器 `uxCriticalNesting`。其核心目标是确保当前任务对 CPU 的独占，防止被其他任务或受控中断打断。
- **参数详解**：
    - **无**。
- **返回值**：
    - **无**。
- **注意事项**：
    - **嵌套支持**：支持多次调用，但必须配对等量的 `EXIT` 操作。
    - **环境限制**：严禁在中断服务程序（ISR）中调用。
#### 退出任务临界区：`taskEXIT_CRITICAL`
- **函数原型**：
    ```c
    void taskEXIT_CRITICAL( void );
    ```
- **功能描述**： 用于任务上下文。每调用一次，内核嵌套计数器 `uxCriticalNesting` 递减。**只有当计数器减至 0 时**，系统才会通过恢复 `BASEPRI` 寄存器来重新开启硬件中断。
- **参数详解**：
    - **无**。
- **返回值**
    - **无**。
- **注意事项**：
    - **配对原则**：必须与 `taskENTER_CRITICAL` 成对出现，否则会导致中断永久性关闭。
#### 进入中断临界区：`taskENTER_CRITICAL_FROM_ISR`
- **函数原型**：
    ```
    UBaseType_t taskENTER_CRITICAL_FROM_ISR( void );
    ```
- **功能描述**： 专门用于中断服务程序（ISR）。它会保存当前 CPU 的中断屏蔽状态（BASEPRI 掩码），随后屏蔽所有受控中断，实现中断环境下的原子操作保护。
- **参数详解**：
    - **无**。
- **返回值**：
    - **`UBaseType_t`**：返回进入临界区前的中断掩码值。开发者**必须**定义变量保存此返回值，以便退出时恢复。
- **注意事项**：
    - **不可嵌套**：与任务级 API 不同，中断级临界区不使用嵌套计数器，而是依靠保存/恢复掩码来维持状态。
#### 退出中断临界区：`taskEXIT_CRITICAL_FROM_ISR`
- **函数原型**：
    ```
    void taskEXIT_CRITICAL_FROM_ISR( UBaseType_t uxSavedInterruptStatus );
    ```
- **功能描述**： 专门用于中断服务程序（ISR）。将 CPU 的中断屏蔽状态恢复至进入临界区之前的水平，确保中断嵌套逻辑的完整性。
- **参数详解**：
    - **`uxSavedInterruptStatus`**：必须传入 `taskENTER_CRITICAL_FROM_ISR` 获取的原始掩码值。
- **返回值**：
    - **无**。
- **注意事项**
    - **变量匹配**：若传入错误的掩码值，可能导致中断状态紊乱，甚至屏蔽掉不该屏蔽的高优先级中断

内核实现逻辑：
FreeRTOS 引入了临界区嵌套机制。核心变量 uxCriticalNesting 记录了嵌套深度。
```c
// 简化后的内核源码逻辑
void vPortEnterCritical( void ) {
    portDISABLE_INTERRUPTS(); // 操作 BASEPRI 关中断
    uxCriticalNesting++;      // 增加嵌套计数
    if( uxCriticalNesting == 1 ) {
        // 断言确保当前不在中断上下文中
        configASSERT( ( portNVIC_INT_CTRL_REG & portVECTACTIVE_MASK ) == 0 );
    }
}

void vPortExitCritical( void ) {
    configASSERT( uxCriticalNesting ); // 确保之前已经进入了临界区
    uxCriticalNesting--;
    if( uxCriticalNesting == 0 ) {
        portENABLE_INTERRUPTS(); // 只有当最外层退出时才真正开启中断
    }
}
```

> [!tip] 嵌套的意义
>
> 这种设计保证了如果 Function A 中包含了临界区，而 Function B 在其自身的临界区内调用了 A，当 A 退出时并不会立即开启中断，从而保护了 B 剩余代码的安全。



---

### 优先级对临界区的影响
抢占式优先级分组为 4（即 `NVIC_PriorityGroup_4`），并设定 FreeRTOS 系统管理的中断阈值 `configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY` 为 **5**
在这种配置下，中断优先级在 **5~15** 之间受系统管理，而 **0~4** 则属于内核无法触达的非屏蔽区域。
#### 场景一：受控低优先级中断（优先级 6）
当外设（如串口 1）的中断抢占优先级设置为 **6** 时，它处于 FreeRTOS 的管理范围内。一旦任务进入临界区，BASEPRI 寄存器会被设置为 5，从而屏蔽所有优先级数值大于或等于 5 的中断。
```c
// 串口 1 初始化：抢占优先级设为 6 (低于系统阈值 5)
NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 6; 

void vTaskMonitor(void *pvParameters) {
    uint32_t i;
    for(;;) {
        /* 进入临界区，此时 BASEPRI 屏蔽优先级 5-15 的中断 */
        taskENTER_CRITICAL(); 
        
        printf("Task: Entered Critical Section. \r\n");
        
        // 模拟长耗时操作：此时即使外部给串口发送数据，串口中断也无法立即响应
        i = 0x1FFFFFF; 
        while(i--); 
        
        printf("Task: Exiting Critical Section. \r\n");
        
        /* 退出临界区，恢复中断响应 */
        taskEXIT_CRITICAL(); 
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 串口 1 中断服务程序
void USART1_IRQHandler(void) {
    // 只有当任务调用完 taskEXIT_CRITICAL 后，此处的代码才会被执行
    if(USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        printf("ISR: Received Data (Priority 6). \r\n");
        USART_ClearITPendingBit(USART1, USART_IT_RXNE);
    }
}
```

**现象分析**：在任务执行长耗时循环期间，串口中断被硬件挂起。外部发送的数据必须等待任务退出临界区后，中断服务程序才会被触发并打印接收信息。

---

#### 场景二：非受控高优先级中断（优先级 4）
当串口 1 的抢占优先级设置为 **4** 时，其优先级高于系统管理阈值。BASEPRI 寄存器的屏蔽操作对这类中断无效，它们拥有“穿透”临界区的能力。
```c
// 串口 1 初始化：抢占优先级设为 4 (高于系统阈值 5)
NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 4; 

void vTaskMonitor(void *pvParameters) {
    uint32_t i;
    for(;;) {
        taskENTER_CRITICAL(); 
        
        printf("Task: Inside Critical Section. \r\n");

        // 模拟长耗时操作：临界区无法阻止优先级 4 的中断触发
        i = 0x1FFFFFF; 
        while(i--); 
        
        taskEXIT_CRITICAL(); 
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// 串口 1 中断服务程序
void USART1_IRQHandler(void) {
    // 即使任务正处于临界区内，此中断依然会立即打断循环并执行
    if(USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
        // 注意：此处严禁调用 FreeRTOS API
        printf("ISR: Immediate Response (Priority 4). \r\n");
        USART_ClearITPendingBit(USART1, USART_IT_RXNE);
    }
}
```

**现象分析**：即使任务在临界区内进行耗时计算，只要外部有串口数据输入，CPU 就会立即停下任务去处理 `USART1_IRQHandler`。这种机制确保了极高精度的硬件响应，但也带来了巨大的风险。

> [!danger] 核心准则
>
> 如果中断优先级高于系统阈值（如示例 2 中的 4），虽然响应快，但严禁调用 API。如果在该中断中使用 xQueueSendFromISR，将导致内核数据结构在临界区内被非法篡改，引发系统崩溃。

---

## 调度器控制
当保护逻辑仅限于任务之间，且不希望影响中断响应（保持高实时性中断处理）时，应使用调度器挂起机制。这种方法比进入临界区更“轻量”，因为它允许外设中断正常触发，仅仅是暂时禁止了任务的抢占与切换。
### 挂起调度器：`vTaskSuspendAll`
- **函数原型**：
    ```c
    void vTaskSuspendAll( void );
    ```
- **功能描述**： 强制停止实时操作系统（RTOS）的内核进行任务切换。调用后，当前任务将持续占用 CPU，不会被更高优先级的任务抢占。**此机制仅限制调度器，硬件中断（ISR）仍保持活跃状态并能正常响应。**
- **参数详解**：
    - **无**。
- **返回值**：
    - **无**。
- **注意事项**：
    - **禁止阻塞调用**：在调度器挂起期间，绝对不能调用任何可能导致任务进入阻塞态的 API 函数（如 `vTaskDelay()`、获取信号量等），否则会导致系统逻辑锁死。
    - **嵌套支持**：该函数支持嵌套调用，但必须保证 `vTaskSuspendAll()` 与 `xTaskResumeAll()` 在逻辑上成对出现。
### 恢复调度器：`xTaskResumeAll`
- **函数原型**：
    ```c
    BaseType_t xTaskResumeAll( void );
    ```
- **功能描述**： 重新开启内核的调度机制。该函数会评估在调度器挂起期间是否有更高优先级的任务因中断触发而进入就绪态。如果存在此类任务，则在退出函数前立即触发一次上下文切换
- **参数详解**：
    - **无**。
- **返回值**：
    - 返回 `pdTRUE`：表示在恢复过程中触发了任务切换（有更高优先级任务抢占了 CPU）
    - 返回 `pdFALSE`：表示未发生任务切换，系统继续执行当前任务
- **注意事项**：
    - **执行开销**：如果在挂起期间发生了多次中断并唤醒了多个任务，`xTaskResumeAll` 的执行时间会相对较长，因为它需要逐一处理挂起的就绪任务列表
    - **调用环境**：严禁在中断服务函数（ISR）中调用此函数
        
> [!tip] 调度器锁与临界区的权衡
> 使用 `vTaskSuspendAll` 保护资源时，系统的硬件中断（如定时器、串口接收）依然能够得到及时响应，这对于需要高精度时序控制的外设应用至关重要。相比之下，`taskENTER_CRITICAL` 会彻底屏蔽中断，应尽量缩短其驻留时间。


~~~c
// 使用示例
void SharedVariableUpdate (void) {
    vTaskSuspendAll (); // 挂起调度器
    /* 此时中断依然在后台运行，但任务不会被抢占 */
    g_data_buffer[0]++; 
    xTaskResumeAll ();  // 恢复调度器
}
~~~
## 信号量
见 [004_1 FreeRTOS 信号量](004_1%20FreeRTOS%20信号量.md)
## 互斥信号量
见 [005_1 FreeRTOS 互斥量](005_1%20FreeRTOS%20互斥量.md)