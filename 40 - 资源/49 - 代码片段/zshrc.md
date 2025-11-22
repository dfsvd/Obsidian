~~~sh
#-----------------------------------------------------------------------
# 路径配置
#-----------------------------------------------------------------------

# 设置 PATH 环境变量
export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# [TODO] 你可以稍后在这里添加 arm-linux-gcc 的路径
# export PATH=$PATH:/usr/local/arm/5.4.0/usr/bin


#-----------------------------------------------------------------------
# Oh My Zsh 配置
#-----------------------------------------------------------------------

# Oh My Zsh 安装路径
export ZSH="$HOME/.oh-my-zsh"

# 加载 pacman 安装的 fzf 键位绑定和补全 
source /usr/share/fzf/key-bindings.zsh 
source /usr/share/fzf/completion.zsh

# 设置主题 (agnoster 需 Powerline 字体)
ZSH_THEME=""

# 自动更新 oh-my-zsh（每 7 天）
zstyle ':omz:update' mode auto
zstyle ':omz:update' frequency 7

# 加载插件（git、补全、高亮、跳转、模糊搜索）
plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
  z
)

# 加载 Oh My Zsh
source $ZSH/oh-my-zsh.sh


#-----------------------------------------------------------------------
# 环境与编辑器
#-----------------------------------------------------------------------

# 设置语言
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 设置编辑器（本地用 nvim，远程用 vim）
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='vim'
else
  export EDITOR='nvim'
fi

# 编译标志
export ARCHFLAGS="-arch $(uname -m)"


#-----------------------------------------------------------------------
# Zsh 行为与历史记录
#-----------------------------------------------------------------------

# 大小写不敏感补全
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# 历史记录大小
HISTSIZE=10000
SAVEHIST=10000

# 历史记录时间格式
HIST_STAMPS="yyyy-mm-dd"

# 自动补全建议颜色
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#999999"

# 共享历史记录选项
setopt APPEND_HISTORY      # 立即将历史记录追加到历史文件
setopt INC_APPEND_HISTORY  # 增量追加，并读取新条目
setopt SHARE_HISTORY       # 在所有 shell 间共享


#-----------------------------------------------------------------------
# 工具与别名
#-----------------------------------------------------------------------

# 自定义别名
alias nano="micro"            # micro
alias ll="ls -lah"            # 详细列表
alias update="sudo pacman -Syu"  # 更新系统
alias gs="git status"         # git 状态
alias wecome='clear && fastfetch' 

# 自定义函数：创建目录并进入
function mkcd() {
  mkdir -p "$1" && cd "$1"
}

# 初始化 Starship 提示符
eval "$(starship init zsh)"
~~~