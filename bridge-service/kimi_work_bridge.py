# Kimi Work 桥接服务 - MCP Server
# 作用：将 Kimi Work 的核心能力封装为 MCP Tool，供 WorkBuddy 调用
# 协议：Model Context Protocol (MCP) via stdio
# 依赖：fastmcp, pandas, openpyxl, reportlab, markdown

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    print("ERROR: 请先安装 mcp 库: pip install mcp", file=sys.stderr)
    sys.exit(1)

# ── 配置 ──────────────────────────────────────────────
SERVER_NAME = "kimi-work-bridge"
SERVER_VERSION = "1.1.0"

# 从环境变量读取允许的目录（逗号分隔），默认使用当前工作目录下的 bridge-io
DEFAULT_BRIDGE_DIR = Path(__file__).parent.parent / "bridge-io"
ALLOWED_PATHS = [
    Path(p.strip()).expanduser().resolve()
    for p in os.environ.get("KIMI_WORK_BRIDGE_ALLOWED_PATHS", str(DEFAULT_BRIDGE_DIR)).split(",")
    if p.strip()
]

LOG_LEVEL = os.environ.get("KIMI_WORK_BRIDGE_LOG_LEVEL", "INFO")

# 确保桥接目录存在
for p in ALLOWED_PATHS:
    p.mkdir(parents=True, exist_ok=True)

# 日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(SERVER_NAME)

# 初始化 MCPServer (mcp 2.x)
mcp = MCPServer(SERVER_NAME, version=SERVER_VERSION)


# ── 辅助函数 ──────────────────────────────────────────
def _resolve_path(file_path: str) -> Path:
    """解析路径并确保在白名单内。相对路径基于桥接目录解析。"""
    p = Path(file_path).expanduser()
    if not p.is_absolute():
        p = _ensure_bridge_dir() / p
    p = p.resolve()
    for allowed in ALLOWED_PATHS:
        try:
            p.relative_to(allowed)
            return p
        except ValueError:
            continue
    raise PermissionError(f"路径 {p} 不在允许的目录内: {ALLOWED_PATHS}")


def _ensure_bridge_dir() -> Path:
    """返回第一个可用的桥接目录"""
    return ALLOWED_PATHS[0]


# ── MCP Tools ─────────────────────────────────────────

@mcp.tool()
def list_workspace_files(directory: Optional[str] = None) -> str:
    """
    列出 Kimi Work 桥接工作区中的文件列表。

    参数：
      - directory (str, optional): 子目录路径，默认列出根桥接目录

    返回：
      - str: JSON 格式的文件列表，包含文件名、大小、修改时间
    """
    try:
        base = _resolve_path(directory) if directory else _ensure_bridge_dir()
        files = []
        for f in base.iterdir():
            if f.is_file():
                stat = f.stat()
                files.append({
                    "name": f.name,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime
                })
        return json.dumps({"directory": str(base), "files": files}, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"list_workspace_files 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    读取桥接工作区中指定文件的内容。

    参数：
      - file_path (str): 文件相对路径或绝对路径（必须在白名单目录内）

    返回：
      - str: 文件内容文本，或错误信息
    """
    try:
        p = _resolve_path(file_path)
        if not p.exists():
            return json.dumps({"error": f"文件不存在: {p}"})
        if p.stat().st_size > 5 * 1024 * 1024:
            return json.dumps({"error": "文件超过 5MB，请使用分片读取"})
        content = p.read_text(encoding="utf-8")
        return json.dumps({"file_path": str(p), "content": content}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"read_file 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    向桥接工作区写入文本文件。WorkBuddy 可通过此方式向 Kimi Work 传递任务指令或数据。

    参数：
      - file_path (str): 目标文件路径（必须在白名单目录内）
      - content (str): 文件内容

    返回：
      - str: 操作结果状态
    """
    try:
        p = _resolve_path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        logger.info(f"已写入文件: {p}")
        return json.dumps({"success": True, "file_path": str(p), "bytes_written": len(content.encode("utf-8"))})
    except Exception as e:
        logger.error(f"write_file 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_data(file_path: str, analysis_type: str = "summary") -> str:
    """
    对桥接工作区中的 CSV 或 Excel 文件进行数据分析，返回统计结果。

    参数：
      - file_path (str): 数据文件路径（.csv 或 .xlsx）
      - analysis_type (str): 分析类型，可选 "summary"（概览）、"columns"（列统计）、"correlation"（相关性）

    返回：
      - str: JSON 格式的分析结果
    """
    try:
        p = _resolve_path(file_path)
        if not p.exists():
            return json.dumps({"error": f"文件不存在: {p}"})

        try:
            import pandas as pd
        except ImportError:
            return json.dumps({"error": "pandas 未安装，无法执行数据分析。请运行: pip install pandas openpyxl"})

        if p.suffix.lower() == ".csv":
            df = pd.read_csv(p)
        elif p.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(p)
        else:
            return json.dumps({"error": "仅支持 .csv 和 .xlsx 文件"})

        result = {"file_path": str(p), "rows": len(df), "columns": list(df.columns)}

        if analysis_type == "summary":
            result["describe"] = json.loads(df.describe().to_json())
        elif analysis_type == "columns":
            result["column_stats"] = {col: {"dtype": str(df[col].dtype), "null_count": int(df[col].isnull().sum())} for col in df.columns}
        elif analysis_type == "correlation":
            numeric_df = df.select_dtypes(include=["number"])
            if not numeric_df.empty:
                result["correlation"] = json.loads(numeric_df.corr().to_json())
            else:
                result["correlation"] = "无数值列可计算相关性"
        else:
            result["describe"] = json.loads(df.describe().to_json())

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"analyze_data 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_excel_report(data_json: str, output_path: str, sheet_name: str = "Report") -> str:
    """
    将 JSON 数据转换为 Excel 报告文件。WorkBuddy 可将结构化数据交给 Kimi Work 生成专业表格。

    参数：
      - data_json (str): JSON 数组字符串，每行一个对象
      - output_path (str): 输出 .xlsx 文件路径（必须在白名单目录内）
      - sheet_name (str): 工作表名称，默认 "Report"

    返回：
      - str: 操作结果与文件路径
    """
    try:
        p = _resolve_path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        try:
            import pandas as pd
        except ImportError:
            return json.dumps({"error": "pandas 未安装，无法生成 Excel。请运行: pip install pandas openpyxl"})

        data = json.loads(data_json)
        df = pd.DataFrame(data)
        df.to_excel(p, sheet_name=sheet_name, index=False)
        logger.info(f"已生成 Excel: {p}")
        return json.dumps({"success": True, "file_path": str(p), "rows": len(df), "columns": list(df.columns)})
    except Exception as e:
        logger.error(f"generate_excel_report 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_markdown_report(title: str, sections_json: str, output_path: str) -> str:
    """
    生成结构化 Markdown 报告文件。WorkBuddy 可将分析结论交给 Kimi Work 生成格式化的长文报告。

    参数：
      - title (str): 报告标题
      - sections_json (str): JSON 数组，每个元素为 {"heading": "标题", "content": "正文内容"}
      - output_path (str): 输出 .md 文件路径（必须在白名单目录内）

    返回：
      - str: 操作结果与文件路径
    """
    try:
        p = _resolve_path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        sections = json.loads(sections_json)
        lines = [f"# {title}", "", f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "---", ""]

        for sec in sections:
            heading = sec.get("heading", "未命名章节")
            content = sec.get("content", "")
            level = sec.get("level", 2)
            prefix = "#" * level
            lines.extend([f"{prefix} {heading}", "", content, "", "---", ""])

        md_content = "\n".join(lines)
        p.write_text(md_content, encoding="utf-8")
        logger.info(f"已生成 Markdown 报告: {p}")
        return json.dumps({"success": True, "file_path": str(p), "sections": len(sections), "chars": len(md_content)})
    except Exception as e:
        logger.error(f"generate_markdown_report 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_html_dashboard(title: str, data_json: str, output_path: str, chart_type: str = "bar") -> str:
    """
    将 JSON 数据生成为可独立打开的 HTML 看板页面。支持表格和简单图表展示。

    参数：
      - title (str): 看板标题
      - data_json (str): JSON 数组，每行一个数据对象，第一列作为标签
      - output_path (str): 输出 .html 文件路径（必须在白名单目录内）
      - chart_type (str): 图表类型，可选 "bar"（柱状图）、"line"（折线图）、"table"（仅表格）

    返回：
      - str: 操作结果与文件路径
    """
    try:
        p = _resolve_path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        data = json.loads(data_json)
        if not data:
            return json.dumps({"error": "数据为空"})

        columns = list(data[0].keys())
        label_col = columns[0]
        numeric_cols = [c for c in columns[1:] if isinstance(data[0].get(c), (int, float))]

        table_rows = ""
        for row in data:
            cells = "".join(f"<td>{row.get(c, '')}</td>" for c in columns)
            table_rows += f"<tr>{cells}</tr>\n"

        table_header = "".join(f"<th>{c}</th>" for c in columns)

        chart_script = ""
        if numeric_cols and chart_type != "table":
            labels = [str(row.get(label_col, i)) for i, row in enumerate(data)]
            datasets = []
            for i, col in enumerate(numeric_cols):
                values = [row.get(col, 0) for row in data]
                color = ["#e94560", "#0f3460", "#533483", "#f39422", "#16c79a"][i % 5]
                datasets.append({
                    "label": col,
                    "data": values,
                    "backgroundColor": color if chart_type == "bar" else "transparent",
                    "borderColor": color,
                    "borderWidth": 2,
                    "fill": chart_type == "line"
                })

            chart_script = f"""
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
            <canvas id="chart" style="max-height:400px;"></canvas>
            <script>
            new Chart(document.getElementById('chart'), {{
                type: '{chart_type}',
                data: {{
                    labels: {json.dumps(labels, ensure_ascii=False)},
                    datasets: {json.dumps(datasets)}
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }} }}
            }});
            </script>
            """
        else:
            chart_script = "<p style='color:#888;'>数据无可视化数值列，仅展示表格。</p>"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; background: #f5f5f7; color: #1a1a2e; }}
  .container {{ max-width: 1200px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  h1 {{ font-size: 24px; margin-bottom: 8px; color: #0f3460; }}
  .meta {{ color: #888; font-size: 12px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }}
  th {{ background: #fafafa; font-weight: 600; color: #555; }}
  tr:hover {{ background: #f8f9ff; }}
</style>
</head>
<body>
<div class="container">
  <h1>{title}</h1>
  <div class="meta">生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据行数: {len(data)}</div>
  {chart_script}
  <table>
    <thead><tr>{table_header}</tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>
</body>
</html>"""

        p.write_text(html, encoding="utf-8")
        logger.info(f"已生成 HTML 看板: {p}")
        return json.dumps({"success": True, "file_path": str(p), "rows": len(data), "columns": len(columns)})
    except Exception as e:
        logger.error(f"create_html_dashboard 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_pdf_from_markdown(md_file_path: str, output_path: str) -> str:
    """
    将桥接目录中的 Markdown 文件转换为 PDF。需要 reportlab 支持。

    参数：
      - md_file_path (str): 输入 .md 文件路径
      - output_path (str): 输出 .pdf 文件路径（必须在白名单目录内）

    返回：
      - str: 操作结果与文件路径
    """
    try:
        md_p = _resolve_path(md_file_path)
        out_p = _resolve_path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if not md_p.exists():
            return json.dumps({"error": f"源文件不存在: {md_p}"})

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            return json.dumps({"error": "reportlab 未安装，无法生成 PDF。请运行: pip install reportlab"})

        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]
        font_name = "Helvetica"
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont("CustomCN", fp))
                    font_name = "CustomCN"
                    break
                except Exception:
                    continue

        content = md_p.read_text(encoding="utf-8")
        doc = SimpleDocTemplate(str(out_p), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            if line.startswith("# "):
                story.append(Paragraph(line[2:], styles["Heading1"]))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
            elif line.startswith("### "):
                story.append(Paragraph(line[4:], styles["Heading3"]))
            elif line.startswith("> "):
                story.append(Paragraph(f"<i>{line[2:]}</i>", styles["Italic"]))
            elif line.startswith("---"):
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 4))

        doc.build(story)
        logger.info(f"已生成 PDF: {out_p}")
        return json.dumps({"success": True, "md_source": str(md_p), "pdf_output": str(out_p)})
    except Exception as e:
        logger.error(f"generate_pdf_from_markdown 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def convert_data_to_pptx_outline(data_json: str, output_path: str, title: str = "演示文稿") -> str:
    """
    将结构化数据转换为 PPT 大纲 JSON 文件。WorkBuddy 可读取该 JSON 后调用自身 PPT 生成能力完成最终制作。

    参数：
      - data_json (str): JSON 数组，每个元素包含 "slide_title" 和 "bullet_points"（字符串数组）
      - output_path (str): 输出 .json 文件路径（必须在白名单目录内）
      - title (str): 演示文稿总标题

    返回：
      - str: 操作结果与文件路径
    """
    try:
        p = _resolve_path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        slides = json.loads(data_json)
        outline = {
            "title": title,
            "slide_count": len(slides),
            "slides": []
        }

        for i, slide in enumerate(slides, 1):
            outline["slides"].append({
                "slide_number": i,
                "title": slide.get("slide_title", f"第{i}页"),
                "bullets": slide.get("bullet_points", []),
                "notes": slide.get("speaker_notes", "")
            })

        p.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"已生成 PPT 大纲: {p}")
        return json.dumps({"success": True, "file_path": str(p), "slides": len(slides)})
    except Exception as e:
        logger.error(f"convert_data_to_pptx_outline 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def deep_research_brief(topic: str, scope: str, output_path: str, max_sources: int = 5) -> str:
    """
    在桥接目录中创建一个深度研究任务简报。Kimi Work 的 Automation 检测到后，会调用其联网搜索与长文本分析能力完成研究。

    参数：
      - topic (str): 研究主题
      - scope (str): 研究范围描述（如"近3个月的融资动态"、"技术架构对比"）
      - output_path (str): 输出研究简报 .md 文件路径（必须在白名单目录内）
      - max_sources (int): 建议参考来源数量，默认 5

    返回：
      - str: 创建的研究任务文件路径
    """
    try:
        p = _resolve_path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        brief = {
            "type": "deep_research",
            "topic": topic,
            "scope": scope,
            "max_sources": max_sources,
            "status": "pending",
            "created_by": "workbuddy",
            "instructions": f"""请对以下主题进行深度研究：

主题：{topic}
范围：{scope}
要求：
1. 搜索并整合至少 {max_sources} 个权威来源的信息
2. 使用 Kimi Work 的联网搜索与多源整合能力
3. 输出结构化的 Markdown 研究报告，包含摘要、核心发现、详细分析、结论与建议
4. 将最终结果写入 {output_path}
5. 完成后将本任务状态更新为 done
""",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }

        task_file = _ensure_bridge_dir() / f"research_{topic.replace(' ', '_').replace('/', '_')[:30]}.json"
        task_file.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"已创建深度研究任务: {task_file}")
        return json.dumps({"success": True, "task_file": str(task_file), "brief": brief})
    except Exception as e:
        logger.error(f"deep_research_brief 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_task_instruction(task_name: str, instructions: str, priority: str = "normal") -> str:
    """
    在桥接目录中创建一个任务指令文件，Kimi Work 的 Automation 可定时扫描并执行该任务。
    这是 WorkBuddy → Kimi Work 单向任务调度的核心机制。

    参数：
      - task_name (str): 任务名称（作为文件名前缀）
      - instructions (str): 任务详细指令
      - priority (str): 优先级，可选 "low" / "normal" / "high"

    返回：
      - str: 创建的任务文件路径
    """
    try:
        base = _ensure_bridge_dir()
        task_file = base / f"task_{priority}_{task_name}.json"
        task_data = {
            "task_name": task_name,
            "priority": priority,
            "instructions": instructions,
            "created_by": "workbuddy",
            "status": "pending",
            "timestamp": asyncio.get_event_loop().time()
        }
        task_file.write_text(json.dumps(task_data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"已创建任务指令: {task_file}")
        return json.dumps({"success": True, "task_file": str(task_file), "task": task_data})
    except Exception as e:
        logger.error(f"create_task_instruction 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def check_task_status(task_name: str) -> str:
    """
    查询由 WorkBuddy 创建的任务指令执行状态。Kimi Work 执行后会将 status 改为 done 并追加结果。

    参数：
      - task_name (str): 任务名称

    返回：
      - str: 任务状态与结果（如已执行）
    """
    try:
        base = _ensure_bridge_dir()
        candidates = list(base.glob(f"task_*_{task_name}.json"))
        if not candidates:
            return json.dumps({"status": "not_found", "message": f"未找到任务: {task_name}"})

        task_file = max(candidates, key=lambda p: p.stat().st_mtime)
        data = json.loads(task_file.read_text(encoding="utf-8"))
        return json.dumps({"task_file": str(task_file), "status": data.get("status", "unknown"), "data": data}, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"check_task_status 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def sync_clipboard(action: str, content: Optional[str] = None) -> str:
    """
    通过桥接目录中的共享文件实现 WorkBuddy 与 Kimi Work 的剪贴板内容交换。

    参数：
      - action (str): 操作类型，"write"（写入）或 "read"（读取）
      - content (str, optional): 当 action="write" 时，要写入的文本内容

    返回：
      - str: 操作结果或读取到的内容
    """
    try:
        cb_file = _ensure_bridge_dir() / "shared_clipboard.txt"
        if action == "write":
            if content is None:
                return json.dumps({"error": "写入操作需要提供 content 参数"})
            cb_file.write_text(content, encoding="utf-8")
            logger.info(f"剪贴板已写入: {len(content)} 字符")
            return json.dumps({"success": True, "action": "write", "chars": len(content)})
        elif action == "read":
            if not cb_file.exists():
                return json.dumps({"status": "empty", "message": "剪贴板为空"})
            text = cb_file.read_text(encoding="utf-8")
            return json.dumps({"success": True, "action": "read", "content": text, "chars": len(text)})
        else:
            return json.dumps({"error": f"不支持的操作: {action}，请使用 write 或 read"})
    except Exception as e:
        logger.error(f"sync_clipboard 失败: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_bridge_info() -> str:
    """
    获取桥接服务的基本信息与配置。用于 WorkBuddy 初始化时探测能力。

    返回：
      - str: 服务器名称、版本、允许访问的目录、可用工具列表
    """
    try:
        info = {
            "server_name": SERVER_NAME,
            "server_version": SERVER_VERSION,
            "allowed_paths": [str(p) for p in ALLOWED_PATHS],
            "tools": [
                "list_workspace_files",
                "read_file",
                "write_file",
                "analyze_data",
                "generate_excel_report",
                "generate_markdown_report",
                "create_html_dashboard",
                "generate_pdf_from_markdown",
                "convert_data_to_pptx_outline",
                "deep_research_brief",
                "create_task_instruction",
                "check_task_status",
                "sync_clipboard",
                "get_bridge_info"
            ],
            "notes": "WorkBuddy 可通过本桥接服务与 Kimi Work 进行文件级互通、数据分析、报告生成与任务调度"
        }
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── 启动入口 ──────────────────────────────────────────
async def main():
    logger.info(f"{SERVER_NAME} v{SERVER_VERSION} 启动中...")
    logger.info(f"允许目录: {ALLOWED_PATHS}")
    logger.info("MCP Server 以 STDIO 模式运行，等待 WorkBuddy 连接...")
    await mcp.run_stdio_async()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({
            "server_name": SERVER_NAME,
            "version": SERVER_VERSION,
            "status": "ready",
            "allowed_paths": [str(p) for p in ALLOWED_PATHS],
            "message": "桥接服务可正常启动。请通过 MCP Client 连接使用。"
        }, ensure_ascii=False, indent=2))
    else:
        asyncio.run(main())
