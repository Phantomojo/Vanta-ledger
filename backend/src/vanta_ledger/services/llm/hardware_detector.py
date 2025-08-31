#!/usr/bin/env python3
"""
Hardware Detector for Local LLM Service
Optimized for RTX 3050 GPU with automatic hardware adaptation
"""

import logging
import os
from typing import Any, Dict, Optional

import psutil

logger = logging.getLogger(__name__)

try:
    import os
    import sys

    # Add the correct path to site-packages
    venv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "venv",
        "lib",
        "python3.12",
        "site-packages",
    )
    sys.path.append(venv_path)
    from GPUtil import getGPUs

    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.warning("GPUtil not available - GPU detection disabled")

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")


class HardwareDetector:
    """Detect and configure hardware for optimal LLM performance"""

    def __init__(self):
        self.gpu_info = None
        self.cpu_info = None
        self.memory_info = None
        self.detected_hardware = {}

    def detect_hardware(self) -> Dict[str, Any]:
        """Detect available hardware and configure optimal settings"""
        try:
            logger.info("Starting hardware detection...")

            # Detect GPU
            self._detect_gpu()

            # Detect CPU
            self._detect_cpu()

            # Detect Memory
            self._detect_memory()

            # Configure optimal settings
            self._configure_optimal_settings()

            logger.info(
                f"Hardware detection completed: {self.detected_hardware['performance_profile']}"
            )
            return self.detected_hardware

        except Exception as e:
            logger.error(f"Error detecting hardware: {str(e)}")
            return self._get_fallback_config()

    def _detect_gpu(self):
        """Detect NVIDIA GPU"""
        try:
            if not GPUTIL_AVAILABLE:
                logger.warning("GPUtil not available, skipping GPU detection")
                return

            gpus = getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                self.gpu_info = {
                    "name": gpu.name,
                    "memory_total": gpu.memoryTotal,
                    "memory_free": gpu.memoryFree,
                    "memory_used": gpu.memoryUsed,
                    "temperature": gpu.temperature,
                    "load": gpu.load * 100 if gpu.load else 0,
                }

                # RTX 3050 specific optimizations
                if "RTX 3050" in gpu.name:
                    logger.info("RTX 3050 detected - applying optimized settings")
                    self.gpu_info["optimizations"] = {
                        "max_batch_size": 4,  # Conservative for 4GB VRAM
                        "model_quantization": "Q4_K_M",  # Good balance for RTX 3050
                        "context_length": 2048,  # Reduced for memory efficiency
                        "use_gpu_layers": 20,  # Use GPU for transformer layers
                        "tensor_split": [0.8, 0.2],  # 80% GPU, 20% CPU
                        "rope_scaling": {"type": "linear", "factor": 1.0},
                    }
                elif "RTX" in gpu.name:
                    # Other RTX cards
                    logger.info(f"RTX GPU detected: {gpu.name}")
                    self.gpu_info["optimizations"] = {
                        "max_batch_size": 6,
                        "model_quantization": "Q4_K_M",
                        "context_length": 3072,
                        "use_gpu_layers": 25,
                        "tensor_split": [0.9, 0.1],
                    }
                else:
                    # Generic GPU settings
                    logger.info(f"Generic GPU detected: {gpu.name}")
                    self.gpu_info["optimizations"] = {
                        "max_batch_size": 2,
                        "model_quantization": "Q4_K_M",
                        "context_length": 1024,
                        "use_gpu_layers": 10,
                        "tensor_split": [0.6, 0.4],
                    }

        except Exception as e:
            logger.warning(f"GPU detection failed: {str(e)}")
            self.gpu_info = None

    def _detect_cpu(self):
        """Detect CPU capabilities"""
        try:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()

            self.cpu_info = {
                "cores": cpu_count,
                "frequency": cpu_freq.current if cpu_freq else 0,
                "architecture": os.uname().machine,
                "optimizations": {
                    "threads": min(cpu_count, 8),  # Limit threads for stability
                    "batch_size": 1,  # CPU-only batch size
                    "model_quantization": "Q4_K_M",
                },
            }

            logger.info(
                f"CPU detected: {cpu_count} cores, {cpu_freq.current if cpu_freq else 'unknown'} MHz"
            )

        except Exception as e:
            logger.warning(f"CPU detection failed: {str(e)}")
            self.cpu_info = {"cores": 4, "optimizations": {"threads": 4}}

    def _detect_memory(self):
        """Detect system memory"""
        try:
            memory = psutil.virtual_memory()
            self.memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
            }

            total_gb = round(memory.total / (1024**3), 2)
            logger.info(f"Memory detected: {total_gb} GB total")

        except Exception as e:
            logger.warning(f"Memory detection failed: {str(e)}")
            self.memory_info = {"total": 8 * 1024**3, "available": 4 * 1024**3}

    def _configure_optimal_settings(self):
        """Configure optimal settings based on detected hardware"""
        self.detected_hardware = {
            "gpu": self.gpu_info,
            "cpu": self.cpu_info,
            "memory": self.memory_info,
            "recommended_models": self._get_recommended_models(),
            "performance_profile": self._get_performance_profile(),
        }

    def _get_recommended_models(self) -> Dict[str, Any]:
        """Get recommended models based on hardware"""
        if self.gpu_info and "RTX 3050" in self.gpu_info.get("name", ""):
            logger.info("Configuring models for RTX 3050")
            return {
                "primary": {
                    "name": "mistral_7b",
                    "quantization": "Q4_K_M",
                    "size_gb": 4.1,
                    "context_length": 2048,
                    "batch_size": 4,
                },
                "secondary": {
                    "name": "phi3_mini",
                    "quantization": "Q4_K_M",
                    "size_gb": 2.1,
                    "context_length": 4096,
                    "batch_size": 8,
                },
                "document_understanding": {
                    "name": "layoutlmv3_base",
                    "size_gb": 1.2,
                    "batch_size": 2,
                },
            }
        elif self.gpu_info:
            # Other GPU configuration
            logger.info("Configuring models for other GPU")
            return {
                "primary": {
                    "name": "mistral_7b",
                    "quantization": "Q4_K_M",
                    "size_gb": 4.1,
                    "context_length": 3072,
                    "batch_size": 6,
                },
                "secondary": {
                    "name": "phi3_mini",
                    "quantization": "Q4_K_M",
                    "size_gb": 2.1,
                    "context_length": 4096,
                    "batch_size": 8,
                },
            }
        else:
            # CPU-only configuration
            logger.info("Configuring models for CPU-only")
            return {
                "primary": {
                    "name": "phi3_mini",
                    "quantization": "Q4_K_M",
                    "size_gb": 2.1,
                    "context_length": 2048,
                    "batch_size": 1,
                },
                "secondary": {
                    "name": "tinyllama",
                    "quantization": "Q4_K_M",
                    "size_gb": 0.6,
                    "context_length": 1024,
                    "batch_size": 2,
                },
            }

    def _get_performance_profile(self) -> str:
        """Get performance profile based on hardware"""
        if self.gpu_info and "RTX 3050" in self.gpu_info.get("name", ""):
            return "rtx3050_optimized"
        elif self.gpu_info and self.gpu_info.get("memory_total", 0) >= 4000:
            return "high_performance"
        elif self.gpu_info:
            return "medium_performance"
        else:
            return "cpu_only"

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration"""
        logger.warning("Using fallback hardware configuration")
        return {
            "gpu": None,
            "cpu": {"cores": 4, "optimizations": {"threads": 4}},
            "memory": {"total": 8 * 1024**3, "available": 4 * 1024**3},
            "recommended_models": {
                "primary": {
                    "name": "tinyllama",
                    "quantization": "Q4_K_M",
                    "size_gb": 0.6,
                    "context_length": 1024,
                    "batch_size": 1,
                }
            },
            "performance_profile": "cpu_only",
        }

    def get_hardware_summary(self) -> str:
        """Get human-readable hardware summary"""
        summary_parts = []

        if self.gpu_info:
            summary_parts.append(
                f"GPU: {self.gpu_info['name']} ({self.gpu_info['memory_total']}MB)"
            )

        if self.cpu_info:
            summary_parts.append(f"CPU: {self.cpu_info['cores']} cores")

        if self.memory_info:
            total_gb = round(self.memory_info["total"] / (1024**3), 2)
            summary_parts.append(f"RAM: {total_gb}GB")

        summary_parts.append(
            f"Profile: {self.detected_hardware.get('performance_profile', 'unknown')}"
        )

        return " | ".join(summary_parts)
