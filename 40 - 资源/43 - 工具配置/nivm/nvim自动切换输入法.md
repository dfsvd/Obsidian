在 Windows 下使用 Neovim 时，最痛苦的体验莫过于：在 **插入模式 (Insert Mode)** 使用小狼毫输入中文后，按下 `<Esc>` 回到 **普通模式 (Normal Mode)**，输入法依然停留在中文状态。此时按下 `j/k/h/l` 移动光标会直接触发输入法弹窗，导致操作中断，极度影响效率本文档通过使用 `im-select.ext` 加 `im-select.lua` 的组合解决这一问题

环境
- **OS**: Windows 10/11
- **输入法**: 小狼毫 (Weasel) + Rime 框架
- **编辑器**: Neovim (AstroNvim 框架)


## 原理
Neovim 自身无法直接控制 Windows 系统输入法。我们需要通过一个轻量级的命令行工具 `im-select.exe` 作为中介，监测并切换系统的输入法语言。
> [!note] **核心逻辑**：
>
> - 退出插入模式时：执行 `im-select.exe 1033`（切换到美式英语）。
>     
> - 进入插入模式时：自动恢复之前的输入法状态（例如切回中文）。
>     

## 准备工作

### 安装英文输入法
1. 进入 Windows **设置 -> 时间和语言 -> 语言和区域**
2. 点击 **添加语言**，搜索并安装 **英语（美国）**
3. 确保你的任务栏语言栏可以看到“中”和“ENG”两个选项

> [!tip]
> 如果 Windows 只安装了“中文”语言包，即便你在小狼毫内部按 `Shift` 切换到了英文，系统 ID 依然是 `2052`

### 部署 `im-select.exe`
1. 从 [GitHub](https://github.com/daipeihust/im-select) 下载 Windows 版本的二进制文件。
2. 将其存放在环境变量路径下，推荐路径：`C:\Windows\System32`（无需额外配置 `Path`）。
3. **校验 ID**：
    - 切到 ENG 运行 `im-select.exe` → 输出 `1033`
    - 切到小狼毫运行 `im-select.exe` → 输出 `2052`
---

### 插件配置
在 AstroNvim 中，在 `lua/plugins/` 目录下创建独立文件：`lua/plugins/im-select.lua`

```lua
-- 文件路径: lua/plugins/im-select.lua
return {
  -- 推荐使用 keaising 维护的版本，功能更全且稳定
  "keaising/im-select.nvim",
  -- 设置 InsertEnter 懒加载，不影响 Nvim 启动速度
  event = "InsertEnter",
  config = function()
    require("im_select").setup {
      -- 1. 设置退出插入模式时自动切换到的 ID（英文）
      default_im_select = "1033",
      
      -- 2. 自动记录并恢复状态：设为 true 
      -- 这样当你按 i 进入插入模式时，会自动回到你刚才的中文状态
      set_previous_im_select = true,
      
      -- 3. 在特定文件类型或 UI 界面中禁用切换功能
      disable_ft = { "help", "dashboard", "NvimTree", "neo-tree", "TelescopePrompt" },
    }
  end,
}
```

## 进阶技巧
### 解决切换“延迟感”

如果感觉 `Esc` 退出后有零点几秒的卡顿，这是因为 Windows 执行 `.exe` 的开销。
- **建议**：确保 `im-select.exe` 被加入杀毒软件（如 Windows Defender）的**白名单**中，避免每次调用都被扫描
#### 配合小狼毫的 `weasel.custom.yaml`
如果你希望在特定应用中默认行为更统一，可以在小狼毫配置中强制 nvim 启动时为英文：
```YAML
# weasel.custom.yaml
patch:
  app_options:
    nvim.exe:
      ascii_mode: true
    nvim-qt.exe:
      ascii_mode: true
```

---

## 验证与排查常见问题
1. **安装插件**：重启 Neovim，AstroNvim 会自动弹出 Lazy 界面并安装插件。
2. **测试流程**：
    - 按 `i` 进入插入模式。
    - 切换到中文，输入一段文字。
    - 按 `<Esc>` 返回普通模式。
    - **观察**：任务栏是否自动跳回了 `ENG`？按下 `j/k` 是否能立即移动光标？
3. **常见问题**：
    - **无效？**：检查 `im-select.exe` 是否在系统的 `Path` 中，可在 Nvim 内运行 `:!im-select.exe` 测试。
    - **延迟？**：确保你没有安装多个功能冲突的输入法切换插件。
    - **仓库报错？**：确保使用的是 `"keaising/im-select.nvim"` 而不是 `"daipeihust/im-select.nvim"`。