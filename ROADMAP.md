# Kimi Work Bridge — ROADMAP

> 版本规划与演进路线。欢迎提交 Issue 和 PR 参与共建。

---

## 当前版本：v1.1.0（已提交 WorkBuddy 开放平台审核）

### 已有能力（14 个工具）

| 类别 | 工具 |
|---|---|
| 文件操作 | `list_workspace_files` `read_file` `write_file` |
| 数据分析 | `analyze_data`（summary/columns/correlation） |
| 报告生成 | `generate_excel_report` `generate_markdown_report` `generate_pdf_from_markdown` `create_html_dashboard` |
| 演示文稿 | `convert_data_to_pptx_outline` |
| 任务调度 | `create_task_instruction` `check_task_status` `deep_research_brief` |
| 内容交换 | `sync_clipboard` |
| 服务信息 | `get_bridge_info` |

---

## v1.2.0 — 计划 2026 Q4

### 🔧 高优先级（核心增强）

#### 1. 原生 PPT 生成
- **新工具**：`generate_pptx`
- 不再只输出 JSON 大纲，直接用 python-pptx 生成真正的 .pptx 文件
- 支持模板主题、母版、图表嵌入
- WorkBuddy 可一步拿到可直接演示的 PPT

#### 2. 图片生成与处理
- **新工具**：`generate_chart_image`
- 用 matplotlib 生成 PNG 图表（离线，不依赖 CDN）
- 解决 HTML 看板在无网络环境下图表不显示的问题
- 可直接嵌入 Word/PPT/PDF

#### 3. 双向实时通知
- **新工具**：`wait_for_task`（长轮询）
- WorkBuddy 无需反复调用 `check_task_status`，可阻塞等待 Kimi Work 完成任务
- 配合 Kimi Work Automation 实现真正的异步协作

#### 4. 数据清洗增强
- **增强**：`analyze_data` 新增 `clean` 模式
- 自动处理缺失值、重复行、异常值
- 输出清洗报告 + 清洗后的数据文件

### 🔧 中优先级（体验优化）

#### 5. 批量文件操作
- **新工具**：`batch_write_files` / `batch_read_files`
- 一次调用传输多个文件，减少 MCP 往返次数
- 适合 WorkBuddy 批量交付分析素材的场景

#### 6. 数据看板主题
- **增强**：`create_html_dashboard` 新增 `theme` 参数
- 预设主题：商务蓝 / 科技黑 / 清新绿 / 简约白
- 支持自定义 CSS 注入

#### 7. 文件预览缩略图
- **新工具**：`get_file_preview`
- 对 Excel/CSV 返回前 N 行预览（JSON 格式）
- WorkBuddy 可在调用完整分析前快速预览数据

#### 8. 多目录白名单管理
- **增强**：动态添加/移除允许目录
- 新工具：`add_allowed_path` / `remove_allowed_path`
- 运行时管理，无需重启 MCP Server

### 🔧 低优先级（远期规划）

#### 9. Expert 专家封装
- 基于现有 Connector 封装垂直场景 Expert：
  - 📊 财务分析助手
  - 📈 市场研究专家
  - 📝 报告撰写专家
  - 🔍 竞品分析专家

#### 10. HTTP 传输模式
- 支持 Streamable HTTP 传输，从 stdio 单用户扩展到局域网多用户
- 配合简单的 Web 界面管理桥接目录

#### 11. 文件版本历史
- 桥接目录中的文件自动保留版本快照
- 支持 `list_file_versions` / `restore_file_version`
- 防止 WorkBuddy 和 Kimi Work 互相覆盖对方的修改

#### 12. 使用统计与分析
- 新工具：`get_usage_stats`
- 记录每个工具的调用次数、耗时、成功率
- 帮助开发者优化 Skill 指南

---

## 贡献指南

### 如何提议新功能

1. 在此 ROADMAP 中查看是否已有规划
2. 如无，提交 Issue，描述：
   - 使用场景（什么情况下需要）
   - 预期行为（工具名、参数、返回值）
   - 优先级建议
3. 或直接提交 PR 实现

### 开发规范

- 新增工具必须同步更新 `SKILL.md` 和 `get_bridge_info` 的工具列表
- 必须添加对应的测试用例到 `test_bridge.py`
- 遵循现有代码风格（中文注释、类型标注、JSON 返回）
- 所有文件操作必须经过 `_resolve_path` 白名单校验

---

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.1.0 | 2026-09-10 | 新增 6 个工具（Markdown/PDF/HTML/PPT/研究/剪贴板），适配 mcp 2.x |
| v1.0.0 | 2026-09-10 | 初始版本：8 个基础工具 |
