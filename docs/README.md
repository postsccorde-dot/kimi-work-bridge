# Kimi Work × WorkBuddy 开放平台互通方案

> 版本：v1.0  
> 目标：通过 WorkBuddy 开放平台（open.workbuddy.cn），将 Kimi Work 的能力封装为 WorkBuddy 生态组件，实现产品级互通。  
> 适配：WorkBuddy 连接器（MCP / CLI 双协议）+ Skill 技能包

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WorkBuddy 桌面端                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐  │
│  │   用户输入   │───→│  Agent调度  │───→│        Connector 面板            │  │
│  └─────────────┘    └─────────────┘    └─────────────────────────────────┘  │
│                                                   │                         │
│                    ┌──────────────────────────────┘                         │
│                    ▼  MCP 协议 (stdio / HTTP)                               │
│         ┌──────────────────────┐                                            │
│         │  Kimi Work MCP Bridge │ ←── 本方案核心桥接服务                     │
│         │    (Python 服务)      │                                            │
│         └──────────────────────┘                                            │
│                    │                                                        │
│         ┌─────────┴──────────┐                                             │
│         ▼                    ▼                                             │
│  ┌─────────────┐      ┌─────────────────────────────┐                     │
│  │  共享文件目录 │      │      Kimi Work 运行时        │                     │
│  │  (bridge-io) │      │  ┌─────┐ ┌─────┐ ┌──────┐  │                     │
│  └─────────────┘      │  │文件操作│ │Automation│ │Widget │  │                     │
│                       │  └─────┘ └─────┘ └──────┘  │                     │
│                       └─────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**互通逻辑**：
1. WorkBuddy 用户通过自然语言发起任务
2. WorkBuddy Agent 识别需要调用 Kimi Work 能力，通过 MCP Connector 调用桥接服务
3. 桥接服务将请求转换为 Kimi Work 可执行的格式（文件指令 / Python 脚本）
4. Kimi Work 执行后，结果通过共享目录或返回给桥接服务
5. 桥接服务将结果格式化后返回给 WorkBuddy，由 WorkBuddy 完成最终交付（PPT、海报、推送等）

---

## 二、核心互通能力映射

| Kimi Work 能力 | WorkBuddy 调用方式 | 输出形态 | 典型场景 |
|---|---|---|---|
| **文件读写与数据分析** | MCP Tool: `analyze_data` | Excel / CSV / 图表 | WorkBuddy 收集原始数据 → Kimi Work 清洗分析 → 返回结构化结果 |
| **Blueprint 自动化** | MCP Tool: `trigger_automation` | 执行状态 / 产物文件 | WorkBuddy 触发 Kimi Work 的定时任务（如日报生成） |
| **Widget 可视化** | MCP Tool: `create_dashboard` | HTML 看板文件 | Kimi Work 生成数据看板 → WorkBuddy 嵌入展示或截图分享 |
| **Web 深度调研** | MCP Tool: `deep_research` | Markdown 报告 | WorkBuddy 需要行业研究 → Kimi Work 多源检索并撰写长文 |
| **插件生态（PDF/PPT/Word）** | MCP Tool: `generate_document` | .pdf / .pptx / .docx | WorkBuddy 调用 Kimi Work 的专业文档生成能力 |
| **多 Agent 协作** | MCP Tool: `swarm_task` | 汇总结果 | 复杂任务分解给 Kimi Work 的 explore/plan/coder 子 Agent |

---

## 三、项目结构

```
workbuddy-bridge/
├── connector/                      # WorkBuddy 连接器包
│   ├── connector-meta.json         # 连接器元信息（必填）
│   ├── mcp.json                    # MCP Server 启动配置（必填）
│   └── icon.svg                    # 市场图标（必填）
│
├── skills/                         # Skill 技能包
│   └── kimi-work-bridge/
│       └── SKILL.md                # AI 使用说明（可选但推荐）
│
├── bridge-service/                 # MCP 桥接服务源码
│   ├── kimi_work_bridge.py         # 主服务（FastMCP）
│   └── requirements.txt            # Python 依赖
│
└── docs/                           # 文档
    ├── README.md                   # 本文件（总体方案）
    ├── DEPLOYMENT.md               # 部署指南
    └── SUBMISSION-CHECKLIST.md     # 开放平台提交审核清单
```

---

## 四、三步快速落地

### Step 1：注册并认证 WorkBuddy 开放平台

1. 访问 [open.workbuddy.cn](https://open.workbuddy.cn)
2. 点击「立即入驻」，完成账号注册
3. **个人开发者**：身份证 + 手机号 + 邮箱认证  
   **企业开发者**：腾讯云账号 / 微信公众号 / 企业法人实名
4. 等待资质审核（通常 1-3 个工作日）

### Step 2：本地部署桥接服务

```bash
# 1. 克隆或复制本项目到本地
cd bridge-service

# 2. 安装依赖（使用 Kimi Work 内置 Python 运行时）
pip install -r requirements.txt

# 3. 验证服务可启动
python kimi_work_bridge.py --test
```

详细部署说明见 [DEPLOYMENT.md](DEPLOYMENT.md)。

### Step 3：打包提交审核

```bash
# 按开放平台要求的格式打包
cd ..
zip -r kimi-work-connector-v1.0.zip connector/ skills/
# 然后在 open.workbuddy.cn 提交连接器 + Skill 审核
```

审核周期约 **7 个工作日**，通过后即可在 WorkBuddy 技能市场被搜索和调用。

---

## 五、关键技术细节

### 5.1 为什么需要桥接服务？

Kimi Work 当前定位是 **MCP Client**（消费外部 MCP Server），而 WorkBuddy 也需要通过 **MCP Client** 连接外部能力。两者都是客户端，无法直接互联。

桥接服务 (`kimi_work_bridge.py`) 作为一个独立的 **MCP Server**，将 Kimi Work 的核心能力（文件操作、数据分析、自动化等）封装为标准的 MCP Tool，供 WorkBuddy 调用。

### 5.2 传输方式选择

| 方式 | 适用场景 | 本方案选择 |
|---|---|---|
| **stdio** | 本地单用户，无网络依赖，调试简单 | ✅ 主推荐 |
| **Streamable HTTP** | 多用户、远程调用、服务化部署 | 进阶可选 |

本方案默认使用 **stdio**，因为 Kimi Work 与 WorkBuddy 通常运行在同一台桌面电脑上，本地管道通信最安全、延迟最低。

### 5.3 安全与权限

- 桥接服务默认只能访问用户显式授权的目录（通过 `ALLOWED_PATHS` 配置）
- 所有文件写操作需确认目标路径在白名单内
- 不涉及 Kimi Work 的内部会话数据或记忆内容，仅互通**文件级工作产物**

---

## 六、扩展建议

1. **进阶：HTTP 模式部署**  
   如需在团队内多用户共享 Kimi Work 能力，可将桥接服务改造为 HTTP Server，部署在局域网或内网服务器上。

2. **进阶：双向调用**  
   本方案是 WorkBuddy → Kimi Work 的单向调用。如需 Kimi Work 反向触发 WorkBuddy，可通过共享目录中的「指令文件」实现：Kimi Work 的 Automation 定期扫描目录，发现 WorkBuddy 的调用请求后执行对应任务。

3. **进阶：Expert 专家封装**  
   将 Kimi Work 的某个垂直领域工作流（如"财务分析报告生成"）封装为 WorkBuddy 的 **Expert 专家智能体**，获得更高的市场曝光和调用频次。

---

## 七、参考资料

- [WorkBuddy 开放平台官网](https://open.workbuddy.cn)
- [MCP 官方协议文档](https://modelcontextprotocol.io)
- [WorkBuddy 开发者社区 - 腾讯云](https://developer.cloud.tencent.com)
- [Kimi Work 使用指南](https://www.moonshot.cn)

---

> **下一步**：请阅读 [DEPLOYMENT.md](DEPLOYMENT.md) 完成桥接服务的本地部署与测试。
