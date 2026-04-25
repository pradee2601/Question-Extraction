# agent/report_generator.py

from pathlib import Path
from datetime import datetime
import json

def generate_report(filename: str, entries: list, final_status: str, reports_folder: Path, llm_stats: dict = None):
    """Generate a Markdown validation report for a processed JSON file."""

    clean = [e for e in entries if e["status"] in ("CLEAN", "FIXED_BY_RULES", "FIXED_BY_LLM")]
    flagged = [e for e in entries if e["status"] == "FLAGGED"]

    report_lines = [
        f"# Validation Report: `{filename}`",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Final Status:** `{final_status}`",
        "",
        "## Summary",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Total Questions | {len(entries)} |",
        f"| ✅ Clean (no changes) | {sum(1 for e in entries if e['status'] == 'CLEAN')} |",
        f"| 🔧 Fixed by Rules | {sum(1 for e in entries if e['status'] == 'FIXED_BY_RULES')} |",
        f"| 🤖 Fixed by LLM | {sum(1 for e in entries if e['status'] == 'FIXED_BY_LLM')} |",
        f"| 🚨 Flagged (needs review) | {len(flagged)} |",
        "",
    ]

    if llm_stats and llm_stats.get("total_calls", 0) > 0:
        report_lines += [
            "## 🤖 AI Resource Usage",
            f"- **Total AI Repairs:** {llm_stats['total_calls']}",
            f"- **Input (Prompt) Tokens:** {llm_stats['prompt_tokens']:,}",
            f"- **Output (Completion) Tokens:** {llm_stats['completion_tokens']:,}",
            f"- **Total Tokens:** {llm_stats['total_tokens']:,}",
            f"- **Estimated Repair Cost:** ₹{llm_stats['cost_by_tokens']}",
            "",
        ]

    if flagged:
        report_lines += ["## 🚨 Flagged Questions", ""]
        for entry in flagged:
            report_lines.append(f"### Question #{entry['index'] + 1}")
            for issue in entry.get("remaining_issues", []):
                report_lines.append(
                    f"- **{issue['severity']}** | Field: `{issue['field']}` — {issue['message']}"
                )
            report_lines.append("")

    report_path = reports_folder / filename.replace(".json", "_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Report saved: {report_path}")
