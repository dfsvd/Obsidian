> [!INFO] 前言
>
> 在 C 语言中，没有像 Python 或 Java 那样内置的 split() 函数。开发者需要根据具体场景（是否允许修改原串、是否需要线程安全、是否处理空字段）选择不同的方案。

---
## 1. 经典之选：`strtok`
`strtok` 是标准库 `<string.h>` 提供的最常用函数，通过将分隔符替换为 `\0` 来分割字符串。


熟练配置 DMA、ADC、PWM 等外设

> [!EXAMPLE] 代码示例
>
> C
>
> ```
> char str[] = "apple,banana,cherry";
> char *token = strtok(str, ",");
> while (token != NULL) {
>     printf("%s\n", token);
>     token = strtok(NULL, ","); // 后续调用第一个参数需传 NULL
> }
> ```

> [!WARNING] 注意事项
>
> 1. **修改原串**：它会直接改变输入的字符串。
>     
> 2. **非线程安全**：内部使用静态变量记录进度。
>     
> 3. **跳过空字段**：遇到连续分隔符（如 `a,,b`）时，它会跳过空的部分。
>     

---

## 2. 线程安全版：`strtok_r`

它是 `strtok` 的可重入版本（POSIX 标准），通过一个显式的指针来保存上下文，解决了多线程安全问题。

> [!TIP] 适用场景：多线程环境
>
> C
>
> ```
> char str[] = "192.168.1.1";
> char *saveptr;
> char *token = strtok_r(str, ".", &saveptr);
> while (token != NULL) {
>     printf("%s\n", token);
>     token = strtok_r(NULL, ".", &saveptr);
> }
> ```

---

## 3. 处理空字段：`strsep`

`strsep` 是 `strtok` 的增强版（主要见于 BSD/Linux）。它不会跳过连续的分隔符，非常适合解析 CSV 这种可能存在空列的数据。

> [!IMPORTANT] 核心区别
>
> 如果输入是 a,,b：
>
> - `strtok` 返回：`a`, `b`
>     
> - `strsep` 返回：`a`, `""` (空串), `b`
>     

> C
>
> ```
> char *stringp = strdup("a,,b"); // 必须是可写的内存
> char *token;
> while ((token = strsep(&stringp, ",")) != NULL) {
>     printf("Token: [%s]\n", token);
> }
> ```

---

## 4. 格式化提取：`sscanf`

如果你处理的是**固定格式**的字符串（例如日志、配置文件），`sscanf` 是最优雅的选择。

> [!SUCCESS] 模式匹配与类型转换
>
> sscanf 可以在切割的同时完成数据类型转换（如转为 int），且不修改原串。
>
> C
>
> ```
> const char *info = "User:Gemini,ID:1024";
> char name[20];
> int id;
> // %[^,] 表示匹配直到遇到逗号
> sscanf(info, "User:%[^,],ID:%d", name, &id);
> ```
>
> > [!NOTE] 技巧：%n 参数
> >
> > 可以使用 %n 来记录 sscanf 处理了多少个字符，配合指针偏移可以实现循环解析。

---

## 5. 高级/非破坏性：手动指针处理

如果你不想修改原始字符串，也不想使用动态分配内存，可以使用 `strchr` 配合偏移量。

> [!ABSTRACT] 逻辑实现
>
> 1. 使用 `p = strchr(start, delimiter)` 查找位置。
>     
> 2. 片段长度 `len = p - start`。
>     
> 3. 使用 `strncpy` 拷贝或直接处理该长度的内存。
>     
> 4. `start = p + 1` 进入下一次循环。
>     
