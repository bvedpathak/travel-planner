#!/usr/bin/env python3
"""
Comprehensive static analysis runner for Travel Planner.

This script runs all configured static analysis tools and generates
comprehensive reports for code quality assessment.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class AnalysisRunner:
    """Main class for running static analysis tools."""

    def __init__(self, source_dirs: List[str], reports_dir: str = "reports"):
        """Initialize the analysis runner."""
        self.source_dirs = source_dirs
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.results = {}

    def run_tool(self, name: str, command: List[str], output_file: str = None) -> Dict[str, Any]:
        """Run a single analysis tool."""
        print(f"🔧 Running {name}...")

        try:
            if output_file:
                output_path = self.reports_dir / output_file
                with open(output_path, 'w') as f:
                    result = subprocess.run(
                        command,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

            return {
                "name": name,
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if not output_file else f"Output saved to {output_file}",
                "stderr": result.stderr,
                "output_file": output_file
            }

        except subprocess.TimeoutExpired:
            return {
                "name": name,
                "success": False,
                "error": "Tool execution timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "name": name,
                "success": False,
                "error": str(e),
                "returncode": -1
            }

    def run_black_check(self) -> Dict[str, Any]:
        """Run Black code formatting check."""
        command = ["python", "-m", "black", "--check", "--line-length=100"] + self.source_dirs
        return self.run_tool("Black Format Check", command)

    def run_isort_check(self) -> Dict[str, Any]:
        """Run isort import sorting check."""
        command = ["python", "-m", "isort", "--check-only", "--profile=black"] + self.source_dirs
        return self.run_tool("isort Import Check", command)

    def run_flake8(self) -> Dict[str, Any]:
        """Run flake8 linting."""
        command = ["python", "-m", "flake8"] + self.source_dirs
        return self.run_tool("Flake8 Linting", command, "flake8-report.txt")

    def run_pylint(self) -> Dict[str, Any]:
        """Run pylint analysis."""
        command = ["python", "-m", "pylint", "--output-format=text", "--reports=yes"] + self.source_dirs
        return self.run_tool("Pylint Analysis", command, "pylint-report.txt")

    def run_mypy(self) -> Dict[str, Any]:
        """Run mypy type checking."""
        command = ["python", "-m", "mypy", "--ignore-missing-imports"] + self.source_dirs
        return self.run_tool("MyPy Type Check", command, "mypy-report.txt")

    def run_bandit(self) -> Dict[str, Any]:
        """Run bandit security analysis."""
        command = ["python", "-m", "bandit", "-r"] + self.source_dirs + [
            "-f", "json", "-o", str(self.reports_dir / "bandit-report.json")
        ]
        result = self.run_tool("Bandit Security", command)

        # Also generate text report
        text_command = ["python", "-m", "bandit", "-r"] + self.source_dirs
        self.run_tool("Bandit Security (text)", text_command, "bandit-report.txt")

        return result

    def run_all_tools(self) -> Dict[str, Any]:
        """Run all analysis tools."""
        print("🚀 Starting comprehensive static analysis...")
        print(f"📁 Source directories: {', '.join(self.source_dirs)}")
        print(f"📊 Reports will be saved to: {self.reports_dir}")
        print("-" * 60)

        tools = [
            self.run_black_check,
            self.run_isort_check,
            self.run_flake8,
            self.run_pylint,
            self.run_mypy,
            self.run_bandit,
        ]

        results = {}
        for tool_func in tools:
            try:
                result = tool_func()
                results[result["name"]] = result

                # Print immediate feedback
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['name']}")

                if not result["success"] and result.get("stderr"):
                    print(f"   Error: {result['stderr'][:100]}...")

            except Exception as e:
                tool_name = tool_func.__name__.replace("run_", "").replace("_", " ").title()
                print(f"❌ {tool_name} - Failed to run: {str(e)}")
                results[tool_name] = {
                    "name": tool_name,
                    "success": False,
                    "error": str(e)
                }

        self.results = results
        return results

    def generate_summary_report(self) -> None:
        """Generate a summary report of all analysis results."""
        print("\n📋 Generating summary report...")

        summary_file = self.reports_dir / "analysis-summary.json"
        html_file = self.reports_dir / "analysis-summary.html"

        # JSON summary
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "source_directories": self.source_dirs,
            "total_tools": len(self.results),
            "successful_tools": sum(1 for r in self.results.values() if r["success"]),
            "failed_tools": sum(1 for r in self.results.values() if not r["success"]),
            "results": self.results
        }

        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)

        # HTML summary
        self.generate_html_report(html_file, summary_data)

        print(f"📄 Summary report: {summary_file}")
        print(f"🌐 HTML report: {html_file}")

    def generate_html_report(self, html_file: Path, summary_data: Dict) -> None:
        """Generate an HTML summary report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Planner - Static Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .tool-result {{ margin: 15px 0; padding: 15px; border-radius: 6px; border-left: 4px solid #ccc; }}
        .success {{ border-left-color: #27ae60; background: #d5f4e6; }}
        .failure {{ border-left-color: #e74c3c; background: #fdf2f2; }}
        .tool-name {{ font-weight: bold; font-size: 1.1em; }}
        .error-details {{ margin-top: 10px; padding: 10px; background: #f8f8f8; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
        .timestamp {{ color: #7f8c8d; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Static Analysis Report</h1>
        <p class="timestamp">Generated: {summary_data['timestamp']}</p>

        <div class="summary">
            <div class="metric">
                <div class="metric-value">{summary_data['total_tools']}</div>
                <div class="metric-label">Total Tools</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #27ae60;">{summary_data['successful_tools']}</div>
                <div class="metric-label">Successful</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: #e74c3c;">{summary_data['failed_tools']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(summary_data['source_directories'])}</div>
                <div class="metric-label">Source Dirs</div>
            </div>
        </div>

        <h2>📁 Source Directories</h2>
        <ul>
        """

        for dir_name in summary_data['source_directories']:
            html_content += f"<li><code>{dir_name}</code></li>"

        html_content += """
        </ul>

        <h2>🔧 Tool Results</h2>
        """

        for tool_name, result in summary_data['results'].items():
            status_class = "success" if result['success'] else "failure"
            status_icon = "✅" if result['success'] else "❌"

            html_content += f"""
        <div class="tool-result {status_class}">
            <div class="tool-name">{status_icon} {tool_name}</div>
            """

            if not result['success']:
                error_msg = result.get('stderr', result.get('error', 'Unknown error'))
                html_content += f'<div class="error-details">{error_msg}</div>'

            if result.get('output_file'):
                html_content += f'<p>📄 Report: <code>{result["output_file"]}</code></p>'

            html_content += "</div>"

        html_content += """
        </div>

        <h2>📊 Report Files</h2>
        <p>Check the <code>reports/</code> directory for detailed reports from each tool:</p>
        <ul>
            <li><code>flake8-report.txt</code> - Code style issues</li>
            <li><code>pylint-report.txt</code> - Comprehensive code analysis</li>
            <li><code>mypy-report.txt</code> - Type checking results</li>
            <li><code>bandit-report.json</code> - Security analysis (JSON)</li>
            <li><code>bandit-report.txt</code> - Security analysis (text)</li>
        </ul>
    </div>
</body>
</html>
        """

        with open(html_file, 'w') as f:
            f.write(html_content)

    def print_summary(self) -> None:
        """Print a summary of the analysis results."""
        print("\n" + "=" * 60)
        print("📊 STATIC ANALYSIS SUMMARY")
        print("=" * 60)

        total = len(self.results)
        successful = sum(1 for r in self.results.values() if r["success"])
        failed = total - successful

        print(f"📋 Total tools run: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Source directories: {', '.join(self.source_dirs)}")

        if failed > 0:
            print("\n🔍 Failed tools:")
            for name, result in self.results.items():
                if not result["success"]:
                    error = result.get("stderr", result.get("error", "Unknown error"))
                    print(f"   ❌ {name}: {error[:100]}{'...' if len(error) > 100 else ''}")

        print(f"\n📊 Detailed reports available in: {self.reports_dir}/")
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run comprehensive static analysis")
    parser.add_argument(
        "--source-dirs",
        nargs="+",
        default=["core", "services", "tools", "tools_solid", "server.py", "server_solid.py"],
        help="Source directories/files to analyze"
    )
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Directory to save reports"
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        choices=["black", "isort", "flake8", "pylint", "mypy", "bandit"],
        help="Specific tools to run (default: all)"
    )

    args = parser.parse_args()

    # Check if source directories exist
    for source_dir in args.source_dirs:
        if not os.path.exists(source_dir):
            print(f"❌ Source directory/file does not exist: {source_dir}")
            sys.exit(1)

    runner = AnalysisRunner(args.source_dirs, args.reports_dir)

    # Run analysis
    try:
        results = runner.run_all_tools()
        runner.generate_summary_report()
        runner.print_summary()

        # Exit with error code if any tool failed
        failed_count = sum(1 for r in results.values() if not r["success"])
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} tools reported issues. Check reports for details.")
            sys.exit(1)
        else:
            print("\n🎉 All analysis tools completed successfully!")

    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()