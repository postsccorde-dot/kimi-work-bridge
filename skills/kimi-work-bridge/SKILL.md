---
name: kimi-work-bridge-skill
version: 1.1.0
display_name: Kimi Work 桥接技能
display_name_en: Kimi Work Bridge Skill
description: 指导 WorkBuddy Agent 高效调用 Kimi Work 桥接连接器的完整使用规范
description_zh: 指导 WorkBuddy Agent 高效调用 Kimi Work 桥接连接器的完整使用规范。包含 14 个工具的详细说明、参数解释、最佳实践与完整工作流示例，帮助 Agent 准确判断何时、如何调用 Kimi Work 的数据分析、报告生成、深度研究与任务调度能力。
description_en: A comprehensive guide for WorkBuddy Agent to efficiently invoke the Kimi Work Bridge Connector. Includes detailed documentation for 14 tools, parameter explanations, best practices, and complete workflow examples to help the Agent accurately determine when and how to leverage Kimi Work's data analysis, report generation, deep research, and task scheduling capabilities.
author: Your Name
license: MIT
---

# Kimi Work 桥接技能 v1.1

## 概述

本 Skill 指导 WorkBuddy Agent 如何高效调用 **Kimi Work 桥接连接器**，实现与 Kimi Work 的深度互通。

Kimi Work 是月之暗面推出的 AI 原生工作台，擅长：
- 长文本分析与多源信息整合
- 文件级数据分析（Excel、CSV）
- Blueprint 自动化（定时任务、工作流）
- Widget 可视化看板生成
- 专业文档生成（PPT、Word、PDF、Markdown）

通过本连接器，WorkBuddy 可以将自身不擅长的"深度分析""长文本研究""复杂报告排版"委托给 Kimi Work，并将结果拉回 WorkBuddy 完成最终交付（如生成 PPT、海报、推送）。

## 何时调用 Kimi Work 桥接

当用户任务涉及以下场景时，应优先调用 `kimi-work-bridge` 连接器：

| 场景 | 推荐工具 | 说明 |
|---|---|---|
| 分析本地数据文件（CSV、Excel） | `analyze_data` | 即时统计分析，无需打开文件 |
| 生成 Excel 报告 | `generate_excel_report` | 结构化数据 → 专业表格 |
| 生成长文 Markdown 报告 | `generate_markdown_report` | 多章节结构化文档 |
| 生成数据看板 | `create_html_dashboard` | 含图表的独立 HTML 页面 |
| Markdown 转 PDF | `generate_pdf_from_markdown` | 正式文档交付 |
| 数据转 PPT 大纲 | `convert_data_to_pptx_outline` | 为 WorkBuddy PPT 生成准备素材 |
| 派发深度研究任务 | `deep_research_brief` | 触发 Kimi Work 联网搜索 + 长文本分析 |
| 异步任务调度 | `create_task_instruction` + `check_task_status` | 非即时返回的长任务 |
| 快速内容交换 | `sync_clipboard` | 剪贴板级文本互通 |
| 文件读写 | `write_file` / `read_file` | 通用文件交换 |

---

## 工具使用规范

### 1. 文件交换（write_file / read_file）

WorkBuddy 与 Kimi Work 通过共享的桥接目录交换文件。默认路径：`${workspace}/bridge-io/`

**场景：WorkBuddy 收集数据 → Kimi Work 分析**
```
步骤1：WorkBuddy 用 write_file 将原始数据写入 bridge-io/raw_data.json
步骤2：告知用户"已将数据发送给 Kimi Work 进行分析"
步骤3：Kimi Work 侧读取该文件并执行分析
步骤4：Kimi Work 将结果写回 bridge-io/analysis_result.md
步骤5：WorkBuddy 用 read_file 读取结果并展示给用户
```

### 2. 数据分析（analyze_data）

直接对桥接目录中的 CSV/Excel 进行统计分析，无需手动打开文件。

**推荐参数组合**：
- 首次分析：`analysis_type="summary"` —— 获取数据概览（行数、均值、分布）
- 深入了解：`analysis_type="columns"` —— 查看每列的数据类型和空值情况
- 数值探索：`analysis_type="correlation"` —— 获取数值列的相关性矩阵

### 3. Markdown 报告生成（generate_markdown_report）

将结构化结论生成为格式化的 Markdown 长文报告。

**sections_json 格式**：
```json
[
  {"heading": "市场概况", "content": "本季度销售额同比增长 23%...", "level": 2},
  {"heading": "区域表现", "content": "华东区领跑，华南区增速最快...", "level": 2}
]
```

**典型场景**：WorkBuddy 完成数据探索 → 调用 `generate_markdown_report` 生成报告 → 用户可直接在 Kimi Work 中继续编辑完善。

### 4. HTML 数据看板（create_html_dashboard）

将 JSON 数据生成为可独立打开的 HTML 看板，含 Chart.js 图表。

**参数说明**：
- `chart_type="bar"`：柱状图，适合对比数据
- `chart_type="line"`：折线图，适合趋势数据
- `chart_type="table"`：仅表格，适合无数值列的数据

**使用提示**：生成的 HTML 可直接用浏览器打开，也可由 WorkBuddy 截图后嵌入 PPT。

### 5. PDF 转换（generate_pdf_from_markdown）

将已生成的 Markdown 报告转为 PDF，用于正式交付。

**标准流程**：
```
generate_markdown_report(...) → 生成 .md
generate_pdf_from_markdown(md_file_path="...", output_path="...") → 生成 .pdf
```

### 6. PPT 大纲生成（convert_data_to_pptx_outline）

将内容结构化为 PPT 大纲 JSON，WorkBuddy 可读取后调用自身 PPT 能力完成制作。

**data_json 格式**：
```json
[
  {"slide_title": "市场概览", "bullet_points": ["Q3 销售额 1.2 亿", "同比增长 23%"], "speaker_notes": "强调增长驱动因素"},
  {"slide_title": "竞争格局", "bullet_points": ["Top3 品牌市占率 65%", "新进入者 3 家"], "speaker_notes": ""}
]
```

### 7. 深度研究任务（deep_research_brief）

专门用于触发 Kimi Work 的**联网搜索 + 长文本整合**能力。与普通任务不同，它会自动生成详细的研究指令模板。

**使用场景**：
- "帮我调研一下最近三个月大模型领域的融资动态"
- "对比分析 Kimi、DeepSeek、GLM 的技术架构差异"

**与 `create_task_instruction` 的区别**：
- `deep_research_brief`：专用于研究类任务，自动包含搜索、整合、结构化输出的指令模板
- `create_task_instruction`：通用任务调度，需自行编写完整指令

### 8. 剪贴板交换（sync_clipboard）

轻量级的文本内容交换，适合快速传递小段内容（如一段代码、一个链接、一个公式）。

**使用方式**：
- WorkBuddy `sync_clipboard(action="write", content="...")`
- Kimi Work 侧读取 `bridge-io/shared_clipboard.txt`

### 9. 任务调度（create_task_instruction / check_task_status）

用于 Kimi Work 无法即时返回的**长任务**（如批量数据处理、复杂报告生成）。

**标准流程**：
```
1. create_task_instruction(
     task_name="ai_weekly_report_20260910",
     instructions="请搜索本周 AI 行业重大新闻...",
     priority="high"
   )
→ 返回任务文件路径

2. 告知用户："任务已发送给 Kimi Work，预计 3-5 分钟完成。"

3. 稍后调用 check_task_status(task_name="ai_weekly_report_20260910")
→ 若 status == "done"，读取结果文件并展示
→ 若 status == "pending"，告知用户仍在处理中
```

### 10. Excel 报告生成（generate_excel_report）

WorkBuddy 可将结构化数据（如 JSON 数组）交给 Kimi Work 生成格式化的 Excel 文件。

**data_json 格式要求**：
```json
[
  {"姓名": "张三", "销售额": 150000, "月份": "2026-08"},
  {"姓名": "李四", "销售额": 230000, "月份": "2026-08"}
]
```

---

## 最佳实践

1. **路径安全**：所有文件操作必须在白名单目录内（默认 `bridge-io/`），不要尝试访问系统敏感路径。
2. **任务命名**：使用英文+下划线命名任务，包含日期便于追踪，如 `market_research_20260910`。
3. **错误处理**：如果桥接服务返回 `error`，首先检查：
   - 文件路径是否在允许目录内
   - pandas/openpyxl/reportlab 是否已安装
   - JSON 格式是否合法
4. **性能注意**：
   - `analyze_data` 目前支持最大 5MB 的文件
   - `generate_pdf_from_markdown` 对超大 Markdown 可能分页不佳，建议控制单文件在 50 页以内
5. **协同提示**：向用户说明"正在调用 Kimi Work 的 XX 能力"，增强透明度和信任感。
6. **版本兼容**：本 Skill 适配桥接服务 v1.1.0+，旧版可能缺少 `create_html_dashboard`、`deep_research_brief` 等工具。

---

## 完整工作流示例

### 示例 1：数据分析 → 看板 → PPT

**用户**：分析 Q3 销售数据，做成看板并准备 PPT 素材。

**WorkBuddy**：
> 我来调用 Kimi Work 的数据分析与可视化能力帮您处理。

1. `analyze_data(file_path="sales_q3.xlsx", analysis_type="summary")` → 获取数据概览
2. `analyze_data(file_path="sales_q3.xlsx", analysis_type="correlation")` → 获取相关性分析
3. `create_html_dashboard(title="Q3 销售数据看板", data_json="...", output_path="dashboard_q3.html", chart_type="bar")` → 生成可视化看板
4. `convert_data_to_pptx_outline(data_json="...", output_path="ppt_outline_q3.json", title="Q3 销售复盘")` → 生成 PPT 大纲

→ 告知用户："分析完成。HTML 看板已生成，可直接浏览器打开；PPT 大纲已准备好，您可以直接调用 WorkBuddy 的 PPT 生成能力完成制作。"

### 示例 2：深度研究 → 报告 → PDF

**用户**：帮我调研一下 AIGC 在教育行业的最新应用案例，整理成报告。

**WorkBuddy**：
> 这是一个需要深度研究的任务，我将委托 Kimi Work 完成。

1. `deep_research_brief(topic="AIGC 在教育行业的应用案例", scope="2026 年以来的最新实践、落地产品、效果评估", output_path="research_aigc_edu.md", max_sources=8)` → 创建研究任务
2. 告知用户："研究任务已发送给 Kimi Work，预计 5-10 分钟完成。Kimi Work 将搜索至少 8 个权威来源并整合成结构化报告。"
3. （用户稍后询问时）`check_task_status(task_name="AIGC_在教育行业的应用案例")` → 确认完成
4. `generate_pdf_from_markdown(md_file_path="research_aigc_edu.md", output_path="AIGC教育应用报告.pdf")` → 转为 PDF 交付

---

**维护者**：Your Name  
**版本**：1.1.0  
**适配桥接服务版本**：≥ 1.1.0  
**适配 WorkBuddy 版本**：≥ 2026.09
