本文档为在 windows 下基与 **AstroNvim** 搭建一套简介高效的编辑器的全过程。
**核心环境：**
- **OS:** Windows 11
- **Terminal:** WezTerm
- **Toolchain:** MSYS2 (UCRT64)
- **Shell:** PowerShell
---
## 安装与基础
### 安装
在彻底清理旧配置后，通过 AstroNvim 模板初始化：

PowerShell

```
git clone --depth 1 https://github.com/AstroNvim/template $env:LOCALAPPDATA\nvim
# 启动后务必运行 :Lazy 等待插件安装完成
```

#### 2.2 解决 Windows 下的 LuaRocks 报错

在 Windows 上，`lazy.nvim` 尝试自动构建 `luarocks` 环境时常因路径或编译器问题导致红色 ERROR。

- **解决方案**：在 `lua/lazy_setup.lua` 的 `setup` 函数中完全禁用它（因为 99% 的插件不需要它）。
    

Lua

```
-- lua/lazy_setup.lua 
require("lazy").setup({
  -- ... 插件定义
}, {
  rocks = { enabled = false }, -- 彻底禁用，保持启动页清爽
  -- ... 其他配置
})
```

---

### 3. 第二阶段：编辑器核心行为定制

通过修改 `lua/plugins/astrocore.lua`，我们实现了与 VSCode 高度一致的编辑体验。

**核心配置项：**

- **缩进**：统一为 4 空格。
    
- **折行**：开启 `wrap`。
    
- **行号**：开启相对行号（高效跳转的关键）。
    
- **格式化**：开启 `autoformat_enabled`，实现保存即美化。
    

Lua

```
-- lua/plugins/astrocore.lua
options = {
  opt = {
    relativenumber = true, -- 开启相对行号
    number = true,         -- 显示当前行号
    tabstop = 4,           -- Tab 宽度 4
    shiftwidth = 4,        -- 缩进宽度 4
    expandtab = true,      -- Tab 转空格
    wrap = true,           -- 开启自动折行
    scrolloff = 8,         -- 光标上下保留 8 行，滚动更平滑
  },
  g = {
    autoformat_enabled = true, -- 保存时自动格式化
  }
}
```

---

### 4. 第三阶段：C/C++ 开发环境

这是配置中最核心的部分，解决了 `stdio.h` 找不到以及 LSP 无法跳转的问题。

#### 4.1 引入社区插件包

在 `lua/community.lua` 中（**务必删除第一行安全开关**），引入 C++ 和 CMake 支持：

Lua

```
-- lua/community.lua
return {
  "AstroNvim/astrocommunity",
  { import = "astrocommunity.pack.cpp" },   -- 引入 C++ 全家桶
  { import = "astrocommunity.pack.cmake" }, -- 引入 CMake 支持
}
```

#### 4.2 深度修复 Clangd（astrolsp.lua）

`clangd` 默认无法找到 MSYS2 的标准库。通过 `astrolsp.lua` 进行精准打击：

- **关键参数 1**：`--query-driver`。告诉 `clangd` 询问你的编译器（GCC/G++）来获取内置头文件路径。
    
- **关键参数 2**：`--function-arg-placeholders=true`。开启函数参数占位符提示（VSCode 风格）。
    
- **关键参数 3**：`offsetEncoding = "utf-16"`。解决 Windows 编码报错。
    

Lua

```
-- lua/plugins/astrolsp.lua
config = {
  clangd = {
    capabilities = { offsetEncoding = "utf-16" },
    cmd = {
      "clangd",
      -- 替换为你真实的编译器路径
      "--query-driver=C:/MyProgram/Development/msys64/ucrt64/bin/gcc.exe,C:/MyProgram/Development/msys64/ucrt64/bin/g++.exe",
      "--background-index",
      "--function-arg-placeholders=true", -- 必须带上 =true
      "--header-insertion=iwyu",
    },
  },
}
```

---

### 5. 第四阶段：细节优化与 UX 增强

#### 5.1 Inlay Hints (内联提示)

开启后，Neovim 会像现代 IDE 一样在代码中显示参数名和类型推导，极大提升代码可读性。

- **设置**：在 `astrolsp.lua` 的 `features` 中开启 `inlay_hints = true`。
    

#### 5.2 终端与字体

- **字体**：推荐使用 **Maple Mono NF CN**，在 WezTerm 中设置 `font_size = 20` 获得最佳清晰度。
    
- **项目标志**：在代码根目录下放置一个空文件 `.clangd`，确保 LSP 能精准识别项目根目录。
    

---

### 🏁 第一阶段成果展示

1. **LSP 全功能激活**：`gd` 跳转到定义、`K` 查看文档说明。
    
2. **错误实时反馈**：不再有 `stdio.h not found`，只有真实的语法错误提示。
    
3. **内联参数提示**：函数调用时自动显示参数标签。
    
4. **Mason 自动管理**：所有编译器后端（clangd, codelldb）由 Mason 自动下载管理。
    

---

### 💡 小结

AstroNvim 的强大在于它的模块化。通过 `AstroCore` 控制编辑器行为，`AstroLSP` 调教语言服务器，我们成功在 Windows 上驯服了 C/C++ 开发流程。

**下一阶段预告**：我们将探索 **DAP 调试配置**（使用 `codelldb` 断点调试）以及 **VSCode 风格的 TODO 彩色标签高亮**。