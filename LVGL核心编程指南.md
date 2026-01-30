# LVGL 核心编程指南：从基础对象到事件驱动

**角色：** 资深嵌入式工程师 / 技术专栏作家

LVGL (Light and Versatile Graphics Library) 是一个功能强大的开源嵌入式图形库。要精通 LVGL，不能仅仅停留在调用 API 的层面，必须深入理解其背后的**面向对象设计思想**、**盒子模型**、**样式系统**以及**事件驱动机制**。本文将基于官方 v8.2 版本，将零散的知识点整合为一套完整的核心编程方法论。

---

## 一、 LVGL 的面向对象哲学

尽管 LVGL 是用 C 语言编写的，但它在内核设计上严格遵循**面向对象编程 (OOP)** 的思想。

### 1. 一切皆对象
在 LVGL 的世界里，无论是简单的按钮（Button）、标签（Label），还是复杂的图表（Chart）、列表（List），本质上都是**对象 (`lv_obj_t`)**。
*   **基类 (`lv_obj`)**：这是所有部件的“祖先”。它定义了所有部件共有的属性，如坐标、大小、父子关系、样式和事件处理能力。
*   **派生类 (Widgets)**：特定的部件（如滑块 Slider）继承自 `lv_obj`，并在此基础上扩展了特有的功能（如滑动的逻辑、当前值的存储）。

### 2. 父子层级关系
对象之间存在严格的**树状层级关系**：
*   **父对象 (Parent)**：容器。移动父对象，其子对象会跟随移动；删除父对象，子对象也会被级联删除。
*   **子对象 (Children)**：附着在父对象上的元素。子对象的坐标通常是**相对**于父对象的。
*   **屏幕 (Screen)**：顶层父对象，没有父节点的特殊对象。

---

## 基础对象

`lv_obj` 是万物之源，掌握它的操作就等于掌握了 LVGL 开发的 80%。

### 大小
对象的大小决定了它在屏幕上占据的像素区域。LVGL 提供了灵活的 API 来设置宽度和高度。

#### 设置宽度：`lv_obj_set_width`
- **函数原型**：
    ```c
    void lv_obj_set_width(lv_obj_t * obj, lv_coord_t w);
    ```
- **功能描述**：设置对象的宽度。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `w`：宽度值。可以是具体的像素数值（如 100），也可以是特殊宏（如 `LV_PCT(50)`）。
- **返回值**：无。

#### 设置高度：`lv_obj_set_height`
- **函数原型**：
    ```c
    void lv_obj_set_height(lv_obj_t * obj, lv_coord_t h);
    ```
- **功能描述**：设置对象的高度。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `h`：高度值。
- **返回值**：无。

#### 同时设置宽高：`lv_obj_set_size`
- **函数原型**：
    ```c
    void lv_obj_set_size(lv_obj_t * obj, lv_coord_t w, lv_coord_t h);
    ```
- **功能描述**：一步到位同时设置对象的宽度和高度。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `w`：宽度值。
    - `h`：高度值。
- **返回值**：无。

#### 获取宽度：`lv_obj_get_width`
- **函数原型**：
    ```c
    lv_coord_t lv_obj_get_width(const lv_obj_t * obj);
    ```
- **功能描述**：获取对象经过布局计算后的**实际像素宽度**。该值包含了对象的内容区、内边距和边框宽度。
- **参数详解**：
    - `obj`：指向对象的指针。
- **返回值**：返回对象的实际宽度（像素）。
- **注意事项**：
    - **获取时机**：在对象刚刚创建且尚未进行屏幕刷新（Rendering）之前，LVGL 的布局系统可能还未计算出最终尺寸，此时调用该函数可能返回 **0** 或旧值。
    - **强制刷新**：若必须立即获取正确尺寸，请先调用 `lv_obj_update_layout(obj)`。

#### 获取高度：`lv_obj_get_height`
- **函数原型**：
    ```c
    lv_coord_t lv_obj_get_height(const lv_obj_t * obj);
    ```
- **功能描述**：获取对象经过布局计算后的**实际像素高度**。
- **参数详解**：
    - `obj`：指向对象的指针。
- **返回值**：返回对象的实际高度（像素）。

> [!TIP] 特殊尺寸值的妙用
> LVGL 的大小设置支持两个非常实用的宏：
> *   **`LV_PCT(x)`**：百分比布局。例如 `LV_PCT(50)` 表示占用父对象一半的尺寸。
> *   **`LV_SIZE_CONTENT`**：自适应内容。对象会自动伸缩，刚好包裹住其内部的所有子对象和文本（包含 Padding）。

*   **实战代码示例**：
    ```c
    // 创建一个基础对象
    lv_obj_t * obj = lv_obj_create(lv_scr_act());

    // 方式一：分别设置宽高为 200x200 像素
    lv_obj_set_width(obj, 200);
    lv_obj_set_height(obj, 200);

    // 方式二：同时设置，效果同上
    lv_obj_set_size(obj, 200, 200);

    // 方式三：宽度占满父容器（屏幕）的一半，高度自适应内容
    lv_obj_set_size(obj, LV_PCT(50), LV_SIZE_CONTENT);
    ```

### 位置与坐标系

LVGL 的坐标系与数学中的直角坐标系略有不同，它遵循 LCD 显示的标准：
*   **原点 (0, 0)**：位于父对象（或屏幕）的**左上角**。
*   **X 轴**：向**右**增加为正，向**左**为负。
*   **Y 轴**：向**下**增加为正，向**上**为负。
![](40%20-%20资源/44%20-%20硬件/电路设计/images/LVGL核心编程指南/file-20260128155151553.jpg)
#### 设置 X 坐标：`lv_obj_set_x`
- **函数原型**：
    ```c
    void lv_obj_set_x(
	    lv_obj_t * obj, 
	    lv_coord_t x
    );
    ```
- **功能描述**：设置对象相对于父对象左边框的水平偏移量。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `x`：X 轴坐标值（像素）。可以是正数（向右）或负数（向左）。
- **返回值**：无。

#### 设置 Y 坐标：`lv_obj_set_y`
- **函数原型**：
    ```c
    void lv_obj_set_y(lv_obj_t * obj, lv_coord_t y);
    ```
- **功能描述**：设置对象相对于父对象上边框的垂直偏移量。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `y`：Y 轴坐标值（像素）。可以是正数（向下）或负数（向上）。
- **返回值**：无。

#### 同时设置坐标：`lv_obj_set_pos`
- **函数原型**：
    ```c
    void lv_obj_set_pos(lv_obj_t * obj, lv_coord_t x, lv_coord_t y);
    ```
- **功能描述**：同时设置对象的 X 和 Y 坐标。
- **参数详解**：
    - `obj`：指向对象的指针。
    - `x`：X 轴坐标。
    - `y`：Y 轴坐标。
- **返回值**：无。

#### 获取坐标：`lv_obj_get_x` 
- **函数原型**：
    ```c
    lv_coord_t lv_obj_get_x(const lv_obj_t * obj);
    ```
- **功能描述**：获取对象相对于父对象的当前坐标值。
- **返回值**：当前的 X 坐标（像素）。
#### 获取坐标： `lv_obj_get_y`
- **函数原型**：
    ```c
    lv_coord_t lv_obj_get_y(const lv_obj_t * obj);
    ```
- **功能描述**：获取对象相对于父对象的当前坐标值。
- **返回值**：当前的 Y 坐标（像素）。

* **实战代码示例**：
    ```c
    // 创建一个对象
    lv_obj_t * obj = lv_obj_create(lv_scr_act());

    // 方式一：分别设置 X 和 Y
    lv_obj_set_x(obj, 200);   // 向右偏移 200px
    lv_obj_set_y(obj, -50);   // 向上偏移 50px (可能会超出父容器边界)

    // 方式二：同时设置
    lv_obj_set_pos(obj, 100, 100); 

    // 获取并打印坐标
    printf("x: %d, y: %d\n", lv_obj_get_x(obj), lv_obj_get_y(obj));
    ```

> [!WARNING] 超出边界的处理
> LVGL 的坐标允许设置为负数或远超父对象尺寸的值（如 `lv_obj_set_pos(obj, 1300, 600)`）。
> 默认情况下，父对象就像一个“窗口”，子对象超出窗口的部分会被**裁剪 (Clip)** 而不可见，或者导致父对象出现滚动条（取决于父对象的滚动设置），但对象本身依然存在于逻辑位置上。

### 对齐
为了适配不同尺寸的屏幕，**硬编码坐标**（如 `x=100`）往往不是最佳实践。LVGL 提供了强大的对齐功能，可以基于参照物进行相对定位。

#### 内部对齐：`lv_obj_align`
- **函数原型**：
    ```c
    void lv_obj_align(
	    lv_obj_t * obj,
	    lv_align_t align, 
	    lv_coord_t x_ofs, 
	    lv_coord_t y_ofs
    );
    ```
- **功能描述**：将对象相对于其**父对象**进行对齐。
- **参数详解**：
    - `obj`：要对齐的对象。
    - `align`：对齐基准点（如 `LV_ALIGN_CENTER`, `LV_ALIGN_TOP_LEFT` 等）。
    - `x_ofs`：在对齐基准上的水平偏移量。
    - `y_ofs`：在对齐基准上的垂直偏移量。
- **返回值**：无。

#### 外部对齐：`lv_obj_align_to`
- **函数原型**：
    ```c
    void lv_obj_align_to(
	    lv_obj_t * obj, 
	    const lv_obj_t * base, 
	    lv_align_t align, 
	    lv_coord_t x_ofs, 
	    lv_coord_t y_ofs
    );
    ```
- **功能描述**：将对象相对于**另一个任意对象**（通常是兄弟节点）进行对齐。
- **参数详解**：
    - `obj`：要移动的对象。
    - `base`：参照物对象（基准对象）。
    - `align`：对齐方式（如 `LV_ALIGN_OUT_BOTTOM_MID` 表示在参照物正下方）。
    - `x_ofs`：偏移量。
    - `y_ofs`：偏移量。
- **返回值**：无。
![](40%20-%20资源/44%20-%20硬件/电路设计/images/LVGL核心编程指南/file-20260128155654900.jpg)
#### 快捷居中：`lv_obj_center`
- **函数原型**：
    ```c
    void lv_obj_center(lv_obj_t * obj);
    ```
- **功能描述**：将对象放置在父对象的正中心。等同于 `lv_obj_align(obj, LV_ALIGN_CENTER, 0, 0)`。

*   **实战代码示例**：
    ```c
    // 1. 父子对齐：将 obj 放在屏幕中心，向右下各偏移 100
    lv_obj_align(obj, LV_ALIGN_CENTER, 100, 100);

    // 2. 兄弟对齐：创建 label 并放在 obj 的正下方
    lv_obj_t * label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "Hello, LVGL!");
    lv_obj_align_to(label, obj, LV_ALIGN_OUT_BOTTOM_MID, 0, 10); // 偏移 10px 间距
    ```

---

## 盒子模型 (Box Model)

LVGL 的布局系统深度借鉴了 CSS 的**盒子模型**。一个对象不仅仅是一个简单的矩形，它由以下几个同心层级组成（从内向外）：
![](40%20-%20资源/44%20-%20硬件/电路设计/images/LVGL核心编程指南/file-20260128160210242.jpg)

### 盒子模型分解
LVGL 的布局系统借鉴了 CSS 的盒子模型。一个对象不仅仅是一个简单的矩形，它由以下几个同心层级组成（从内向外）：
*   **Content (内容区)**：
    * **定义**：实际放置子对象、文本或图片的区域。
    * **大小计算**：`Content Width = Object Width - Padding Left - Padding Right`。
* **Padding (内边距)**：
    * **定义**：内容区与边界之间的填充空间。
    * **作用**：增加 Padding 会压缩内容区的可用空间，但不会改变对象整体大小（除非使用自适应大小）。
* **Border (边框)**：
    * **定义**：围绕在内边距之外的装饰性线条。
    * **关键点**：**边框占据宽度，且是在盒子内部绘制的**。如果边框宽度为 5px，那么它会遮挡 Padding 或 Content 的边缘 5px（如果没有足够的 Padding）。
* **Outline (轮廓)**：
    * **定义**：绘制在边框之外的线条。
    * **关键点**：**不占据空间**。轮廓是绘制在对象边界之外的，可能会覆盖周边的其他对象，通常用于焦点高亮。

`[此处插入图片：LVGL 盒子模型分解图 (Content/Padding/Border/Outline)]`

### 实战代码
通过调整边框和轮廓，我们可以直观地看到它们对布局的影响。

```c
void lv_box_model_test(void)
{
    // 创建一个基础对象，居中显示
    lv_obj_t * obj1 = lv_obj_create(lv_scr_act());
    lv_obj_align(obj1, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_size(obj1, 200, 150);

    // 1. 修改边框 (Border)
    // 边框是在对象内部绘制的，会占用内部空间
    lv_obj_set_style_border_width(obj1, 10, 0);        
    // 设置边框宽度为 10px
    lv_obj_set_style_border_color(obj1, lv_palette_main(LV_PALETTE_BLUE), 0);

    // 2. 修改轮廓 (Outline)
    // 轮廓是在对象外部绘制的，不占用对象空间，也不会影响布局
    lv_obj_set_style_outline_width(obj1, 10, 0);       
    // 设置轮廓宽度为 10px
    lv_obj_set_style_outline_color(obj1, lv_palette_main(LV_PALETTE_RED), 0);
    lv_obj_set_style_outline_pad(obj1, 5, 0);          
    // 轮廓与边框之间的间距

    // 3. 验证轮廓不占空间
    // 创建一个参考对象，紧贴 obj1 左侧排列
    lv_obj_t * obj_left = lv_obj_create(lv_scr_act());
    lv_obj_set_size(obj_left, 50, 50);
    // 注意观察：obj_left 会紧贴 obj1 的边框，而红色的轮廓会覆盖在 obj_left 上
    lv_obj_align_to(obj_left, obj1, LV_ALIGN_OUT_LEFT_MID, 0, 0); 
}
```

> [!NOTE] 布局陷阱：边框 vs 轮廓
> *   如果你希望给对象加一个“边框”且**不改变**它周围元素的排列位置，请使用 **Border**。
> *   如果你希望在对象被选中时加一个高亮圈，且**不希望**这个圈挤开周围的元素，请使用 **Outline**。

### 盒子模型的意义
* **空间计算**：当你设置 `width=100` 时，默认指的是整个盒子的宽度（包含 Border 和 Padding）。
* **文本换行**：如果你设置了 `pad_left=10` 和 `pad_right=10`，那么实际可用于显示文字的宽度只剩 `100 - 10 - 10 = 80`。这就是为什么有时候文字会自动换行，即使看起来宽度足够。

---

## 样式系统

样式决定了对象“长什么样”。LVGL 采用了类似 CSS 的设计，将样式属性与对象分离，实现了高度的复用性和灵活性。

### 普通样式 (Styles)
样式是一个独立的变量 (`lv_style_t`)，可以被多个对象共享。
*   **生命周期**：样式变量必须是 `static` 或全局的，不能是函数内的局部变量（除非动态分配），因为对象只是引用了样式指针，而非拷贝样式数据。

#### 初始化样式：`lv_style_init`
- **函数原型**：
    ```c
    void lv_style_init(lv_style_t * style);
    ```
- **功能描述**：初始化样式变量。在使用任何样式变量前必须先调用此函数。
- **参数详解**：
    - `style`：指向样式变量的指针。
- **返回值**：无。

#### 设置样式属性：`lv_style_set_...`
- **函数原型**：
    ```c
    void lv_style_set_bg_color(lv_style_t * style, lv_color_t value);
    void lv_style_set_bg_opa(lv_style_t * style, lv_opa_t value);
    // ... 数百种属性设置函数
    ```
- **功能描述**：设置样式的具体属性（如背景色、透明度、边框等）。
- **参数详解**：
    - `style`：指向样式变量的指针。
    - `value`：属性值。
- **返回值**：无。

#### 添加样式到对象：`lv_obj_add_style`
- **函数原型**：
    ```c
    void lv_obj_add_style(lv_obj_t * obj, lv_style_t * style, lv_style_selector_t selector);
    ```
- **功能描述**：将定义好的样式应用到对象上。
- **参数详解**：
    - `obj`：对象指针。
    - `style`：样式变量指针。
    - `selector`：生效的选择器（部分+状态），如 `LV_PART_MAIN | LV_STATE_PRESSED`。
- **返回值**：无。

### 本地样式 (Local Styles)
如果某个属性只针对特定对象，且不想定义额外的样式变量，可以直接使用本地样式 API。
*   **特点**：优先级高于普通样式，存储在对象内部，不共享。

#### 设置本地样式：`lv_obj_set_style_...`
- **函数原型**：
    ```c
    void lv_obj_set_style_bg_color(lv_obj_t * obj, lv_color_t value, lv_style_selector_t selector);
    // ... 对应所有普通样式的属性
    ```
- **功能描述**：直接设置对象的私有样式属性。
- **参数详解**：
    - `obj`：对象指针。
    - `value`：属性值。
    - `selector`：生效的选择器。
- **返回值**：无。

### 3. 状态 (States)与部分 (Parts)
样式不仅可以定义“长什么样”，还可以定义“在哪里”和“什么时候”生效。这通过 `selector` 参数实现，它是 **Part** 和 **State** 的按位或组合。

#### 状态 (States)
对象所处的交互状态。
*   `LV_STATE_DEFAULT`：默认状态。
*   `LV_STATE_PRESSED`：按下状态。
*   `LV_STATE_FOCUSED`：聚焦状态（被键盘或编码器选中）。
*   `LV_STATE_DISABLED`：禁用状态。

#### 部分 (Parts)
复杂部件由多个部分组成。以滑块 (`Slider`) 为例：
*   `LV_PART_MAIN`：背景槽（矩形背景）。
*   `LV_PART_INDICATOR`：填充条（指针部分）。
*   `LV_PART_KNOB`：旋钮（把手）。

#### 实战：自定义滑块样式
以下代码展示了如何利用 **Part** 和 **State** 彻底重构一个滑块的外观。

```c
void lv_slider_style_demo(void)
{
    // 定义样式变量 (必须 static)
    static lv_style_t style_main;      // 背景样式
    static lv_style_t style_indicator; // 指针样式
    static lv_style_t style_knob;      // 旋钮样式
    static lv_style_t style_pressed;   // 按下时的样式

    // 1. 背景部分 (LV_PART_MAIN)
    lv_style_init(&style_main);
    lv_style_set_bg_color(&style_main, lv_color_hex3(0xbbb)); // 灰色背景
    lv_style_set_radius(&style_main, LV_RADIUS_CIRCLE);       // 胶囊形状
    lv_style_set_pad_ver(&style_main, -2); // 负边距让背景比指标细一点

    // 2. 指针部分 (LV_PART_INDICATOR)
    lv_style_init(&style_indicator);
    lv_style_set_bg_color(&style_indicator, lv_palette_main(LV_PALETTE_CYAN)); // 青色填充
    lv_style_set_radius(&style_indicator, LV_RADIUS_CIRCLE);

    // 3. 旋钮部分 (LV_PART_KNOB)
    lv_style_init(&style_knob);
    lv_style_set_bg_color(&style_knob, lv_palette_main(LV_PALETTE_CYAN));
    lv_style_set_border_width(&style_knob, 2);
    lv_style_set_border_color(&style_knob, lv_palette_darken(LV_PALETTE_CYAN, 3)); // 深青色边框
    lv_style_set_pad_all(&style_knob, 6); // 增加内边距会让旋钮看起来更大（因为旋钮大小是基于 padding 计算的）

    // 4. 按下状态 (LV_STATE_PRESSED)
    lv_style_init(&style_pressed);
    lv_style_set_bg_color(&style_pressed, lv_palette_darken(LV_PALETTE_CYAN, 2)); // 按下变深

    // 创建滑块并应用样式
    lv_obj_t * slider = lv_slider_create(lv_scr_act());
    lv_obj_center(slider);

    // 清除默认样式（可选，为了纯净效果）
    lv_obj_remove_style_all(slider);

    // 应用样式到对应部分
    lv_obj_add_style(slider, &style_main, LV_PART_MAIN);
    lv_obj_add_style(slider, &style_indicator, LV_PART_INDICATOR);
    lv_obj_add_style(slider, &style_knob, LV_PART_KNOB);

    // 组合选择器：当 KNOB 被 PRESSED 时应用
    lv_obj_add_style(slider, &style_pressed, LV_PART_KNOB | LV_STATE_PRESSED);
}
```

> [!TIP] 样式继承与层叠
> *   **继承**：子对象默认不会继承父对象的样式（除了文本颜色等少数属性）。
> *   **层叠**：后添加的样式会覆盖先添加的样式；本地样式优先级最高。
> *   **过渡 (Transition)**：可以通过 `lv_style_transition_dsc_t` 定义样式切换时的动画效果（如颜色渐变）。

---

## 五、 事件驱动机制 (Events)

GUI 的核心在于交互。事件机制让对象能够响应用户的操作（点击、滑动、数值改变）。

### 1. 添加事件回调
GUI 的核心在于交互。事件机制让对象能够响应用户的操作（点击、滑动、数值改变）。

#### 注册回调：`lv_obj_add_event_cb`
- **函数原型**：
    ```c
    void lv_obj_add_event_cb(lv_obj_t * obj, lv_event_cb_t event_cb, lv_event_code_t filter, void * user_data);
    ```
- **功能描述**：为对象添加一个事件回调函数。
- **参数详解**：
    - `obj`：要添加事件的对象。
    - `event_cb`：回调函数指针。
    - `filter`：事件过滤类型（如 `LV_EVENT_CLICKED`）。若想接收所有事件，可使用 `LV_EVENT_ALL`。
    - `user_data`：传递给回调函数的用户数据指针，可在回调中通过 `lv_event_get_user_data(e)` 获取。
- **返回值**：无。

#### 实战：处理按键事件
以下代码演示了如何根据不同的按键事件改变对象颜色，并更新一个 Label 的文本。

```c
static void my_event_cb(lv_event_t * e)
{
    lv_obj_t * obj = lv_event_get_target(e);        // 获取触发事件的部件(对象)
    lv_event_code_t code = lv_event_get_code(e);    // 获取当前部件(对象)触发的事件代码
    lv_obj_t * label = lv_event_get_user_data(e);   // 获取添加事件时传递的用户数据(Label)

    switch(code){
        case LV_EVENT_PRESSED:
            lv_label_set_text(label, "LV_EVENT_PRESSED");
            // 按下变红
            lv_obj_set_style_bg_color(obj, lv_color_hex(0xc43e1c), 0);
            printf("LV_EVENT_PRESSED\n");
            break;
        case LV_EVENT_LONG_PRESSED:
            lv_label_set_text(label, "LV_EVENT_LONG_PRESSED");
            // 长按变绿
            lv_obj_set_style_bg_color(obj, lv_color_hex(0x4cbe37), 0);
            printf("LV_EVENT_LONG_PRESSED\n");
            break;
        default:
            break;
    }
}

void lv_event_demo(void)
{
    /* 创建基础部件(对象) */
    lv_obj_t * obj = lv_obj_create(lv_scr_act());
    lv_obj_center(obj);

    /* 创建label部件用于显示状态 */
    lv_obj_t * label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "test");
    lv_obj_align_to(label, obj, LV_ALIGN_OUT_TOP_MID, 0, -10);

    // 为obj添加事件回调，传入 label 作为 user_data
    // 使用 LV_EVENT_ALL 监听所有事件，然后在回调的 switch 中区分
    lv_obj_add_event_cb(obj, my_event_cb, LV_EVENT_ALL, label);
}
```

### 2. 事件冒泡 (Event Bubbling)
默认情况下，事件只由被操作的对象处理。但通过开启 **冒泡标志** (`LV_OBJ_FLAG_EVENT_BUBBLE`)，子对象的事件可以一层层传递给父对象，直到被处理。这在列表、复杂的容器交互中非常有用。

#### 核心 API
- **获取触发源**：`lv_event_get_target(e)` —— 实际被点击的（最里层）对象。
- **获取当前处理者**：`lv_event_get_current_target(e)` —— 当前正在执行回调的（父）对象。

#### 实战：四层套娃的冒泡传递
以下代码创建了4个层层嵌套的矩形，点击最内层的矩形，事件会一直冒泡传递给最外层的父对象处理。

```c
static void bubble_event_cb(lv_event_t * e)
{
    lv_obj_t * target = lv_event_get_target(e);            // 实际被点击的对象（可能是子对象）
    lv_obj_t * current = lv_event_get_current_target(e);   // 当前处理事件的对象（最外层父对象）
    lv_event_code_t code = lv_event_get_code(e);
    lv_obj_t * label = lv_event_get_user_data(e);

    switch(code){
        case LV_EVENT_PRESSED:
            lv_label_set_text(label, "LV_EVENT_PRESSED");
            // 将父对象和子对象都变红，直观看到冒泡路径
            lv_obj_set_style_bg_color(current, lv_color_hex(0xc43e1c), 0);
            lv_obj_set_style_bg_color(target, lv_color_hex(0xc43e1c), 0);
            break;
        case LV_EVENT_CLICKED: // 点击松开后触发
            lv_label_set_text(label, "LV_EVENT_CLICKED");
            // 移除颜色样式（恢复默认）
            lv_obj_remove_local_style_prop(current, LV_STYLE_BG_COLOR, 0);
            lv_obj_remove_local_style_prop(target, LV_STYLE_BG_COLOR, 0);
            break;
        default:
            break;
    }
}

void lv_event_bubble_demo(void)
{
    /* 1. 创建最外层父对象 obj1 */
    lv_obj_t * obj1 = lv_obj_create(lv_scr_act());
    lv_obj_set_size(obj1, 450, 250);
    lv_obj_center(obj1);

    /* 2. 创建子对象 obj2，开启冒泡 */
    lv_obj_t * obj2 = lv_obj_create(obj1);
    lv_obj_set_size(obj2, 400, 200);
    lv_obj_center(obj2);
    lv_obj_add_flag(obj2, LV_OBJ_FLAG_EVENT_BUBBLE); // 关键：开启冒泡

    /* 3. 创建孙对象 obj3，开启冒泡 */
    lv_obj_t * obj3 = lv_obj_create(obj2);
    lv_obj_set_size(obj3, 350, 150);
    lv_obj_center(obj3);
    lv_obj_add_flag(obj3, LV_OBJ_FLAG_EVENT_BUBBLE); // 关键：开启冒泡

    /* 4. 创建最内层对象 obj4，开启冒泡 */
    lv_obj_t * obj4 = lv_obj_create(obj3);
    lv_obj_set_size(obj4, 300, 100);
    lv_obj_center(obj4);
    lv_obj_add_flag(obj4, LV_OBJ_FLAG_EVENT_BUBBLE); // 关键：开启冒泡

    /* 5. 创建显示 Label */
    lv_obj_t * label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "Event Bubble Test");
    lv_obj_align_to(label, obj1, LV_ALIGN_OUT_TOP_MID, 0, -10);

    // 6. 只给最外层父对象 obj1 添加回调
    // 点击内部任何一个开启冒泡的子对象，都会触发这里的回调
    lv_obj_add_event_cb(obj1, bubble_event_cb, LV_EVENT_ALL, label);
}
```

### 3. 常用事件类型
*   **输入类**：`LV_EVENT_CLICKED` (点击)、`LV_EVENT_PRESSED` (按下)、`LV_EVENT_RELEASED` (释放)、`LV_EVENT_LONG_PRESSED` (长按)。
*   **数值类**：`LV_EVENT_VALUE_CHANGED` (滑块、开关值改变)。
*   **绘图类**：`LV_EVENT_DRAW_MAIN` (重绘时触发，用于自定义绘图)。

---

## 六、 总结

LVGL 的开发过程可以概括为：
1.  **创建对象**：基于 `lv_obj` 或其派生类（部件）。
2.  **布局排版**：利用 Size、Position、Align 和盒子模型确定位置。
3.  **美化外观**：使用 Styles 定义颜色、圆角、边框等视觉属性。
4.  **响应交互**：通过 Events 处理用户输入，实现业务逻辑。

掌握了这套核心机制，你就拥有了构建任何复杂 GUI 界面的钥匙。接下来，你可以深入研究具体的部件（如 Slider, Chart, Meter）和高级布局（Flex, Grid），它们都是这套基础逻辑的自然延伸。