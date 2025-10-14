"""
DroneWatch Alerting System - Multi-Channel Notifications
Wave 12 Implementation

Alert channels:
- Console output (colorized)
- Log file
- Markdown report
- Optional: Email, Slack

Alert levels:
- INFO: 1-2 sources failed
- WARNING: 3-9 sources failed
- CRITICAL: 10+ sources failed

Author: DroneWatch Team
Date: 2025-10-14
Version: 1.0.0
"""

import os
from datetime import datetime
from typing import List, Dict
from colorama import Fore, Back, Style, init
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)


class AlertLevel:
    """Alert level constants"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertingSystem:
    """Multi-channel alerting for source verification failures"""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize alerting system

        Args:
            log_dir: Directory for log files (default: logs/)
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def determine_alert_level(self, failed_count: int) -> str:
        """
        Determine alert level based on failure count

        Args:
            failed_count: Number of failed sources

        Returns:
            Alert level (INFO, WARNING, CRITICAL)
        """
        if failed_count >= 10:
            return AlertLevel.CRITICAL
        elif failed_count >= 3:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO

    def console_output(self, results: List, summary: Dict, alert_level: str):
        """
        Print colorized console output

        Args:
            results: List of VerificationResult objects
            summary: Summary statistics dict
            alert_level: Alert level
        """
        # Header
        print()
        print(Fore.CYAN + "╔" + "=" * 58 + "╗")
        print(Fore.CYAN + "║" + " " * 12 + "DroneWatch Source Verification Report" + " " * 9 + "║")
        print(Fore.CYAN + "╠" + "=" * 58 + "╣")

        # Timestamp and duration
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(Fore.CYAN + "║" + f" Timestamp: {timestamp}" + " " * 20 + "║")

        # Summary stats with colors
        total = summary['total_sources']
        working = summary['working']
        failed = summary['failed']
        success_rate = summary['success_rate']

        print(Fore.CYAN + "╠" + "=" * 58 + "╣")
        print(Fore.CYAN + "║" + f" Total Sources:     {total}" + " " * (42 - len(str(total))) + "║")
        print(Fore.CYAN + "║" + Fore.GREEN + f" ✅ Working:         {working} ({success_rate:.1f}%)" + " " * (42 - len(f"{working} ({success_rate:.1f}%)")) + Fore.CYAN + "║")
        print(Fore.CYAN + "║" + Fore.RED + f" ❌ Failed:          {failed} ({100 - success_rate:.1f}%)" + " " * (42 - len(f"{failed} ({100 - success_rate:.1f}%)")) + Fore.CYAN + "║")

        # Alert level indicator
        if alert_level == AlertLevel.CRITICAL:
            alert_color = Fore.RED + Back.WHITE
            alert_emoji = "🚨"
        elif alert_level == AlertLevel.WARNING:
            alert_color = Fore.YELLOW
            alert_emoji = "⚠️"
        else:
            alert_color = Fore.GREEN
            alert_emoji = "✅"

        print(Fore.CYAN + "║" + alert_color + f" Status: {alert_emoji} {alert_level}" + Style.RESET_ALL + " " * (47 - len(alert_level)) + Fore.CYAN + "║")

        # Performance metrics
        avg_time = summary['average_response_time']
        print(Fore.CYAN + "╠" + "=" * 58 + "╣")
        print(Fore.CYAN + "║" + f" Performance:" + " " * 45 + "║")
        print(Fore.CYAN + "║" + f"   Average Response Time: {avg_time:.2f}s" + " " * (33 - len(f"{avg_time:.2f}s")) + "║")

        # Fastest sources
        if summary['fastest_sources']:
            fastest = summary['fastest_sources'][0]
            print(Fore.CYAN + "║" + f"   Fastest: {fastest['name'][:20]} ({fastest['time']:.2f}s)" + " " * (32 - len(fastest['name'][:20]) - len(f"{fastest['time']:.2f}s")) + "║")

        # Slowest sources
        if summary['slowest_sources']:
            slowest = summary['slowest_sources'][0]
            print(Fore.CYAN + "║" + f"   Slowest: {slowest['name'][:20]} ({slowest['time']:.2f}s)" + " " * (32 - len(slowest['name'][:20]) - len(f"{slowest['time']:.2f}s")) + "║")

        print(Fore.CYAN + "╚" + "=" * 58 + "╝")
        print()

        # Failed sources detail
        failed_results = [r for r in results if not r.success]
        if failed_results:
            print(Fore.RED + "Failed Sources:")
            print(Fore.RED + "-" * 60)
            for i, result in enumerate(failed_results[:10], 1):  # Show first 10
                print(Fore.RED + f"  {i}. {result.source_name}")
                print(Fore.RED + f"     URL: {result.url[:50]}...")
                print(Fore.RED + f"     Error: {result.error_message}")
                print()

            if len(failed_results) > 10:
                print(Fore.RED + f"  ... and {len(failed_results) - 10} more failures")
            print()

        # Degraded sources
        if summary['degraded_sources']:
            print(Fore.YELLOW + "Degraded Sources (slow but working):")
            print(Fore.YELLOW + "-" * 60)
            for source in summary['degraded_sources'][:5]:
                print(Fore.YELLOW + f"  • {source['name']} ({source['time']:.2f}s)")
            print()

        # Recommendations
        if failed_results:
            print(Fore.CYAN + "Recommendations:")
            print(Fore.CYAN + "-" * 60)
            for i, result in enumerate(failed_results[:3], 1):
                if result.http_status == 404:
                    print(Fore.CYAN + f"  • {result.source_name}: Update RSS URL in config.py")
                elif result.http_status == 403:
                    print(Fore.CYAN + f"  • {result.source_name}: Check User-Agent or contact source")
                elif "Timeout" in str(result.error_message):
                    print(Fore.CYAN + f"  • {result.source_name}: Increase timeout or check network")
                elif "parse" in str(result.error_message).lower():
                    print(Fore.CYAN + f"  • {result.source_name}: Validate RSS XML format")
                else:
                    print(Fore.CYAN + f"  • {result.source_name}: Investigate error - {result.error_message}")
            print()

    def write_log_file(self, results: List, summary: Dict, alert_level: str):
        """
        Write verification results to log file

        Args:
            results: List of VerificationResult objects
            summary: Summary statistics dict
            alert_level: Alert level
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, "source_verification.log")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"DroneWatch Source Verification - {timestamp}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Alert Level: {alert_level}\n")
            f.write(f"Total Sources: {summary['total_sources']}\n")
            f.write(f"Working: {summary['working']} ({summary['success_rate']:.1f}%)\n")
            f.write(f"Failed: {summary['failed']} ({100 - summary['success_rate']:.1f}%)\n")
            f.write(f"Average Response Time: {summary['average_response_time']:.2f}s\n")
            f.write("\n")

            # Failed sources
            failed_results = [r for r in results if not r.success]
            if failed_results:
                f.write("FAILED SOURCES:\n")
                f.write("-" * 80 + "\n")
                for i, result in enumerate(failed_results, 1):
                    f.write(f"{i}. {result.source_name}\n")
                    f.write(f"   URL: {result.url}\n")
                    f.write(f"   HTTP Status: {result.http_status}\n")
                    f.write(f"   Error: {result.error_message}\n")
                    f.write(f"   Response Time: {result.response_time:.2f}s\n")
                    f.write("\n")

    def generate_markdown_report(self, results: List, summary: Dict, alert_level: str) -> str:
        """
        Generate detailed markdown report

        Args:
            results: List of VerificationResult objects
            summary: Summary statistics dict
            alert_level: Alert level

        Returns:
            Path to generated markdown file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.log_dir, f"verification_report_{timestamp}.md")

        with open(report_file, "w", encoding="utf-8") as f:
            # Header
            f.write("# DroneWatch Source Verification Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"**Status**: {alert_level}\n\n")
            f.write("---\n\n")

            # Summary table
            f.write("## Summary\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Total Sources | {summary['total_sources']} |\n")
            f.write(f"| ✅ Working | {summary['working']} ({summary['success_rate']:.1f}%) |\n")
            f.write(f"| ❌ Failed | {summary['failed']} ({100 - summary['success_rate']:.1f}%) |\n")
            f.write(f"| Average Response Time | {summary['average_response_time']:.2f}s |\n")
            f.write("\n---\n\n")

            # Failed sources
            failed_results = [r for r in results if not r.success]
            if failed_results:
                f.write("## Failed Sources\n\n")
                for i, result in enumerate(failed_results, 1):
                    f.write(f"### {i}. {result.source_name}\n\n")
                    f.write(f"- **URL**: {result.url}\n")
                    f.write(f"- **HTTP Status**: {result.http_status}\n")
                    f.write(f"- **Error**: {result.error_message}\n")
                    f.write(f"- **Response Time**: {result.response_time:.2f}s\n")
                    f.write("\n")

                    # Recommended action
                    if result.http_status == 404:
                        f.write("**Recommended Action**: Update RSS URL in `config.py` or remove source\n\n")
                    elif result.http_status == 403:
                        f.write("**Recommended Action**: Check User-Agent header or contact source\n\n")
                    elif "Timeout" in str(result.error_message):
                        f.write("**Recommended Action**: Increase timeout or check network connectivity\n\n")
                    elif "parse" in str(result.error_message).lower():
                        f.write("**Recommended Action**: Validate RSS XML format\n\n")

                f.write("---\n\n")

            # Degraded sources
            if summary['degraded_sources']:
                f.write("## Degraded Sources\n\n")
                f.write("These sources are working but responding slowly (>5 seconds):\n\n")
                f.write("| Source | Response Time | URL |\n")
                f.write("|--------|---------------|-----|\n")
                for source in summary['degraded_sources']:
                    f.write(f"| {source['name']} | {source['time']:.2f}s | {source['url'][:50]}... |\n")
                f.write("\n---\n\n")

            # Performance breakdown
            f.write("## Performance Breakdown\n\n")
            f.write("**Fastest Sources**:\n")
            for i, source in enumerate(summary['fastest_sources'], 1):
                f.write(f"{i}. {source['name']} ({source['time']:.2f}s)\n")
            f.write("\n")

            f.write("**Slowest Sources**:\n")
            for i, source in enumerate(summary['slowest_sources'], 1):
                f.write(f"{i}. {source['name']} ({source['time']:.2f}s)\n")
            f.write("\n")

            f.write("---\n\n")
            f.write("**Generated by**: DroneWatch Source Verification System v1.0\n")

        return report_file

    def send_alerts(self, results: List, summary: Dict):
        """
        Send alerts via all configured channels

        Args:
            results: List of VerificationResult objects
            summary: Summary statistics dict
        """
        alert_level = self.determine_alert_level(summary['failed'])

        # Always output to console
        self.console_output(results, summary, alert_level)

        # Always write to log file
        self.write_log_file(results, summary, alert_level)

        # Generate markdown report for WARNING and CRITICAL
        if alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            report_path = self.generate_markdown_report(results, summary, alert_level)
            print(Fore.CYAN + f"📄 Markdown report generated: {report_path}")
            print()

        # TODO: Email integration (optional)
        # TODO: Slack integration (optional)
