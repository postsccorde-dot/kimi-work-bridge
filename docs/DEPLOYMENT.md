# 部署指南

> 本文档指导你在本地完成 Kimi Work MCP 桥接服务的部署与验证。

---

## 环境要求

| 项目 | 要求 | 说明 |
|---|---|---|
| Python | 3.10+ | Kimi Work 内置运行时已满足 |
| 操作系统 | macOS / Windows / Linux | 与 WorkBuddy 保持一致 |
| 磁盘空间 | ≥ 50 MB | 桥接目录 + 依赖 |
| 网络 | 可选 | 本地 stdio 模式无需网络 |

---

## 快速部署（5 分钟）

### 1. 准备目录

将本项目的 `workbuddy-bridge/` 目录复制到你希望存放的位置，例如：

```bash
# macOS / Linux
cp -r workbuddy-bridge ~/Documents/kimi-work-bridge

# Windows (PowerShell)
Copy-Item -Recurse workbuddy-bridge $env:USERPROFILE\Documents\kimi-work-bridge
```

### 2. 创建桥接交换目录

```bash
mkdir -p ~/Documents/kimi-work-bridge/bridge-io
```

此目录是 WorkBuddy 与 Kimi Work 交换文件的唯一通道。

### 3. 安装依赖

**方式 A：使用 Kimi Work 内置 Python（推荐）**

Kimi Work 自带 Python 运行时，路径通常为：
- macOS: `~/Library/Application Support/kimi-desktop/daimon-share/daimon/runtime/python/bin/python`
- Windows: `%LOCALAPPDATA%\kimi-desktop\daimon-share\daimon\runtime\python\python.exe`

```bash
# macOS 示例
PYTHON="$HOME/Library/Application Support/kimi-desktop/daimon-share/daimon/runtime/python/bin/python"
"$PYTHON" -m pip install -r bridge-service/requirements.txt
```

**方式 B：使用系统 Python**

```bash
pip install -r bridge-service/requirements.txt
```

### 4. 验证服务

```bash
python bridge-service/kimi_work_bridge.py --test
```

预期输出：
```json
{
  "server_name": "kimi-work-bridge",
  "version": "1.0.0",
  "status": "ready",
  "allowed_paths": ["/Users/xxx/Documents/kimi-work-bridge/bridge-io"],
  "message": "桥接服务可正常启动。请通过 MCP Client 连接使用。"
}
```

---

## WorkBuddy 端配置

### 方式 1：通过 MCP 面板添加（推荐）

1. 打开 WorkBuddy，进入「设置」→「连接器」→「MCP」
2. 点击「添加 MCP 服务」
3. 在 JSON 配置框中填入以下内容（注意替换 `${workspace}` 为实际路径）：

```json
{
  "mcpServers": {
    "kimi-work-bridge": {
      "command": "python",
      "args": [
        "/Users/xxx/Documents/kimi-work-bridge/bridge-service/kimi_work_bridge.py"
      ],
      "env": {
        "KIMI_WORK_BRIDGE_MODE": "stdio",
        "KIMI_WORK_BRIDGE_ALLOWED_PATHS": "/Users/xxx/Documents/kimi-work-bridge/bridge-io",
        "KIMI_WORK_BRIDGE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

4. 保存并刷新，WorkBuddy 会自动启动桥接服务进程
5. 在聊天中测试：「帮我列出桥接工作区的文件」

### 方式 2：通过 Skill 市场安装

待连接器通过开放平台审核后，直接在 WorkBuddy 技能市场搜索「Kimi Work 桥接」，一键安装。

---

## Kimi Work 端配置

为了让 Kimi Work 能够"接收" WorkBuddy 发来的任务，需要设置一个简单的文件监听机制。

### 设置文件监听 Automation（可选但推荐）

在 Kimi Work 中创建一个 Blueprint Automation：

1. 进入 Kimi Work → Automation → 新建 Automation
2. 触发器：选择 **interval**，每 5 分钟运行一次
3. 执行内容：运行以下 Python 脚本

```python
import json, os, glob
from pathlib import Path

BRIDGE_DIR = Path.home() / "Documents/kimi-work-bridge/bridge-io"

for task_file in sorted(BRIDGE_DIR.glob("task_*_*.json")):
    data = json.loads(task_file.read_text())
    if data.get("status") != "pending":
        continue
    
    # 读取任务指令
    instructions = data["instructions"]
    print(f"[WorkBuddy 任务] {data['task_name']}: {instructions}")
    
    # TODO: 在这里执行实际任务（如搜索、分析、生成报告）
    # 任务完成后，更新状态并写入结果
    result = {"status": "done", "result": "任务已完成，结果如下：..."}
    
    data.update(result)
    data["completed_at"] = str(__import__('datetime').datetime.now())
    task_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"  → 已完成: {task_file.name}")
```

4. 保存 Automation，启用定时执行

这样，当 WorkBuddy 通过 `create_task_instruction` 创建任务文件后，Kimi Work 会在 5 分钟内自动检测并执行。

---

## 故障排查

### 问题 1：WorkBuddy 连接失败，提示 "command not found: python"

**原因**：WorkBuddy 找不到 Python 可执行文件。  
**解决**：在 `mcp.json` 中使用 Python 的绝对路径：

```json
"command": "/usr/bin/python3"
```

### 问题 2：提示 "pandas 未安装，无法执行数据分析"

**原因**：桥接服务所在 Python 环境缺少依赖。  
**解决**：在正确的 Python 环境下运行：

```bash
/path/to/python -m pip install pandas openpyxl
```

### 问题 3：文件操作提示 "路径不在允许的目录内"

**原因**：`file_path` 超出了 `KIMI_WORK_BRIDGE_ALLOWED_PATHS` 白名单。  
**解决**：确保所有文件路径都在配置的桥接目录下，或扩展环境变量：

```json
"env": {
  "KIMI_WORK_BRIDGE_ALLOWED_PATHS": "/path/a,/path/b,/path/c"
}
```

### 问题 4：Kimi Work 没有收到 WorkBuddy 的任务

**原因**：Automation 未启用，或桥接目录路径不一致。  
**解决**：
1. 检查 Kimi Work 中 Automation 是否已启用
2. 确认 Automation 脚本中的 `BRIDGE_DIR` 与桥接服务配置中的 `ALLOWED_PATHS` 指向同一目录
3. 手动在桥接目录创建一个 `task_test.json` 文件，观察 Automation 是否能检测到

---

## 升级与维护

- **更新桥接服务**：直接替换 `kimi_work_bridge.py` 文件，重启 WorkBuddy 的 MCP 连接即可
- **添加新工具**：在 `kimi_work_bridge.py` 中新增 `@mcp.tool()` 装饰的函数，然后同步更新 `skills/kimi-work-bridge/SKILL.md`
- **版本管理**：修改 `connector-meta.json` 和桥接服务中的 `SERVER_VERSION`，重新打包提交审核

---

## 安全提示

1. **不要**将桥接目录设在系统敏感路径（如 `~/.ssh`、`/etc`）
2. **不要**在 `mcp.json` 中硬编码 API Key 或密码
3. 如果多人共用一台机器，建议为每个用户配置独立的桥接目录
4. 定期检查桥接目录中的任务文件，避免堆积过多历史文件

---

> 部署完成后，请阅读 [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md) 准备开放平台提交审核材料。
