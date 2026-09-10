#!/usr/bin/env python3
"""桥接服务完整功能测试脚本"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# 设置桥接目录为项目内的 bridge-io（导入前必须设置好环境变量）
TEST_DIR = Path(__file__).parent.parent / "bridge-io"
TEST_DIR.mkdir(parents=True, exist_ok=True)
os.environ["KIMI_WORK_BRIDGE_ALLOWED_PATHS"] = str(TEST_DIR)

sys.path.insert(0, str(Path(__file__).parent))
from kimi_work_bridge import (
    list_workspace_files, read_file, write_file,
    analyze_data, generate_excel_report, generate_markdown_report,
    create_html_dashboard, convert_data_to_pptx_outline,
    generate_chart_image, generate_pptx,
    create_task_instruction, check_task_status, sync_clipboard,
    get_bridge_info
)

passed = []
failed = []

def check(name, result, expect_success=True):
    try:
        data = json.loads(result)
        ok = data.get("success", False) if expect_success else "error" not in data
        if expect_success and not ok:
            ok = "error" not in data
        if ok:
            passed.append(name)
            print(f"  ✅ {name}")
        else:
            failed.append(f"{name}: {data.get('error', 'unknown')}")
            print(f"  ❌ {name}: {data.get('error', 'unknown')}")
    except Exception as e:
        failed.append(f"{name}: {e}")
        print(f"  ❌ {name}: {e}")

print("=" * 50)
print("Kimi Work Bridge — 功能测试")
print(f"测试目录: {TEST_DIR}")
print("=" * 50)

# 1. 服务器信息
print("\n[1] 服务器信息")
r = get_bridge_info()
check("get_bridge_info", r)

# 2. 文件操作
print("\n[2] 文件操作")
r = write_file("test/hello.txt", "Hello from WorkBuddy!")
check("write_file", r)
r = read_file("test/hello.txt")
check("read_file", r)
r = list_workspace_files()
check("list_workspace_files", r)

# 3. 数据分析
print("\n[3] 数据分析")
import pandas as pd
df = pd.DataFrame({
    "姓名": ["张三", "李四", "王五", "赵六"],
    "销售额": [150000, 230000, 180000, 210000],
    "月份": ["8月", "8月", "8月", "8月"]
})
df.to_excel(str(TEST_DIR / "sales_test.xlsx"), index=False)

r = analyze_data("sales_test.xlsx", "summary")
check("analyze_data summary", r)
r = analyze_data("sales_test.xlsx", "columns")
check("analyze_data columns", r)
r = analyze_data("sales_test.xlsx", "correlation")
check("analyze_data correlation", r)

# 4. Excel 报告
print("\n[4] Excel 报告")
r = generate_excel_report(
    '[{"产品": "A", "销量": 100}, {"产品": "B", "销量": 200}]',
    "report_test.xlsx"
)
check("generate_excel_report", r)

# 5. Markdown 报告
print("\n[5] Markdown 报告")
r = generate_markdown_report(
    "测试报告",
    '[{"heading": "概述", "content": "本季度表现良好"}, {"heading": "详情", "content": "同比增长 23%"}]',
    "report_test.md"
)
check("generate_markdown_report", r)

# 6. HTML 看板
print("\n[6] HTML 看板")
r = create_html_dashboard(
    "销售看板",
    '[{"月份": "8月", "销售额": 150}, {"月份": "9月", "销售额": 230}]',
    "dashboard_test.html",
    "bar"
)
check("create_html_dashboard", r)

# 7. PPT 大纲
print("\n[7] PPT 大纲")
r = convert_data_to_pptx_outline(
    '[{"slide_title": "市场概览", "bullet_points": ["Q3 增长 23%"]}]',
    "ppt_test.json",
    "Q3 复盘"
)
check("convert_data_to_pptx_outline", r)

# 8. 任务调度
print("\n[8] 任务调度")
r = create_task_instruction("test_task", "请执行测试任务", "high")
check("create_task_instruction", r)
r = check_task_status("test_task")
check("check_task_status", r)

# 9. 剪贴板
print("\n[9] 剪贴板")
r = sync_clipboard("write", "测试剪贴板内容")
check("sync_clipboard write", r)
r = sync_clipboard("read")
check("sync_clipboard read", r)

# 10. 图表与 PPT 生成（v1.2）
print("\n[10] 图表与 PPT 生成 (v1.2)")
r = generate_chart_image(
    "月度销售额",
    json.dumps([{"月份": "8月", "销售额": 150}, {"月份": "9月", "销售额": 230}], ensure_ascii=False),
    "charts/monthly_sales.png",
    "bar"
)
check("generate_chart_image", r)
r = generate_pptx(
    "桥接服务测试汇报",
    json.dumps([
        {"type": "title", "heading": "桥接服务测试汇报", "content": "v1.2 新功能验证"},
        {"type": "bullets", "heading": "核心能力", "bullet_points": ["文件互通", "数据分析", "报告生成"]}
    ], ensure_ascii=False),
    "reports/v12_test.pptx"
)
check("generate_pptx", r)

# 11. 安全测试：路径越界
print("\n[11] 安全测试")
try:
    r = write_file("/etc/passwd_test", "should fail")
    data = json.loads(r)
    if "error" in data:
        passed.append("路径越界拦截")
        print("  ✅ 路径越界拦截")
    else:
        failed.append("路径越界拦截: 未拦截")
        print("  ❌ 路径越界拦截: 未拦截")
except Exception:
    passed.append("路径越界拦截")
    print("  ✅ 路径越界拦截")

# 汇总
print("\n" + "=" * 50)
print(f"测试结果: {len(passed)} 通过, {len(failed)} 失败")
print("=" * 50)
if failed:
    print("\n失败项:")
    for f in failed:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("\n🎉 全部测试通过！")
    print(f"\n测试产物目录: {TEST_DIR}")
