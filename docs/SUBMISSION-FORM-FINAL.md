# 【复制即用】WorkBuddy 开放平台提交表单

> 打开 https://open.workbuddy.cn → 登录 → 开发者工作台 → 新建资产

---

## 🔴 先替换以下占位符（全文搜索替换）

| 占位符 | 替换为你的真实信息 |
|---|---|
| `YOUR_NAME` | 你的名字/昵称 |
| `YOUR_EMAIL` | 你的邮箱 |
| `YOUR_GITHUB` | 你的 GitHub 用户名（没有可填任意） |
| `YOUR_PHONE` | 你的手机号（平台认证用，不会公开） |

---

## 第一步：提交连接器（Connector）

路径：开发者工作台 → 新建资产 → **连接器**

### 基础信息页

```
【资产名称】
Kimi Work 桥接连接器

【英文标识】
kimi-work-bridge

【接入协议】
MCP

【一句话简介】
将 Kimi Work 的数据分析、报告生成、深度研究与任务调度能力接入 WorkBuddy

【详细描述】
本连接器为 WorkBuddy 与 Kimi Work（月之暗面 AI 工作台）搭建互通桥梁。安装后，WorkBuddy 可直接调用 Kimi Work 的 14 项能力：

• Excel/CSV 数据分析（统计概览、列详情、相关性矩阵）
• Markdown 报告生成（多章节结构化长文）
• HTML 数据看板（含 Chart.js 图表，浏览器直接打开）
• PDF 转换（Markdown → PDF，含中文字体适配）
• PPT 大纲输出（结构化数据 → PPT 素材 JSON）
• 深度研究任务派发（触发 Kimi Work 联网搜索与整合）
• 异步任务调度（非即时长任务自动排队执行）
• 剪贴板内容交换（轻量级文本互通）

所有数据在本地桥接目录交换，不上传云端，适合注重数据隐私的个人和团队。

【适用场景】
数据分析与可视化、研究报告生成、跨平台文件协作、异步任务调度

【目标用户】
数据分析师、行业研究员、运营/市场人员、需要跨工具协作的团队

【分类】
效率工具 / 数据工具

【标签】
kimi, 数据分析, 报告生成, 自动化, 看板, PDF, PPT, 任务调度
```

### 文件上传页

```
【上传文件】
选择文件：kimi-work-connector-v1.1.zip
（文件在工作空间根目录，25KB）

【包含文件】
- connector-meta.json（元信息）
- mcp.json（MCP 启动配置）
- icon.svg（市场图标）
- skills/kimi-work-bridge/SKILL.md（AI 使用说明）
```

### 使用说明页

```
【快速上手】
1. 安装依赖：pip install fastmcp pandas openpyxl reportlab
2. 在 WorkBuddy 设置 → 连接器 → MCP 中点击「添加 MCP 服务」
3. 填入 JSON 配置：
   {
     "mcpServers": {
       "kimi-work-bridge": {
         "command": "python",
         "args": ["实际路径/bridge-service/kimi_work_bridge.py"],
         "env": {
           "KIMI_WORK_BRIDGE_ALLOWED_PATHS": "实际路径/bridge-io"
         }
       }
     }
   }
4. 保存并刷新，即可在对话中调用

【第一个任务示例】
在 WorkBuddy 中输入：
"帮我分析 bridge-io/sales_q3.xlsx 并生成数据看板"

WorkBuddy 会自动调用 analyze_data 分析数据，再调用 create_html_dashboard 生成带图表的 HTML 看板。

【权限说明】
- file:read — 读取桥接目录中的文件
- file:write — 向桥接目录写入文件和报告
数据全程本地处理，不涉及云端上传。
```

### 版本信息页

```
【当前版本】
1.1.0

【更新日志】
v1.1.0（2026-09-10）：
- 新增 Markdown 报告生成
- 新增 HTML 数据看板（含 Chart.js 图表）
- 新增 Markdown → PDF 转换
- 新增 PPT 大纲输出
- 新增深度研究任务派发
- 新增剪贴板内容交换

v1.0.0（2026-09-10）：
- 基础文件交换
- Excel/CSV 数据分析
- Excel 报告生成
- 异步任务调度

【兼容版本】
WorkBuddy ≥ 2026.09
```

### 联系方式页

```
【维护者】
YOUR_NAME

【邮箱】
YOUR_EMAIL

【开源仓库】
https://github.com/YOUR_GITHUB/kimi-work-bridge

【详细文档】
https://github.com/YOUR_GITHUB/kimi-work-bridge/blob/main/docs/README.md
```

---

## 第二步：提交 Skill（可选但推荐，提升调用体验）

路径：开发者工作台 → 新建资产 → **Skill**

### 基础信息页

```
【资产名称】
Kimi Work 桥接技能

【英文标识】
kimi-work-bridge-skill

【一句话简介】
指导 WorkBuddy Agent 高效调用 Kimi Work 桥接连接器的完整使用规范

【详细描述】
包含 14 个工具的完整使用说明、参数解释、最佳实践，以及两个完整工作流示例：

1. 数据分析 → 看板 → PPT：从 Excel 分析到 HTML 可视化再到 PPT 大纲的全链路
2. 深度研究 → 报告 → PDF：从研究任务派发到 Markdown 报告再到 PDF 交付

适配桥接服务 v1.1.0+，帮助 WorkBuddy Agent 准确判断何时、如何调用 Kimi Work 能力。

【关联连接器】
kimi-work-bridge

【分类】
效率工具

【标签】
kimi, 技能指南, 连接器, 数据分析, 报告生成
```

### 文件上传页

```
【上传文件】
从连接器 ZIP 包中解压出：
skills/kimi-work-bridge/SKILL.md

单独上传此文件即可。
```

---

## 第三步：等待审核

- 提交后状态变为「审核中」
- 审核周期：3-7 个工作日
- 审核通过后，站内信 + 邮件通知
- 通过后，WorkBuddy 用户可在技能市场搜索「Kimi Work」找到并安装

---

## 常见问题（审核阶段）

**Q：审核不通过怎么办？**
A：常见原因和修复方式：
1. 文件路径问题 → 检查 mcp.json 中路径是否使用了标准占位符
2. 缺少依赖说明 → 确保使用说明中明确列出了 pip install 命令
3. 描述不清晰 → 直接复制本文档中的「详细描述」即可

**Q：可以先只提交连接器，后补 Skill 吗？**
A：可以。连接器是核心，Skill 是增强。先提交连接器通过审核后再补 Skill 完全没问题。

**Q：个人开发者能过吗？**
A：可以。个人认证（身份证+手机号）即可提交连接器和 Skill，不涉及企业数据对接的都不需要企业资质。

---

> 祝你提交顺利！有问题随时来问。
