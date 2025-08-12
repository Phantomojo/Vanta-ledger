#!/usr/bin/env python3
"""
System Analysis Service
Uses GitHub Models to analyze system health, code quality, and operational metrics
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

try:
    from .github_models_service import github_models_service

    GITHUB_MODELS_AVAILABLE = True
except ImportError:
    GITHUB_MODELS_AVAILABLE = False
    logging.warning("GitHub Models service not available")

logger = logging.getLogger(__name__)


class SystemAnalysisService:
    """
    Advanced system analysis using AI for health monitoring, code review, and operational insights
    """

    def __init__(self):
        self.enabled = GITHUB_MODELS_AVAILABLE and github_models_service.enabled
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        if self.enabled:
            logger.info("System Analysis Service initialized with GitHub Models")
        else:
            logger.warning(
                "System Analysis Service disabled - GitHub Models not available"
            )

    async def analyze_system_health(
        self, include_logs: bool = True, log_lines: int = 1000
    ) -> Dict[str, Any]:
        """Analyze overall system health using AI"""
        if not self.enabled:
            return {"error": "System analysis service not available"}

        try:
            # Collect system metrics
            metrics_data = self._collect_system_metrics()

            # Collect recent logs
            recent_logs = ""
            error_logs = ""

            if include_logs:
                recent_logs = self._collect_recent_logs(log_lines)
                error_logs = self._collect_error_logs(log_lines // 2)

            # Prepare data for AI analysis
            variables = {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": os.environ.get("ENVIRONMENT", "unknown"),
                "metrics_data": json.dumps(metrics_data, indent=2),
                "recent_logs": recent_logs,
                "error_logs": error_logs if error_logs else None,
            }

            # Use the system health analyzer prompt
            messages = github_models_service._render_prompt_template(
                "system_health_analyzer", variables
            )

            # Get model parameters from template
            template = github_models_service.prompts.get("system_health_analyzer", {})
            model = template.get("model", github_models_service.default_model)
            model_params = template.get("modelParameters", {})

            response = await github_models_service._make_request(
                messages, model=model, **model_params
            )

            # Parse AI response
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response[json_start:json_end]
                    analysis = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No JSON found", response, 0)

                # Add metadata
                analysis["analysis_metadata"] = {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "model_used": model,
                    "template_used": "system_health_analyzer",
                    "raw_metrics": metrics_data,
                    "logs_analyzed": include_logs,
                }

                return analysis

            except json.JSONDecodeError:
                return {
                    "system_status": "unknown",
                    "raw_analysis": response,
                    "analysis_metadata": {
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "error": "Failed to parse AI response",
                        "template_used": "system_health_analyzer",
                    },
                }

        except Exception as e:
            logger.error(f"System health analysis failed: {e}")
            return {
                "error": str(e),
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "error": True,
                },
            }

    async def analyze_code_quality(
        self, file_path: str, context: str = None
    ) -> Dict[str, Any]:
        """Analyze code quality and security using AI"""
        if not self.enabled:
            return {"error": "System analysis service not available"}

        try:
            # Read the code file
            code_path = Path(file_path)
            if not code_path.exists():
                return {"error": f"File not found: {file_path}"}

            with open(code_path, "r", encoding="utf-8") as f:
                code_content = f.read()

            # Determine language from file extension
            language_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
                ".go": "go",
                ".rs": "rust",
                ".rb": "ruby",
                ".php": "php",
            }

            language = language_map.get(code_path.suffix.lower(), "text")

            # Prepare variables for AI analysis
            variables = {
                "filename": code_path.name,
                "language": language,
                "context": context or f"Code analysis for {code_path.name}",
                "code_content": code_content,
            }

            # Use the code reviewer prompt
            messages = github_models_service._render_prompt_template(
                "code_reviewer", variables
            )

            # Get model parameters from template
            template = github_models_service.prompts.get("code_reviewer", {})
            model = template.get("model", github_models_service.default_model)
            model_params = template.get("modelParameters", {})

            response = await github_models_service._make_request(
                messages, model=model, **model_params
            )

            # Parse AI response
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response[json_start:json_end]
                    analysis = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No JSON found", response, 0)

                # Add metadata
                analysis["analysis_metadata"] = {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "model_used": model,
                    "template_used": "code_reviewer",
                    "file_analyzed": str(code_path),
                    "language_detected": language,
                    "file_size_bytes": len(code_content),
                    "lines_of_code": len(code_content.split("\n")),
                }

                return analysis

            except json.JSONDecodeError:
                return {
                    "overall_quality": "unknown",
                    "raw_analysis": response,
                    "analysis_metadata": {
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "error": "Failed to parse AI response",
                        "template_used": "code_reviewer",
                        "file_analyzed": str(code_path),
                    },
                }

        except Exception as e:
            logger.error(f"Code quality analysis failed for {file_path}: {e}")
            return {
                "error": str(e),
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "error": True,
                    "file_analyzed": file_path,
                },
            }

    async def analyze_project_codebase(
        self,
        project_dir: str = ".",
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> Dict[str, Any]:
        """Analyze entire codebase for quality and security issues"""
        if not self.enabled:
            return {"error": "System analysis service not available"}

        include_patterns = include_patterns or ["*.py", "*.js", "*.ts", "*.java"]
        exclude_patterns = exclude_patterns or [
            "__pycache__",
            "node_modules",
            ".git",
            "*.pyc",
            "venv",
            ".venv",
        ]

        try:
            project_path = Path(project_dir)
            code_files = []

            # Find code files to analyze
            for pattern in include_patterns:
                for file_path in project_path.rglob(pattern):
                    # Check if file should be excluded
                    if any(exclude in str(file_path) for exclude in exclude_patterns):
                        continue

                    if (
                        file_path.is_file() and file_path.stat().st_size < 100000
                    ):  # Limit to files < 100KB
                        code_files.append(file_path)

            # Limit number of files to analyze (to prevent API limits)
            code_files = code_files[:10]

            analysis_results = []
            overall_issues = {
                "critical_security": 0,
                "high_security": 0,
                "code_quality": 0,
                "performance": 0,
            }

            # Analyze each file
            for file_path in code_files:
                try:
                    file_analysis = await self.analyze_code_quality(
                        str(file_path),
                        f"Security and quality analysis for {project_path.name} project",
                    )

                    analysis_results.append(
                        {
                            "file": str(file_path.relative_to(project_path)),
                            "analysis": file_analysis,
                        }
                    )

                    # Count issues
                    if "security_issues" in file_analysis:
                        for issue in file_analysis["security_issues"]:
                            severity = issue.get("severity", "low")
                            if severity == "critical":
                                overall_issues["critical_security"] += 1
                            elif severity == "high":
                                overall_issues["high_security"] += 1

                    if "code_quality_issues" in file_analysis:
                        overall_issues["code_quality"] += len(
                            file_analysis["code_quality_issues"]
                        )

                    if "performance_issues" in file_analysis:
                        overall_issues["performance"] += len(
                            file_analysis["performance_issues"]
                        )

                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
                    analysis_results.append(
                        {
                            "file": str(file_path.relative_to(project_path)),
                            "error": str(e),
                        }
                    )

            # Generate summary
            total_files = len(analysis_results)
            successful_analyses = len([r for r in analysis_results if "analysis" in r])

            return {
                "project_summary": {
                    "project_directory": str(project_path),
                    "total_files_analyzed": total_files,
                    "successful_analyses": successful_analyses,
                    "failed_analyses": total_files - successful_analyses,
                    "overall_issues": overall_issues,
                },
                "file_analyses": analysis_results,
                "recommendations": self._generate_project_recommendations(
                    overall_issues
                ),
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "include_patterns": include_patterns,
                    "exclude_patterns": exclude_patterns,
                    "files_scanned": len(code_files),
                },
            }

        except Exception as e:
            logger.error(f"Project codebase analysis failed: {e}")
            return {
                "error": str(e),
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "error": True,
                },
            }

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Network (if available)
            network = psutil.net_io_counters()

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_memory_mb": process_memory.rss / (1024**2),
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.warning(f"Failed to collect some system metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def _collect_recent_logs(self, max_lines: int = 1000) -> str:
        """Collect recent application logs"""
        try:
            log_files = list(self.log_dir.glob("*.log"))
            if not log_files:
                return "No log files found"

            # Get the most recent log file
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)

            with open(latest_log, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Return last N lines
            recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            return "".join(recent_lines)

        except Exception as e:
            logger.warning(f"Failed to collect logs: {e}")
            return f"Error collecting logs: {str(e)}"

    def _collect_error_logs(self, max_lines: int = 500) -> str:
        """Collect recent error logs"""
        try:
            log_content = self._collect_recent_logs(max_lines * 2)

            # Filter for error lines
            error_lines = []
            for line in log_content.split("\n"):
                if any(
                    level in line.upper()
                    for level in ["ERROR", "CRITICAL", "EXCEPTION", "TRACEBACK"]
                ):
                    error_lines.append(line)

                if len(error_lines) >= max_lines:
                    break

            return "\n".join(error_lines)

        except Exception as e:
            logger.warning(f"Failed to collect error logs: {e}")
            return f"Error collecting error logs: {str(e)}"

    def _generate_project_recommendations(
        self, issues: Dict[str, int]
    ) -> List[Dict[str, str]]:
        """Generate recommendations based on identified issues"""
        recommendations = []

        if issues["critical_security"] > 0:
            recommendations.append(
                {
                    "priority": "immediate",
                    "category": "security",
                    "action": f"Address {issues['critical_security']} critical security vulnerabilities immediately",
                    "timeline": "immediate",
                }
            )

        if issues["high_security"] > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "security",
                    "action": f"Fix {issues['high_security']} high-severity security issues within 24 hours",
                    "timeline": "24h",
                }
            )

        if issues["code_quality"] > 5:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "maintainability",
                    "action": f"Improve code quality to address {issues['code_quality']} identified issues",
                    "timeline": "weekly",
                }
            )

        if issues["performance"] > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "performance",
                    "action": f"Optimize performance to resolve {issues['performance']} performance concerns",
                    "timeline": "monthly",
                }
            )

        if not any(issues.values()):
            recommendations.append(
                {
                    "priority": "low",
                    "category": "maintenance",
                    "action": "Codebase appears healthy. Continue regular monitoring and reviews.",
                    "timeline": "ongoing",
                }
            )

        return recommendations


# Global service instance
system_analysis_service = SystemAnalysisService()
