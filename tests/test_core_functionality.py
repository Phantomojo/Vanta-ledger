#!/usr/bin/python3
"""
Core Functionality Testing Framework for Vanta Ledger
Tests essential system components without complex backend imports
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import GPUtil
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoreFunctionalityTestSuite:
    """Comprehensive core functionality testing suite"""

    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.system_info = {}

    def log_test_result(
        self, test_name: str, success: bool, details: str = "", data: Dict = None
    ):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "data": data,
            "timestamp": time.time(),
        }

    def test_system_environment(self) -> bool:
        """Test system environment and dependencies"""
        logger.info("🔧 Testing System Environment...")

        try:
            # Test Python version
            python_version = sys.version_info
            python_ok = python_version.major == 3 and python_version.minor >= 8

            # Test essential imports
            imports_ok = True
            import_errors = []

            try:
                import torch

                torch_version = torch.__version__
            except ImportError as e:
                imports_ok = False
                import_errors.append(f"torch: {e}")

            try:
                import transformers

                transformers_version = transformers.__version__
            except ImportError as e:
                imports_ok = False
                import_errors.append(f"transformers: {e}")

            try:
                import llama_cpp

                llama_ok = True
            except ImportError as e:
                imports_ok = False
                import_errors.append(f"llama_cpp: {e}")

            # Test system resources
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            self.system_info = {
                "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "torch_version": (
                    torch_version if "torch_version" in locals() else "Not installed"
                ),
                "transformers_version": (
                    transformers_version
                    if "transformers_version" in locals()
                    else "Not installed"
                ),
                "cpu_count": cpu_count,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }

            success = python_ok and imports_ok
            details = f"Python {self.system_info['python_version']}, CPU: {cpu_count}, RAM: {self.system_info['memory_total_gb']}GB"

            if not imports_ok:
                details += f", Import errors: {', '.join(import_errors)}"

            self.log_test_result(
                "System Environment", success, details, self.system_info
            )
            return success

        except Exception as e:
            self.log_test_result("System Environment", False, f"Error: {str(e)}")
            return False

    def test_hardware_detection(self) -> bool:
        """Test hardware detection capabilities"""
        logger.info("🖥️ Testing Hardware Detection...")

        try:
            # CPU detection
            cpu_info = {
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "frequency": (
                    psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"
                ),
            }

            # Memory detection
            memory_info = {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "percent_used": psutil.virtual_memory().percent,
            }

            # GPU detection
            gpu_info = {}
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_info = {
                        "count": len(gpus),
                        "names": [gpu.name for gpu in gpus],
                        "memory_total": [gpu.memoryTotal for gpu in gpus],
                        "memory_free": [gpu.memoryFree for gpu in gpus],
                    }
                else:
                    gpu_info = {"count": 0, "message": "No GPUs detected"}
            except Exception as e:
                gpu_info = {"error": str(e)}

            # Determine hardware profile
            if gpu_info.get("count", 0) > 0:
                gpu_names = gpu_info.get("names", [])
                if any("RTX" in name for name in gpu_names):
                    profile = "rtx_optimized"
                elif any("GTX" in name for name in gpu_names):
                    profile = "gtx_optimized"
                else:
                    profile = "gpu_optimized"
            else:
                profile = "cpu_only"

            hardware_info = {
                "cpu": cpu_info,
                "memory": memory_info,
                "gpu": gpu_info,
                "profile": profile,
            }

            success = cpu_info["count"] > 0 and memory_info["total_gb"] > 0
            details = f"CPU: {cpu_info['count']} cores, RAM: {memory_info['total_gb']}GB, GPU: {gpu_info.get('count', 0)}, Profile: {profile}"

            self.log_test_result("Hardware Detection", success, details, hardware_info)
            return success

        except Exception as e:
            self.log_test_result("Hardware Detection", False, f"Error: {str(e)}")
            return False

    def test_model_files(self) -> bool:
        """Test model file availability and integrity"""
        logger.info("🤖 Testing Model Files...")

        try:
            model_path = Path("models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

            # Check if model file exists
            exists = model_path.exists()

            if exists:
                # Get file size
                size_mb = model_path.stat().st_size / (1024**2)

                # Check if file is readable
                try:
                    with open(model_path, "rb") as f:
                        # Read first 1024 bytes to check if file is valid
                        header = f.read(1024)
                        readable = len(header) > 0
                except Exception:
                    readable = False

                success = (
                    exists and readable and size_mb > 100
                )  # Should be at least 100MB
                details = f"Model file: {size_mb:.1f}MB, Readable: {readable}"

                model_info = {
                    "path": str(model_path),
                    "size_mb": size_mb,
                    "readable": readable,
                    "exists": exists,
                }
            else:
                success = False
                details = "Model file not found"
                model_info = {"exists": False}

            self.log_test_result("Model Files", success, details, model_info)
            return success

        except Exception as e:
            self.log_test_result("Model Files", False, f"Error: {str(e)}")
            return False

    def test_llm_functionality(self) -> bool:
        """Test LLM loading and basic inference"""
        logger.info("🧠 Testing LLM Functionality...")

        try:
            import llama_cpp

            model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

            # Test model loading
            start_time = time.time()
            llm = llama_cpp.Llama(
                model_path=model_path, n_ctx=512, n_threads=2, verbose=False
            )
            load_time = time.time() - start_time

            # Test basic inference
            start_time = time.time()
            response = llm("Hello, how are you?", max_tokens=20, stop=["\n"])
            inference_time = time.time() - start_time

            # Check response quality
            response_text = (
                response["choices"][0]["text"]
                if "choices" in response
                else str(response)
            )
            response_ok = len(response_text.strip()) > 0

            success = response_ok and load_time < 30  # Should load in under 30 seconds
            details = f"Load time: {load_time:.2f}s, Inference time: {inference_time:.2f}s, Response: {response_text[:50]}..."

            llm_info = {
                "load_time_seconds": load_time,
                "inference_time_seconds": inference_time,
                "response_length": len(response_text),
                "response_preview": response_text[:100],
            }

            self.log_test_result("LLM Functionality", success, details, llm_info)
            return success

        except Exception as e:
            self.log_test_result("LLM Functionality", False, f"Error: {str(e)}")
            return False

    def test_database_connectivity(self) -> bool:
        """Test database connectivity without complex imports"""
        logger.info("🗄️ Testing Database Connectivity...")

        try:
            # Test PostgreSQL connection
            postgres_ok = False
            try:
                import psycopg2

                # Try to connect to PostgreSQL
                conn = psycopg2.connect(
                    host=os.getenv("POSTGRES_HOST", "localhost"),
                    port=os.getenv("POSTGRES_PORT", "5432"),
                    database=os.getenv("POSTGRES_DB", "vanta_ledger"),
                    user=os.getenv("POSTGRES_USER", "postgres"),
                    password=os.getenv("POSTGRES_PASSWORD", "password"),
                )
                conn.close()
                postgres_ok = True
            except Exception as e:
                postgres_error = str(e)

            # Test MongoDB connection
            mongo_ok = False
            try:
                import pymongo

                client = pymongo.MongoClient(
                    os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
                )
                db = client[os.getenv("MONGODB_DB", "vanta_ledger")]
                result = db.command("ping")
                client.close()
                mongo_ok = True
            except Exception as e:
                mongo_error = str(e)

            # Test Redis connection
            redis_ok = False
            try:
                import redis

                r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    db=int(os.getenv("REDIS_DB", "0")),
                )
                r.ping()
                r.close()
                redis_ok = True
            except Exception as e:
                redis_error = str(e)

            success = (
                postgres_ok or mongo_ok or redis_ok
            )  # At least one database should work
            details = (
                f"PostgreSQL: {postgres_ok}, MongoDB: {mongo_ok}, Redis: {redis_ok}"
            )

            db_info = {
                "postgresql": {
                    "connected": postgres_ok,
                    "error": postgres_error if not postgres_ok else None,
                },
                "mongodb": {
                    "connected": mongo_ok,
                    "error": mongo_error if not mongo_ok else None,
                },
                "redis": {
                    "connected": redis_ok,
                    "error": redis_error if not redis_ok else None,
                },
            }

            self.log_test_result("Database Connectivity", success, details, db_info)
            return success

        except Exception as e:
            self.log_test_result("Database Connectivity", False, f"Error: {str(e)}")
            return False

    def test_file_system(self) -> bool:
        """Test file system operations"""
        logger.info("📁 Testing File System...")

        try:
            # Test directory structure
            required_dirs = ["models", "backend", "tests", "docs"]
            dir_checks = {}

            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                dir_checks[dir_name] = {
                    "exists": dir_path.exists(),
                    "is_dir": dir_path.is_dir() if dir_path.exists() else False,
                }

            # Test file operations
            test_file = Path("test_file_system.tmp")
            write_ok = False
            read_ok = False

            try:
                # Test write
                test_file.write_text("test content")
                write_ok = True

                # Test read
                content = test_file.read_text()
                read_ok = content == "test content"

                # Cleanup
                test_file.unlink()
            except Exception as e:
                file_error = str(e)

            success = (
                all(check["exists"] for check in dir_checks.values())
                and write_ok
                and read_ok
            )
            details = f"Directories: {sum(check['exists'] for check in dir_checks.values())}/{len(required_dirs)}, File ops: Write={write_ok}, Read={read_ok}"

            fs_info = {
                "directories": dir_checks,
                "file_operations": {"write": write_ok, "read": read_ok},
            }

            self.log_test_result("File System", success, details, fs_info)
            return success

        except Exception as e:
            self.log_test_result("File System", False, f"Error: {str(e)}")
            return False

    def test_network_connectivity(self) -> bool:
        """Test network connectivity"""
        logger.info("🌐 Testing Network Connectivity...")

        try:
            import socket
            import urllib.request

            # Test internet connectivity
            internet_ok = False
            try:
                urllib.request.urlopen("http://www.google.com", timeout=5)
                internet_ok = True
            except Exception:
                pass

            # Test localhost connectivity
            localhost_ok = False
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(("localhost", 8500))  # Test backend port
                sock.close()
                localhost_ok = result == 0
            except Exception:
                pass

            # Test DNS resolution
            dns_ok = False
            try:
                socket.gethostbyname("localhost")
                dns_ok = True
            except Exception:
                pass

            success = internet_ok or localhost_ok  # At least one should work
            details = (
                f"Internet: {internet_ok}, Localhost: {localhost_ok}, DNS: {dns_ok}"
            )

            network_info = {
                "internet": internet_ok,
                "localhost": localhost_ok,
                "dns": dns_ok,
            }

            self.log_test_result("Network Connectivity", success, details, network_info)
            return success

        except Exception as e:
            self.log_test_result("Network Connectivity", False, f"Error: {str(e)}")
            return False

    def test_performance_metrics(self) -> bool:
        """Test system performance metrics"""
        logger.info("⚡ Testing Performance Metrics...")

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()

            # Network I/O
            network_io = psutil.net_io_counters()

            # Performance assessment
            cpu_ok = cpu_percent < 90  # CPU usage should be under 90%
            memory_ok = memory.percent < 95  # Memory usage should be under 95%

            success = cpu_ok and memory_ok
            details = f"CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%"

            perf_info = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_read_mb": (
                    round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0
                ),
                "disk_write_mb": (
                    round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
                ),
                "network_sent_mb": (
                    round(network_io.bytes_sent / (1024**2), 2) if network_io else 0
                ),
                "network_recv_mb": (
                    round(network_io.bytes_recv / (1024**2), 2) if network_io else 0
                ),
            }

            self.log_test_result("Performance Metrics", success, details, perf_info)
            return success

        except Exception as e:
            self.log_test_result("Performance Metrics", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all core functionality tests"""
        logger.info("🚀 Starting Core Functionality Tests...")
        logger.info("=" * 60)

        tests = [
            ("System Environment", self.test_system_environment),
            ("Hardware Detection", self.test_hardware_detection),
            ("Model Files", self.test_model_files),
            ("LLM Functionality", self.test_llm_functionality),
            ("Database Connectivity", self.test_database_connectivity),
            ("File System", self.test_file_system),
            ("Network Connectivity", self.test_network_connectivity),
            ("Performance Metrics", self.test_performance_metrics),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                success = test_func()
                results[test_name] = success
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False

        # Generate summary
        total_tests = len(results)
        passed_tests = sum(results.values())
        failed_tests = total_tests - passed_tests

        logger.info("=" * 60)
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"   Duration: {time.time() - self.start_time:.2f}s")

        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "duration": time.time() - self.start_time,
            },
            "results": results,
            "detailed_results": self.test_results,
            "system_info": self.system_info,
        }


def main():
    """Main test execution function"""
    print("🧪 Core Functionality Testing Suite")
    print("=" * 60)

    # Create test suite
    test_suite = CoreFunctionalityTestSuite()

    # Run all tests
    results = test_suite.run_all_tests()

    # Save results to file
    results_file = "test_core_functionality_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")

    # Return exit code based on results
    if results["summary"]["failed"] > 0:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == "__main__":
    exit(main())
