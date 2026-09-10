# Kimi Work 桥接连接器 — 快速上手指南

> 一句话介绍：让 WorkBuddy 直接调用 Kimi Work 的数据分析、报告生成、深度研究与任务调度能力。

## 这是什么？

Kimi Work 桥接连接器是 WorkBuddy 与 Kimi Work（月之暗面 AI 工作台）之间的互通桥梁。安装后，你可以在 WorkBuddy 中直接：

- 📊 **分析 Excel/CSV 数据** —— 无需打开文件，一键获取统计概览、列详情、相关性矩阵
- 📄 **生成 Markdown/PDF 报告** —— 将分析结论转为格式化的专业文档
- 📈 **创建 HTML 数据看板** —— 带图表的独立页面，浏览器直接打开
- 📑 **输出 PPT 大纲** —— 结构化内容，衔接 WorkBuddy 的 PPT 生成能力
- 🔍 **派发深度研究任务** —— 触发 Kimi Work 的联网搜索与长文本整合
- 📋 **异步任务调度** —— 非即时任务自动排队，完成后通知你
- 📋 **剪贴板内容交换** —— 快速传递小段文本、代码、链接

## 谁适合用？

| 角色 | 典型用法 |
|---|---|
| **数据分析师** | WorkBuddy 收集原始数据 → Kimi Work 清洗分析 → 生成看板/PPT |
| **行业研究员** | 派发深度研究任务给 Kimi Work，获取结构化研究报告 |
| **运营/市场** | 快速生成周报/月报的 Markdown/PDF，数据看板一键可视化 |
| **团队协作** | 通过共享桥接目录，WorkBuddy 与 Kimi Work 协同处理同一批文件 |

## 安装（30 秒）

1. 确保本地已安装 Python 3.10+，并安装依赖：
   ```bash
   pip install fastmcp pandas openpyxl reportlab
   ```

2. 在 WorkBuddy 设置 → 连接器 → MCP 中，点击「添加 MCP 服务」

3. 填入以下 JSON（将 `${workspace}` 替换为实际路径）：
   ```json
   {
     "mcpServers": {
       "kimi-work-bridge": {
         "command": "python",
         "args": ["/path/to/kimi_work_bridge.py"],
         "env": {
           "KIMI_WORK_BRIDGE_ALLOWED_PATHS": "/path/to/bridge-io"
         }
       }
     }
   }
   ```

4. 保存并刷新，即可在 WorkBuddy 对话中调用 Kimi Work 能力。

## 第一个任务

在 WorkBuddy 中输入：

> "帮我创建一个销售数据看板，数据在 bridge-io/sales_q3.xlsx"

WorkBuddy 会自动调用 `analyze_data` 分析数据，再调用 `create_html_dashboard` 生成带图表的 HTML 看板。

## 常见问题

**Q：需要同时安装 Kimi Work 吗？**  
A：不强制。如果不安装，桥接服务仍可作为独立的数据分析工具使用；安装 Kimi Work 后，可通过任务调度实现双向协作。

**Q：数据安全吗？**  
A：所有文件操作被限制在你指定的桥接目录内，无法访问系统其他路径。数据全程在本地，不上传云端。

**Q：支持哪些文件格式？**  
A：分析支持 .csv 和 .xlsx；报告输出支持 .md、.pdf、.html；PPT 素材输出为 .json 大纲。

---

> 技术支持：Your Email  
> 开源仓库：https://github.com/yourname/kimi-work-bridge  
> 详细文档：[README.md](https://github.com/yourname/kimi-work-bridge/blob/main/docs/README.md)
