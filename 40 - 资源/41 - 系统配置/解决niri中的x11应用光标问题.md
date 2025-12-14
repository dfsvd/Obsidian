# niri 配置文件统一主题
1. Nvim 打开 niri 配置文件
```sh
nvim ./.config/niri/config.kdl
```
2. 在 `environment` 块中添加以下内容
```sh
// qt主题统一为gtk3
QT_QPA_PLATFORMTHEME "gtk3"
```
3. 添加 gtk 3 配置文件
```
nvim ~/.config/gtk-3.0/settings.ini
```
在 `[Settings]` 块中添加以下内容
```txt
gtk-cursor-theme-name=Bibata-Modern-Ice
gtk-cursor-theme-size=32
```
- gtk-cursor-theme-name=Bibata-Modern-Ice 鼠标样式
- gtk-cursor-theme-size=32 鼠标大小