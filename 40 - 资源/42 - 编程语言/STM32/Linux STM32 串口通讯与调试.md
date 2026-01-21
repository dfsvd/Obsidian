本笔记记录了在 Arch Linux 环境下，针对 **STM32F407ZET6** 开发板进行串口（UART）通讯的配置与调试方案
## 软件适配：GCC 重定向 `printf`
在 Arch Linux 使用 `arm-none-eabi-gcc` 编译时，标准库 `printf` 的底层逻辑与 Keil (ARMCC) 有本质区别
- **核心修改**：必须完全移除 Keil 特有的 `#pragma import(__use_no_semihosting)`、`fputc` 函数及 `_sys_exit` 等桩函数
- **GCC 实现**：需在 `uart.c` 中重写 `_write` 函数以对接硬件，这是 `printf` 最终调用的系统接口：
```c
#include <stdio.h>

// 适配 GCC 的重定向
int _write(int file, char *ptr, int len) {
    for (int i = 0; i < len; i++) {
        // 使用标准库函数发送字节
        USART_SendData(USART1, (uint8_t)ptr[i]);
        // 等待发送缓冲区为空
        while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    }
    return len;
}
```
---
## 编译配置：链接 Specs 文件
由于单片机是裸机环境，`printf` 调用的底层接口（如 `_sbrk`）需要桩函数支持
- **`--specs=nosys.specs`**：这是解决 `undefined reference` 链接错误的关键它为缺失的系统调用提供了默认的空实现
- **避坑说明**：**不要**手动在 `CMakeLists.txt` 中添加 `--specs=nano.specs`因为你使用的工具链文件（`gcc-arm-none-eabi.cmake`）通常已内置此项，重复添加会触发 `nano_link` 已定义的致命错误
---
## 硬件适配：修正时钟频率 (HSE)
乱码问题的根源在于物理晶振与代码定义的频率不一致，导致波特率计算偏差
### 关键参数修改
针对 stm32 常见的 **8MHz** 外部晶振，必须同步修改以下两处：
- **`stm32f4xx.h` (约 L123)**：将 `HSE_VALUE` 修改为 `8000000`
- **`system_stm32f4xx.c` (约 L316)**：将 `PLL_M` 修改为 `8`,这一步确保进入 PLL 的频率恒定为 $1\text{MHz}$，从而使系统主频锁定在 $168\text{MHz}$，确保串口时钟准确
---
## Linux 端的查看与交互
### 设备识别：确定串口号
在 Linux 中，USB 转串口设备通常以文件形式存在于 `/dev/` 目录下。
- **快速查询**：使用 `ls` 命令查看当前连接的 USB 串口设备：
    ```Bash
    ls /dev/ttyUSB*
    ```

    通常结果为 `/dev/ttyUSB0`。如果是带有 CDC/ACM 协议的设备，则可能显示为 `/dev/ttyACM0`
    
> [!tip] **动态确认**
> 如果不确定哪个是开发板，可以先拔掉设备，运行 `dmesg -w`（持续监控内核日志），然后插上设备。终端会即时打印出新识别到的设备名。
### 权限预处理（仅需执行一次）
在 Arch Linux 中，串口设备默认属于 `uucp` 组为了避免每次都加 `sudo`，请执行以下命令将自己加入该组：
```sh
sudo usermod -aG uucp $USER
```

> [!tip]
> 执行后需要**注销并重新登录**（或重启）才能生效

### 接收方式
#### 命令行Minicom（最推荐）
这是嵌入式开发者的标准配置
1. **安装**：`sudo pacman -S minicom`
2. **运行**：
    ```Bash
    minicom -D /dev/ttyUSB0 -b 115200
    ```
    - _技巧_：按下 `Ctrl+A` 再按 `Z` 可以调出菜单
    - _退出_：按下 `Ctrl+A` 再按 `Q`
#### VS Code 内置串口监视器

 VS Code 直接集成不需要额外的软件，借助于插件 **"Serial Monitor"**
1. 在 VS Code 左侧插件栏搜索并安装 `Serial Monitor`
2. 在底部状态栏选择串行监视器
3. **端口** 选择 `/dev/ttyUSB0`，**波特率** 选 `115200`
4. 点击 **开始监视** 即可在编辑器内部查看输出
![示意图](images/Linux%20STM32%20串口通讯与调试/file-20260119150242472.jpg)
---
## 常见问题
- **显示乱码**：首选检查 `HSE_VALUE` 和 `PLL_M` 是否为 `8000000` 和 `8`
- **编译报错 `nano_link`**：立即检查 `CMakeLists.txt` 是否重复添加了 `nano.specs`，如有则将其删除
- **Minicom 黑屏**：确认 PA9(TX) 和 PA10(RX) 未接反，并检查硬件流控（Hardware Flow Control）是否已关闭
- **链接报错 `_sbrk`**：确认 `CMakeLists.txt` 的 `target_link_options` 中已包含 `--specs=nosys.specs`