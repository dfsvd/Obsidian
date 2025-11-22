# 安装

```sh
paru -S ghostty
```

# 配置

```c
# This is the configuration file for Ghostty.
# 以下是Ghostty的配置文件。

# --- 窗口/外观设置 (Window/Appearance Settings) ---

# 配置主题（颜色方案）。
theme = "Nocturnal Winter"

# 窗口装饰配置。设置为'none'以移除标题栏和边框，实现无边框外观。
window-decoration = none

# 设置窗口的初始宽度（以终端网格单元/字符列数为单位）。
window-width = 100

# 设置窗口的初始高度（以终端网格单元/字符行数为单位）。
window-height = 30

# 背景不透明度（1为完全不透明，0为完全透明）。
background-opacity = 0.98

# --- 背景图像设置 (Background Image Settings) ---

# 终端的背景图像路径。注意：此处使用了相对路径，它相对于配置文件的目录。
# 警告：分屏时图像会在每个分屏重复显示（Ghostty当前设计限制）。
background-image = ./themes/wa.png

# 背景图像的不透明度。值1.0为默认，小于1.0时图像会与背景颜色混合。
background-image-opacity = 0.8

# 背景图像的位置。'center'表示居中显示。
background-image-position = center

# 背景图像的缩放方式。'cover'表示保持宽高比，将图片缩放至完全覆盖终端，可能会裁剪边缘。
background-image-fit = cover

# --- 字体设置 (Font Settings) ---

# 终端使用的字体家族。
font-family = "Maple Mono NF CN"

# --- 鼠标设置 (Mouse Settings) ---

# 键入时立即隐藏鼠标光标，使用鼠标后再次可见。
mouse-hide-while-typing

# --- 键位绑定 (Keybindings) ---

# 以下绑定用于创建新的分屏。

# Ctrl + 上箭头：创建一个向上分割的新分屏。
keybind = ctrl+up=new_split:up

# Ctrl + 下箭头：创建一个向下分割的新分屏。
keybind = ctrl+down=new_split:down

# Ctrl + 左箭头：创建一个向左分割的新分屏。
keybind = ctrl+left=new_split:left

# Ctrl + 右箭头：创建一个向右分割的新分屏。
keybind = ctrl+right=new_split:right

# 以下绑定用于在分屏之间切换焦点。

# Ctrl + Shift + 上箭头：切换焦点到上方的分屏。
keybind = ctrl+shift+up=goto_split:up

# Ctrl + Shift + 下箭头：切换焦点到下方的分屏。
keybind = ctrl+shift+down=goto_split:down

# Ctrl + Shift + 左箭头：切换焦点到左方的分屏。
keybind = ctrl+shift+left=goto_split:left

# Ctrl + Shift + 右箭头：切换焦点到右方的分屏。
keybind = ctrl+shift+right=goto_split:right

# Alt + Q：关闭当前终端表面（例如分屏或标签页）。
keybind = alt+q=close_surface

# 示例：重新加载配置文件的快捷键（当前被注释掉）。
# keybind = ctrl+r=reload_config

```

