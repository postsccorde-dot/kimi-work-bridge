# WorkBuddy 开放平台 — 连接器提交表单填写参考

> 打开 open.workbuddy.cn → 开发者工作台 → 新建资产 → 连接器，对照以下字段直接复制粘贴。

---

## 基础信息

| 字段 | 填写内容 |
|---|---|
| **资产名称** | Kimi Work 桥接连接器 |
| **英文标识** | kimi-work-bridge |
| **资产类型** | 连接器（Connector） |
| **接入协议** | MCP |
| **一句话简介** | 将 Kimi Work 的数据分析、报告生成、深度研究与任务调度能力接入 WorkBuddy |
| **详细描述** | 本连接器为 WorkBuddy 与 Kimi Work（月之暗面 AI 工作台）搭建互通桥梁。安装后，WorkBuddy 可直接调用 Kimi Work 的 14 项能力：Excel/CSV 数据分析、Markdown/PDF 报告生成、HTML 数据看板、PPT 大纲输出、深度研究任务派发、异步任务调度、剪贴板内容交换等。所有数据在本地桥接目录交换，不上传云端，适合注重数据隐私的团队使用。 |
| **适用场景** | 数据分析与可视化、研究报告生成、跨平台文件协作、异步任务调度 |
| **目标用户** | 数据分析师、行业研究员、运营/市场人员、团队协作场景 |
| **分类** | 效率工具 / 数据工具 |

## 标签

```
kimi, 数据分析, 报告生成, 自动化, 看板, PDF, PPT, 任务调度
```

## 快速上手（提交表单中的「使用说明」字段）

```
1. 安装依赖：pip install fastmcp pandas openpyxl reportlab
2. 在 WorkBuddy 设置 → 连接器 → MCP 中添加配置
3. 指定 bridge-service/kimi_work_bridge.py 路径和桥接目录
4. 保存后刷新，即可在对话中调用

第一个任务示例：
"帮我分析 bridge-io/sales_q3.xlsx 并生成数据看板"
WorkBuddy 会自动调用 analyze_data 和 create_html_dashboard 完成分析。
```

## 权限声明

```
- file:read — 读取桥接目录中的文件
- file:write — 向桥接目录写入文件和报告
```

## 版本信息

| 字段 | 内容 |
|---|---|
| 当前版本 | 1.1.0 |
| 更新日志 | v1.1.0：新增 Markdown 报告、HTML 看板、PDF 转换、PPT 大纲、深度研究、剪贴板交换等 6 个工具 |
| 兼容版本 | WorkBuddy ≥ 2026.09 |

## 联系方式（提交表单中可能需要）

- 维护者：Your Name
- 邮箱：your.email@example.com
- 开源仓库：https://github.com/yourname/kimi-work-bridge
- 详细文档：仓库内 docs/ 目录

---

## Skill 资产提交（同时或单独提交）

在开放平台「新建资产」→ 选择 **Skill**，填写：

| 字段 | 内容 |
|---|---|
| 资产名称 | Kimi Work 桥接技能 |
| 英文标识 | kimi-work-bridge-skill |
| 一句话简介 | 指导 WorkBuddy Agent 高效调用 Kimi Work 桥接连接器的使用规范 |
| 详细描述 | 包含 14 个工具的完整使用说明、参数解释、最佳实践、以及数据分析→看板→PPT、深度研究→报告→PDF 两个完整工作流示例。适配桥接服务 v1.1.0+。 |
| 关联连接器 | kimi-work-bridge |

---

> 提交后约 3-7 个工作日审核，通过后会在 WorkBuddy 技能市场展示。
