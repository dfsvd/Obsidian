一、概述

TFT-LCD 即薄膜晶体管液晶显示器。其英文全称为：Thin Film Transistor-Liquid Crystal Display。TFT-LCD 与无源 TN-LCD、STN-LCD 的简单矩阵不同，它在液晶显示屏的每一个象素上都设置有一个薄膜晶体管（TFT），可有效地克服非选通时的串扰，使显示液晶屏的静态特性与扫描线数无关，因此大大提高了图像质量。TFT-LCD 也被叫做真彩液晶显示器。

模块原理图如图
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161847949.jpg)

TFTLCD 模块采用 16 位的并方式与外部连接，之所以不采用 8 位的方式，是因为彩屏的数据量比较大，尤其在显示图片的时候，如果用 8 位数据线，就会比 16 位方式慢一倍以上，我们当然希望速度越快越好，所以我们选择 16 位的接口。上图还列出了触摸屏芯片的接口。该模块的 80 并口有如下一些信号线：

- CS：TFTLCD 片选信号。
- WR：向 TFTLCD 写入数据。
- RD：从 TFTLCD 读取数据。
- D[15：0]：16 位双向数据线。
- RST：硬复位 TFTLCD。
- RS：命令/数据标志（0，读写命令；1，读写数据）。

|   |   |   |
|---|---|---|
|STM32F407 FSMC|​ILI9341|​说明|
|FSMC_D[15:0]|D[15:0]|16位数据总线|
|FSMC_NWE|WRX|写使能（低有效）|
|FSMC_NOE|RDX|读使能（低有效）|
|FSMC_A6|D/CX(RS)|数据/命令选择|
|FSMC_NE4|CSX|片选（Bank1 Sector4）|

二、ILI9341 TFT LCD控制器详解

ILI9341是一款广泛使用的262K色TFT LCD控制器芯片，支持240x320分辨率，以下是其核心特性与工作原理：

2.1 基本特性

1. ​显示参数​：

- 分辨率：240(RGB)×320 (QVGA)
- 色彩深度：18位/像素（262K色）
- 可视角度：典型70°（全视角改良型号可达160°）

2. ​接口支持​：

- 8/9/16/18位并行8080接口
- 3/4线SPI接口（最高50MHz）
- 支持RGB 6/16/18位直接驱动接口

3. ​显存架构​：

- 内置172.8KB GRAM（240×320×18/8）
- 支持局部刷新和窗口地址设置

2.2 硬件接口

1. ​关键控制信号​：

- RESX：硬复位（低有效）
- CSX：片选（低有效）
- D/CX：数据/命令选择（H:数据，L:命令）
- WRX：写使能（8080模式）
- RDX：读使能（8080模式）

2. ​数据总线​：

- D[17:0]：18位并行数据总线
- 支持8/16/18位可配置模式

3. ​电源要求​：

- VCC：2.8V-3.3V（逻辑电源）
- VCI：2.5V-3.3V（接口电源）
- LED背光：典型3.3V/120mA

4. 引脚连接：

ILI9341 液晶控制器自带显存，其显存总大小为 172800（240*320*18/8），即 18 位模式（26万色）下的显存量。在 16 位模式下，ILI9341 采用 RGB565 格式存储颜色数据，此时 ILI9341的18 位数据线与 MCU 的 16 位数据线以及 LCD GRAM 的对应关系如下图所示：
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161857579.jpg)

从图中可以看出，ILI9341 在 16 位模式下面，数据线有用的是：D17~D13 和D11~D1，D0和D12 没有用到，实际上在我们 LCD 模块里面，ILI9341 的 D0 和 D12 压根就没有引出来，这样，ILI9341 的 D17~D13 和 D11~D1 对应 MCU 的 D15~D0。

这样 MCU 的 16 位数据，最低 5 位代表蓝色，中间 6 位为绿色，最高 5 位为红色。数值越大，表示该颜色越深。

2.3 指令

1、读ID，0xD3

接下来，我们介绍一下 ILI9341 的几个重要命令，因为 ILI9341 的命令很多，我们这里就不全部介绍了，有兴趣的大家可以找到 ILI9341 的 datasheet 看看。里面对这些命令有详细的介绍。我们将介绍：0XD3，0X36，0X2A，0X2B，0X2C，0X2E 等 6 条指令。首先来看指令：0XD3，这个是读 ID4 指令，用于读取 LCD 控制器的 ID，该指令如下表所示：
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161906317.jpg)

从上表可以看出，0XD3 指令后面跟了 4 个参数，最后 2 个参数，读出来是 0X93 和 0X41，刚好是我们控制器 ILI9341 的数字部分，从而，通过该指令，即可判别所用的 LCD 驱动器是什么型号，这样，我们的代码，就可以根据控制器的型号去执行对应驱动 IC 的初始化代码，从而兼容不同驱动 IC 的屏，使得一个代码支持多款 LCD。

2、存储访问控制，0x36

接下来看指令：0X36，这是存储访问控制指令，可以控制 ILI9341 存储器的读写方向，简单的说，就是在连续写 GRAM 的时候，可以控制 GRAM 指针的增长方向，从而控制显示方式（读 GRAM 也是一样）。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161912733.jpg)

从上表可以看出，0X36 指令后面，紧跟一个参数，这里我们主要关注：MY、MX、MV这三个位，通过这三个位的设置，我们可以控制整个 ILI9341 的全部扫描方向
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161918290.jpg)

这样，我们在利用 ILI9341 显示内容的时候，就有很大灵活性了，比如显示 BMP 图片，BMP 解码数据，就是从图片的左下角开始，慢慢显示到右上角，如果设置 LCD 扫描方向为从左到右，从下到上，那么我们只需要设置一次坐标，然后就不停的往 LCD 填充颜色数据即可，这样可以大大提高显示速度。

3、列地址设置指令，0x2A

接下来看指令：0X2A，这是列地址设置指令，在从左到右，从上到下的扫描方式（默认）下面，该指令用于设置横坐标（x 坐标）
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161926199.jpg)

在默认扫描方式时，该指令用于设置 x 坐标，该指令带有 4 个参数，实际上是 2 个坐标值：SC 和 EC，即列地址的起始值和结束值，SC 必须小于等于 EC，且 0≤SC/EC≤239。一般在设置 x 坐标的时候，我们只需要带 2 个参数即可，也就是设置 SC 即可，因为如果 EC 没有变化，我们只需要设置一次即可（在初始化 ILI9341 的时候设置），从而提高速度。

4、页地址设置指令，0x2B

与 0X2A 指令类似，指令：0X2B，是页地址设置指令，在从左到右，从上到下的扫描方式（默认）下面，该指令用于设置纵坐标（y 坐标）。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161936716.jpg)

在默认扫描方式时，该指令用于设置 y 坐标，该指令带有 4 个参数，实际上是 2 个坐标值：SP 和 EP，即页地址的起始值和结束值，SP 必须小于等于 EP，且 0≤SP/EP≤319。一般在设置y 坐标的时候，我们只需要带 2 个参数即可，也就是设置 SP 即可，因为如果 EP 没有变化，我们只需要设置一次即可（在初始化 ILI9341 的时候设置），从而提高速度。

5、写显存指令，0x2C

接下来看指令：0X2C，该指令是写 GRAM 指令，在发送该指令之后，我们便可以往 LCD的 GRAM 里面写入颜色数据了，该指令支持连续写。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161945269.jpg)

从上表可知，在收到指令 0X2C 之后，数据有效位宽变为 16 位，我们可以连续写入 LCD GRAM 值，而 GRAM 的地址将根据 MY/MX/MV 设置的扫描方向进行自增。例如：假设设置的是从左到右，从上到下的扫描方式，那么设置好起始坐标（通过 SC，SP 设置）后，每写入一个颜色值，GRAM 地址将会自动自增 1（SC++），如果碰到 EC，则回到 SC，同时 SP++，一直到坐标：EC，EP 结束，其间无需再次设置的坐标，从而大大提高写入速度。

6、读显存指令，0x2E

最后，来看看指令：0X2E，该指令是读 GRAM 指令，用于读取 ILI9341 的显存（GRAM），该指令在 ILI9341 的数据手册上面的描述是有误的，真实的输出情况如表。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126161952745.jpg)

该指令用于读取 GRAM，如上表 所示，ILI9341 在收到该指令后，第一次输出的是dummy 数据，也就是无效的数据，第二次开始，读取到的才是有效的 GRAM 数据（从坐标：SC，SP 开始），输出规律为：每个颜色分量占 8 个位，一次输出 2 个颜色分量。比如：第一次输出是 R1G1，随后的规律为：B1R2→G2B2→R3G3→B3R4→G4B4→R5G5... 以此类推。如果我们只需要读取一个点的颜色值，那么只需要接收到参数 3 即可，如果要连续读取（利用 GRAM地址自增，方法同上），那么就按照上述规律去接收颜色数据。

以上，就是操作 ILI9341 常用的几个指令，通过这几个指令，我们便可以很好的控制 ILI9341显示我们所要显示的内容了。

2.4 使用流程

一般 TFTLCD 模块的使用流程如下图。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126162001685.jpg)

任何 LCD，使用流程都可以简单的用以上流程图表示。其中硬复位和初始化序列，只需要执行一次即可。而画点流程就是：设置坐标→写 GRAM 指令→写入颜色数据，然后在 LCD 上面，我们就可以看到对应的点显示我们写入的颜色了。读点流程为：设置坐标→读 GRAM 指令→读取颜色数据，这样就可以获取到对应点的颜色数据了。

TFTLCD 显示需要的相关设置步骤如下：

1）设置 STM32F4 与 TFTLCD 模块相连接的 IO。

这一步，先将我们与 TFTLCD 模块相连的 IO 口进行初始化，以便驱动 LCD。这里我们用到的是 FSMC。

2）初始化 TFTLCD 模块。

TFTLCD 的 RST 同 STM32F4 的 RESET 连接在一起，只要按下开发板的 RESET键，就会对 LCD 进行硬复位。初始化序列，就是向 LCD 控制器写入一系列的设置值，这些初始化序列一般 LCD 供应商会提供给客户，我们直接使用这些序列即可，不需要深入研究。在初始化之后，LCD 才可以正常使用。

3）通过函数将字符和数字显示到 TFTLCD 模块上。

设置坐标→写 GRAM 指令→写 GRAM 来实现。

2.5 关键代码

#define __IO volatile typedef __IO uint16_t vu16; //LCD地址结构体 typedef struct { vu16 LCD_REG; vu16 LCD_RAM; } LCD_TypeDef; #define LCD_BASE ((u32)(0x6C000000 | 0x0000007E))

1. 基地址选择 (0x6C000000)

0x6C000000对应FSMC的Bank1 sector4地址空间

- STM32的FSMC将外部存储器分为4个Bank
- Bank1又分为4个sector(子区域)，每个64MB
- sector4地址范围：0x6C000000 - 0x6FFFFFFF

2. 地址偏移量 (0x0000007E，二进制编码为0111 1110)

A6作为D/CX(数据/命令)控制线

- 当A6=0时：表示命令操作(寄存器地址)
- 当A6=1时：表示数据操作(寄存器值或像素数据)

- LCD->LCD_REG地址为(0x6C000000 | 0x0000007E)，内部地址会自动右移，则Bit6为0。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126162013200.jpg)

- LCD->LCD_RAM在原来的LCD_BASE地址偏移两个字节，才指向LCD_RAM成员，地址为(0x6C000000 |(0x0000007E+2))则Bit6为1。
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126162019511.jpg)

3.代码

//LCD地址结构体 typedef struct { vu16 LCD_REG; vu16 LCD_RAM; } LCD_TypeDef; #define LCD_BASE ((u32)(0x6C000000 | 0x0000007E)) #define LCD ((LCD_TypeDef *) LCD_BASE)

//写寄存器函数 //regval:寄存器值 void LCD_WR_REG(vu16 regval) { regval = regval; //使用-O2优化的时候,必须插入的延时 LCD->LCD_REG = regval; //写入要写的寄存器序号 } //写LCD数据 //data:要写入的值 void LCD_WR_DATA(vu16 data) { data = data; //使用-O2优化的时候,必须插入的延时 LCD->LCD_RAM = data; } // 初始化序列示例 void LCD_Init(void) { LCD_WR_REG(0xCF); // 发送命令 LCD_WR_DATA(0x00); // 发送参数 LCD_WR_DATA(0xC1); // ...更多初始化命令 }

三、时间参数

3.1 显示并行18/16/9/8位接口时序特性
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126162027706.jpg)
![](../../44%20-%20硬件/电路设计/images/TFT/file-20260126162033949.jpg)

void LCD_Init(void) { vu32 i = 0; GPIO_InitTypeDef GPIO_InitStructure; /* FSMC NOR/SRAM初始化结构体 */ FSMC_NORSRAMInitTypeDef FSMC_NORSRAMInitStructure; /* 读/写时序配置结构体（用于普通模式） */ FSMC_NORSRAMTimingInitTypeDef readWriteTiming; /* 写时序配置结构体（用于扩展模式） */ FSMC_NORSRAMTimingInitTypeDef writeTiming; RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB | RCC_AHB1Periph_GPIOD | RCC_AHB1Periph_GPIOE | RCC_AHB1Periph_GPIOF | RCC_AHB1Periph_GPIOG, ENABLE); // 使能PD,PE,PF,PG时钟 RCC_AHB3PeriphClockCmd(RCC_AHB3Periph_FSMC, ENABLE); // 使能FSMC时钟 GPIO_InitStructure.GPIO_Pin = GPIO_Pin_15; // PB15 推挽输出,控制背光 GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT; // 普通输出模式 GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; // 推挽输出 GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz; // 100MHz GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; // 上拉 GPIO_Init(GPIOB, &GPIO_InitStructure); // 初始化 //PB15 推挽输出,控制背光 GPIO_InitStructure.GPIO_Pin = (3 << 0) | (3 << 4) | (7 << 8) | (3 << 14); // PD0,1,4,5,8,9,10,14,15 AF OUT GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF; // 复用输出 GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; // 推挽输出 GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz; // 100MHz GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; // 上拉 GPIO_Init(GPIOD, &GPIO_InitStructure); // 初始化 GPIO_InitStructure.GPIO_Pin = (0X1FF << 7); // PE7~15,AF OUT GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF; // 复用输出 GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; // 推挽输出 GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz; // 100MHz GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; // 上拉 GPIO_Init(GPIOE, &GPIO_InitStructure); // 初始化 GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12; // PF12,FSMC_A6 GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF; // 复用输出 GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; // 推挽输出 GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz; // 100MHz GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; // 上拉 GPIO_Init(GPIOF, &GPIO_InitStructure); // 初始化 GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12; // PF12,FSMC_A6 GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF; // 复用输出 GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; // 推挽输出 GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz; // 100MHz GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; // 上拉 GPIO_Init(GPIOG, &GPIO_InitStructure); // 初始化 GPIO_PinAFConfig(GPIOD, GPIO_PinSource0, GPIO_AF_FSMC); // PD0,AF12 GPIO_PinAFConfig(GPIOD, GPIO_PinSource1, GPIO_AF_FSMC); // PD1,AF12 GPIO_PinAFConfig(GPIOD, GPIO_PinSource4, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource5, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource8, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource9, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource10, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource14, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOD, GPIO_PinSource15, GPIO_AF_FSMC); // PD15,AF12 GPIO_PinAFConfig(GPIOE, GPIO_PinSource7, GPIO_AF_FSMC); // PE7,AF12 GPIO_PinAFConfig(GPIOE, GPIO_PinSource8, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource9, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource10, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource11, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource12, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource13, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource14, GPIO_AF_FSMC); GPIO_PinAFConfig(GPIOE, GPIO_PinSource15, GPIO_AF_FSMC); // PE15,AF12 GPIO_PinAFConfig(GPIOF, GPIO_PinSource12, GPIO_AF_FSMC); // PF12,AF12 GPIO_PinAFConfig(GPIOG, GPIO_PinSource12, GPIO_AF_FSMC); /******************** 读时序配置 ********************/ /* 地址建立时间=16个HCLK(96ns@168MHz)，对应时序图t_ast和表格tast(最小0ns) */ readWriteTiming.FSMC_AddressSetupTime = 0XF; /* 地址保持时间=0，模式A不使用，对应表格taht(最小0ns) */ readWriteTiming.FSMC_AddressHoldTime = 0x00; /* 数据建立时间=60个HCLK(360ns)，对应： - 时序图t_dst - 表格trcsfm(读全模式最小355ns)和tdst(写数据建立最小10ns) */ readWriteTiming.FSMC_DataSetupTime = 60; /* 总线转换时间=0，不用于NOR/SRAM接口 */ readWriteTiming.FSMC_BusTurnAroundDuration = 0x00; /* 时钟分频=0，保持FSMC时钟与HCLK同步 */ readWriteTiming.FSMC_CLKDivision = 0x00; /* 数据延迟=0，NOR/SRAM接口不需要 */ readWriteTiming.FSMC_DataLatency = 0x00; /* 访问模式=模式A，对应8080接口时序 */ readWriteTiming.FSMC_AccessMode = FSMC_AccessMode_A; /******************** 写时序配置 ********************/ /* 地址建立时间=9个HCLK(54ns)，对应： - 时序图t_ast - 表格tcs(写操作最小15ns) */ writeTiming.FSMC_AddressSetupTime = 9; /* 地址保持时间=0，模式A不使用 */ writeTiming.FSMC_AddressHoldTime = 0x00; /* 数据建立时间=8个HCLK(48ns)，对应： - 时序图t_dst - 表格tdst(最小10ns)和twrl(写脉冲低电平最小15ns) */ writeTiming.FSMC_DataSetupTime = 8; /* 总线转换时间=0 */ writeTiming.FSMC_BusTurnAroundDuration = 0x00; /* 时钟分频=0 */ writeTiming.FSMC_CLKDivision = 0x00; /* 数据延迟=0 */ writeTiming.FSMC_DataLatency = 0x00; /* 访问模式=模式A */ writeTiming.FSMC_AccessMode = FSMC_AccessMode_A; /******************** FSMC主配置 ********************/ /* 使用Bank1的NORSRAM4(地址范围0x6C000000-0x6FFFFFFF) */ FSMC_NORSRAMInitStructure.FSMC_Bank = FSMC_Bank1_NORSRAM4; /* 禁用地址/数据复用，8080接口需独立信号线 */ FSMC_NORSRAMInitStructure.FSMC_DataAddressMux = FSMC_DataAddressMux_Disable; /* 存储器类型配置为SRAM(实际连接LCD的8080接口) */ FSMC_NORSRAMInitStructure.FSMC_MemoryType = FSMC_MemoryType_SRAM; /* 16位数据总线，对应ILI9341的D[15:0]接口 */ FSMC_NORSRAMInitStructure.FSMC_MemoryDataWidth = FSMC_MemoryDataWidth_16b; /* 禁用突发访问模式，LCD不支持突发传输 */ FSMC_NORSRAMInitStructure.FSMC_BurstAccessMode = FSMC_BurstAccessMode_Disable; /* 等待信号极性低有效(未使用) */ FSMC_NORSRAMInitStructure.FSMC_WaitSignalPolarity = FSMC_WaitSignalPolarity_Low; /* 禁用异步等待 */ FSMC_NORSRAMInitStructure.FSMC_AsynchronousWait = FSMC_AsynchronousWait_Disable; /* 禁用回绕模式 */ FSMC_NORSRAMInitStructure.FSMC_WrapMode = FSMC_WrapMode_Disable; /* 等待信号在等待状态前激活 */ FSMC_NORSRAMInitStructure.FSMC_WaitSignalActive = FSMC_WaitSignalActive_BeforeWaitState; /* 使能写操作，必须开启才能写入LCD */ FSMC_NORSRAMInitStructure.FSMC_WriteOperation = FSMC_WriteOperation_Enable; /* 禁用等待信号，ILI9341不需要插入等待状态 */ FSMC_NORSRAMInitStructure.FSMC_WaitSignal = FSMC_WaitSignal_Disable; /* 使能扩展模式，允许读写使用独立时序 */ FSMC_NORSRAMInitStructure.FSMC_ExtendedMode = FSMC_ExtendedMode_Enable; /* 禁用写突发，LCD不支持 */ FSMC_NORSRAMInitStructure.FSMC_WriteBurst = FSMC_WriteBurst_Disable; /* 关联读/写时序结构体 */ FSMC_NORSRAMInitStructure.FSMC_ReadWriteTimingStruct = &readWriteTiming; /* 关联写时序结构体(扩展模式生效) */ FSMC_NORSRAMInitStructure.FSMC_WriteTimingStruct = &writeTiming; /* 应用FSMC配置到寄存器 */ FSMC_NORSRAMInit(&FSMC_NORSRAMInitStructure); /* 使能Bank1的NORSRAM4控制器 */ FSMC_NORSRAMCmd(FSMC_Bank1_NORSRAM4, ENABLE); //............ }

四、关键变量与函数

//LCD初始化 LCD_Init(); //点亮背光 LCD_LED = 1; //设置LCD显示方向 // dir:0,竖屏；1,横屏 void LCD_Display_Dir(u8 dir) //设置LCD的自动扫描方向 #define L2R_U2D 0 //从左到右,从上到下 #define L2R_D2U 1 //从左到右,从下到上 #define R2L_U2D 2 //从右到左,从上到下 #define R2L_D2U 3 //从右到左,从下到上 #define U2D_L2R 4 //从上到下,从左到右 #define U2D_R2L 5 //从上到下,从右到左 #define D2U_L2R 6 //从下到上,从左到右 #define D2U_R2L 7 //从下到上,从右到左 void LCD_Scan_Dir(u8 dir) //清屏函数 // color:要清屏的填充色 void LCD_Clear(u16 color) // 重设屏幕的宽度与高度 lcddev.width=320; lcddev.height=240; //设置窗口,并自动设置画点坐标到窗口左上角(sx,sy). // sx,sy:窗口起始坐标(左上角) // width,height:窗口宽度和高度,必须大于0!! //窗体大小:width*height. void LCD_Set_Window(u16 sx, u16 sy, u16 width, u16 height) //在指定区域内填充单个颜色 //(sx,sy),(ex,ey):填充矩形对角坐标,区域大小为:(ex-sx+1)*(ey-sy+1) // color:要填充的颜色 void LCD_Fill(u16 sx, u16 sy, u16 ex, u16 ey, u16 color)


