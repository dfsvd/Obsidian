# Fcitx 5 中文输入法

本指南基于 **Arch Linux** 系统，使用 **Fcitx 5** 作为输入法框架，并配置 **雾凇拼音 (Rime-Ice)** 输入方案。
## 一、安装所需软件包
首先，确保您的系统已添加 `archlinuxcn` 仓库（因为 `rime-ice-pinyin-git` 通常位于此仓库），然后安装以下软件包：
```Bash
sudo pacman -S fcitx5-im fcitx5-rime rime-ice-pinyin-git
```
- `fcitx5-im`：Fcitx 5 输入法框架的基本包。
- `fcitx5-rime`：Fcitx 5 专用的 Rime 输入法引擎。
- `rime-ice-pinyin-git`：雾凇拼音输入法方案文件。
## 二、启用雾凇拼音方案
通过创建或编辑 Rime 的默认自定义配置文件，来启用雾凇拼音的预设配置。
1. **创建配置目录：**
    ```sh
    mkdir -p ~/.local/share/fcitx5/rime
    ```
2. **编辑 `default.custom.yaml` 文件：**
    ```sh
    nvim ~/.local/share/fcitx5/rime/default.custom.yaml
    ```
3. **添加以下内容：**
    这将引入雾凇方案的默认预设 (`rime_ice_suggestion`)。
    ```yaml
    patch:
      # 这里的 rime_ice_suggestion 为雾凇方案的默认预设
      __include: rime_ice_suggestion:/
    ```
## 三、配置系统环境变量
配置环境变量以确保 Fcitx 5 能够被 GTK、Qt 等应用程序正确识别和加载。
 ```sh
 sudo nvim /etc/environment
 ```
 编辑系统全局环境变量
### 💻 Gnome 桌面环境
建议使用以下配置，其中 `XDG_CURRENT_DESKTOP=GNOME` 有助于解决某些应用中的“吞字”问题
```Plaintext
XIM="fcitx"
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
XDG_CURRENT_DESKTOP=GNOME
```
### 🖥️ KDE 桌面环境
对于 KDE，通常只需要设置 `XMODIFIERS`。
```Plaintext
XMODIFIERS=@im=fcitx
```
### 📌 提示
配置完成后，**请重启系统** 或重新登录您的用户会话，以使环境变量生效
## 四、关闭 Emoji 输入（可选）
如果您不希望在输入中文时出现 Emoji 候选项，可以针对您使用的具体雾凇拼音方案进行关闭。
### 1. 确定您的拼音方案文件
您使用的雾凇拼音方案决定了您需要修改的文件名：
- **全拼方案：** `rime_ice.custom.yaml`
- **小鹤双拼方案：** `double_pinyin_flypy.custom.yaml`
### 2. 执行关闭操作（以全拼为例）
这里以**全拼方案**（`rime_ice`）为例进行操作。如果您使用双拼，请将文件名替换为 `double_pinyin_flypy.custom.yaml`。
1. **打开或创建自定义配置文件：**
    ```sh
    nvim ~/.local/share/fcitx5/rime/rime_ice.custom.yaml
    ```
2. **添加以下内容：**
    在雾凇拼音方案中，Emoji 开关通常是 `switches` 列表中的**第四个**元素（索引为 `3`）。`reset: 0` 将其默认状态设置为关闭。
    ```YAML
    patch:
      # 关闭 Emoji
      "switches/@3/reset": 0
    ```
3. **保存并关闭文件。**
4. **重新部署 Rime：** 在 Fcitx 5 的配置界面中，找到 Rime 输入法，选择 **“重新部署”**，使更改生效或输入以下内容
```sh
fcitx5 -r
fcitx5 -d &
```