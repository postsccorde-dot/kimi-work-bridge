# WorkBuddy 开放平台提交审核清单

> 完成以下 checklist 后，即可在 [open.workbuddy.cn](https://open.workbuddy.cn) 提交连接器与技能包审核。

---

## 一、入驻前准备

- [ ] 已完成 open.workbuddy.cn 账号注册
- [ ] 已完成开发者资质认证（个人/企业）
- [ ] 已阅读《WorkBuddy 开发者服务协议》
- [ ] 已阅读《隐私保护指引》与《数据处理协议》

---

## 二、Connector 连接器材料

### 必需文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `connector-meta.json` | ☐ | 元信息：名称、版本、描述、作者、入口配置 |
| `mcp.json` | ☐ | MCP 启动配置：command / args / env |
| `icon.svg` | ☐ | 市场图标，建议 100×100，品牌色系 |

### 元信息核对清单

- [ ] `name` 字段：英文，无空格，唯一标识，如 `kimi-work-bridge`
- [ ] `version` 字段：遵循 SemVer，如 `1.0.0`
- [ ] `description` 字段：中文，≤ 100 字，清晰说明用途
- [ ] `type` 字段：确认为 `mcp`（或 `cli` 如果使用 CLI 方案）
- [ ] `categories` 字段：选择最贴切的分类，如 `productivity`、`data`、`automation`
- [ ] `entry` 或 `mcpServers` 配置：路径使用相对占位符或标准变量
- [ ] `permissions` 字段：如实声明需要的权限（`file:read`、`file:write`）
- [ ] `homepage` / `documentation` 字段：指向可访问的仓库或文档

---

## 三、Skill 技能包材料

### 必需文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `skills/{skill-name}/SKILL.md` | ☐ | AI 使用说明，指导 WorkBuddy Agent 如何调用 |

### SKILL.md 质量检查

- [ ] 文件顶部包含清晰的「概述」，说明技能解决什么问题
- [ ] 包含「何时调用」章节，明确触发条件
- [ ] 每个工具都有独立的使用说明和参数解释
- [ ] 包含具体的「示例对话」，展示完整交互流程
- [ ] 包含「最佳实践」或「注意事项」
- [ ] 语言风格简洁、指令化，适合 AI 直接阅读和理解
- [ ] 无敏感信息（API Key、内网地址、个人隐私）

---

## 四、功能测试清单

在提交审核前，必须在本地完成以下测试：

### 基础连通性

- [ ] `python kimi_work_bridge.py --test` 正常输出 ready 状态
- [ ] WorkBuddy MCP 面板添加配置后，服务正常启动（无报错）
- [ ] `get_bridge_info` 返回正确的服务器信息和工具列表

### 文件操作

- [ ] `list_workspace_files` 能正确列出桥接目录文件
- [ ] `write_file` 能成功写入文件到桥接目录
- [ ] `read_file` 能正确读取已写入的文件内容
- [ ] 尝试访问白名单外路径，正确返回 PermissionError

### 数据分析

- [ ] `analyze_data` 对 CSV 文件返回正确的 summary
- [ ] `analyze_data` 对 XLSX 文件返回正确的 summary
- [ ] `analyze_data` 的 `correlation` 模式对数值数据有效

### 任务调度

- [ ] `create_task_instruction` 成功创建任务 JSON 文件
- [ ] Kimi Work 侧 Automation 能在 5 分钟内检测到新任务
- [ ] `check_task_status` 能正确返回任务状态

### 报告生成

- [ ] `generate_excel_report` 能将 JSON 数据正确转为 .xlsx 文件
- [ ] 生成的 Excel 能用 Microsoft Excel / WPS / LibreOffice 正常打开

---

## 五、打包规范

```
kimi-work-connector-v1.0.zip
├── connector-meta.json
├── mcp.json
├── icon.svg
└── skills/
    └── kimi-work-bridge/
        └── SKILL.md
```

- [ ] ZIP 文件名包含版本号，如 `kimi-work-connector-v1.0.zip`
- [ ] 目录结构符合开放平台要求
- [ ] 无 `.git`、无 `__pycache__`、无测试残留文件
- [ ] 总大小 ≤ 5 MB（图标建议 ≤ 100 KB）

---

## 六、提交审核流程

1. 登录 [open.workbuddy.cn](https://open.workbuddy.cn)
2. 进入「开发者工作台」→「我的资产」→「新建资产」
3. 选择资产类型：**连接器**
4. 上传 ZIP 包，填写以下信息：
   - **名称**：Kimi Work 桥接连接器
   - **简介**：将 Kimi Work 的文件分析、自动化与报告生成能力接入 WorkBuddy
   - **分类**：效率工具 / 数据工具
   - **适用场景**：跨平台文件互通、数据分析、任务调度
5. 同步提交关联 Skill（如有）：在「我的资产」→「新建资产」→ 选择 **Skill**
6. 提交审核，等待反馈

---

## 七、审核后运营建议

- [ ] 准备一份 200 字以内的「快速上手指南」，供用户在技能市场查看
- [ ] 在 GitHub 仓库发布 Release，附上版本说明
- [ ] 在 WorkBuddy 社区或腾讯云开发者社区分享接入经验
- [ ] 收集用户反馈，规划 v1.1 功能（如更多文件格式支持、双向实时通信）

---

## 八、常见问题（审核侧）

**Q：个人开发者可以提交 Connector 吗？**  
A：可以。个人开发者通过身份证+手机号认证后，即可提交技能、专家、连接器。但涉及企业数据对接的复杂连接器，平台可能要求补充企业资质。

**Q：审核不通过通常是什么原因？**  
A：常见原因包括：
1. `connector-meta.json` 格式错误或缺少必填字段
2. `mcp.json` 配置无法启动（路径错误、依赖缺失）
3. `SKILL.md` 质量不足（缺少示例、说明模糊）
4. 功能测试未通过（权限越界、崩溃、超时）
5. 图标不符合规范（非 SVG、尺寸异常）

**Q：审核周期多久？**  
A：官方说明约 7 个工作日，实际通常为 3-5 个工作日。审核通过后会有站内信通知。

**Q：可以同时在 WorkBuddy 和 CodeBuddy 上架吗？**  
A：WorkBuddy 和 CodeBuddy 共享同一套开放平台和审核体系，一次上架即可在两个客户端中被搜索和安装。

---

> 完成以上所有 checklist 后，你就可以自信地点击「提交审核」了。祝上架顺利！
