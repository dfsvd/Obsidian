---
created: <% tp.file.creation_date() %>
tags:
  - daily-note
  - journal
week: [[<% tp.date.now("gggg-[W]ww") %>]]
---

# 📅 <% tp.date.now("YYYY-MM-DD (dddd)") %>

> [!NOTE] 时间流
> ⬅️ **昨天**: [[<% tp.date.now("YYYY-MM-DD", -1) %>]] | 🗓️ **本周**: [[<% tp.date.now("gggg-[W]ww") %>]] | ➡️ **明天**: [[<% tp.date.now("YYYY-MM-DD", 1) %>]]

---

## 🚀 今日专注 (Focus)
> [!quote] 今日一句
> <% tp.web.daily_quote() %>

- **🎯 最重要的一件事 (The One Thing):** - [ ]

---

## 📥 任务控制台 (Task Dashboard)

### ⚡️ 收集箱 (Inbox - 随手记)
- [ ] 

### ⏰ 今日到期 / 逾期 (来自其他项目笔记)
*(这里会自动抓取你散落在 `20-项目` 或 `40-资源` 中，标记为今天做或已过期的任务)*
```tasks
not done
(due before tomorrow) OR (scheduled before tomorrow)
path does not include 10 - 每日记录
group by filename
hide backlink
```
