# 摘要
*   **安装必备依赖**：更新系统并安装 Zsh、Git、Neovim 等核心工具。
*   **配置中文环境**：编辑 `/etc/locale.gen` 文件以启用 `en_US.UTF-8` 和 `zh_CN.UTF-8`，生成 locale，并设置 `LANG=zh_CN.UTF-8` 全局变量。
*   **安装 Oh My Zsh**：使用 curl 脚本自动安装 Oh My Zsh，并将其设置为默认 Shell。
*   **安装 Zsh 插件**：克隆 `zsh-autosuggestions` 和 `zsh-syntax-highlighting` 插件到 Oh My Zsh 的自定义插件目录。
*   **配置 .zshrc 文件**：配置 PATH 环境变量、Oh My Zsh 路径、加载 fzf 绑定、设置主题、启用自动更新、加载所需插件、设置语言和编辑器、配置 Zsh 行为和历史记录，以及定义自定义别名和函数。
*   **配置 Starship**：创建 `~/.config/starship.toml` 文件并替换为提供的配置内容，以自定义终端提示符的外观和行为。
*   **重启终端**：关闭并重新打开 Arch WSL 终端以使所有配置生效。
# 安装必备依赖
~~~sh
# 1. 更新系统
sudo pacman -Syu

# 2. 安装 Zsh 和所有依赖工具
sudo pacman -S zsh git neovim vim micro fastfetch fzf starship curl
~~~
# 配置中文环境
编辑`/etc/locale.gen`文件（需要sudo）
~~~sh
sudo nvim /etc/locale.gen
# 使用“/”找到以下两行去掉注释
#en_US.UTF-8 UTF-8 
#zh_CN.UTF-8 UTF-8

# :wq 退出nvim
~~~
> **提示**：保留 `en_US.UTF-8` 可以防止 tty 乱码。

生成locale
~~~sh
sudo locale-gen
~~~
设置全局变量Locale
~~~sh
echo "LANG=zh_CN.UTF-8" | sudo tee /etc/locale.conf
~~~
# 安装oh my zsh
使用curl安装
~~~sh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
~~~
>**注意**：会自动将 Zsh 设置为你的默认 Shell。提示是否切换，输入 `Y`

手动切换
将zsh添加白名单
~~~SH
echo $(which zsh) | sudo tee -a /etc/shells
~~~
设置默认 Shell
~~~SH
chsh -s $(which zsh)
~~~
# 安装zsh插件
`zsh-autosuggestions`自动补全
`zsh-syntax-highlighting`语法高亮
~~~sh
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
~~~
# 配置zsh配置文件（.zshrc）
打开~/.zshrc
~~~sh
nvim ~/.zshrc
~~~
将代码更换为以下内容
[zshrc](../49%20-%20代码片段/zshrc.md)
# 配置starship
创建文件`~/.config/starship.toml`。
```sh
mkdir -p ~/.config && touch ~/.config/starship.toml
```
替换为 [starship](../49%20-%20代码片段/starship.md)

> 提示 要安装书呆子字体才能正确显示
> 我选择的是Maple Mono NF CN
> 安装书呆子字体见后文

# 重启终端
关闭所有的 Arch WSL，重新打开一个新的
检查配置是否生效
