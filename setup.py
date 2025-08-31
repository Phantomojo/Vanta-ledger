"""
Setup script for Vanta Ledger.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("config/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vanta-ledger",
    version="1.0.0",
    author="Vanta Ledger Team",
    author_email="team@vantaledger.com",
    description="AI-Powered Financial Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phantomojo/Vanta-ledger",
    packages=find_packages(where="backend/src"),
    package_dir={"": "backend/src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vanta-ledger=vanta_ledger.main:main",
        ],
    },
)
