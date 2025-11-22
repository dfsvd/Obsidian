// ==================================================
// 1. 获取当前文件夹的所有笔记
// ==================================================
let pages = dv.pages(`"${dv.current().file.folder}"`).array();

// ==================================================
// 2. 核心排序逻辑 (Order 霸权 + 自然排序)
// ==================================================
pages.sort((a, b) => {
    // 检测是否存在 order 属性 (排除 null 和 undefined)
    const aHasOrder = (a.order != null);
    const bHasOrder = (b.order != null);

    // 规则 1：有 order 的笔记，必须排在没有 order 的笔记前面
    if (aHasOrder && !bHasOrder) {
        return -1; // a 排前面
    }
    if (!aHasOrder && bHasOrder) {
        return 1;  // b 排前面
    }

    // 规则 2：如果两个都有 order，按 order 数字大小排
    if (aHasOrder && bHasOrder) {
        return a.order - b.order;
    }

    // 规则 3：如果两个都没有 order，按文件名自然排序 (1 -> 2 -> 14)
    return a.file.name.localeCompare(b.file.name, undefined, {
        numeric: true,
        sensitivity: 'base'
    });
});

// ==================================================
// 3. 定位当前笔记位置
// ==================================================
const current = pages.find(p => p.file.path === dv.current().file.path);
const index = pages.indexOf(current);

// 获取前后篇
const prev = pages[index - 1];
const next = pages[index + 1];

// 隐身逻辑：如果没有邻居，完全隐藏
if (!prev && !next) {
    return;
}

// ==================================================
// 4. 智能索引逻辑 (优先属性，其次自动)
// ==================================================
let indexLink = dv.current().index; 

if (!indexLink) {
    // 如果属性里没写，就自动生成
    const folderPath = dv.current().file.folder;
    const folderName = folderPath.split("/").pop(); 
    indexLink = `[[${folderName}]]`; 
}

// ==================================================
// 5. 构建 HTML 内容
// ==================================================
let content = `**🧭 导航**\n`;

if (prev) {
    content += `🔙 **上一篇**：${dv.fileLink(prev.file.path, false, prev.file.name)}\n`;
}

if (next) {
    content += `🔜 **下一篇**：${dv.fileLink(next.file.path, false, next.file.name)}\n`;
}

content += `***\n`;
content += `🏠 **返回索引**：${indexLink}`;

// ==================================================
// 6. 渲染输出
// ==================================================
dv.el("div", content, { 
    attr: { 
        style: "border: 1px solid var(--background-modifier-border); background-color: var(--background-secondary); border-radius: 5px; padding: 10px; font-size: 0.9em;" 
    }
});
