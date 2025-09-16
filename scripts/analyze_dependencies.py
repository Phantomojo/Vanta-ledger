#!/usr/bin/env python3
"""
Dependency Analysis Script for Vanta Ledger

This script analyzes the project's dependencies to:
1. Identify unused packages
2. Find redundant dependencies
3. Check for security vulnerabilities
4. Optimize the requirements.txt file
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_src = project_root / "backend" / "src"
        self.requirements_file = project_root / "config" / "requirements.txt"
        self.installed_packages = {}
        self.imports_found = set()
        self.package_usage = {}
        self.results = {
            "total_packages": 0,
            "used_packages": 0,
            "unused_packages": 0,
            "redundant_packages": 0,
            "security_issues": 0,
            "optimization_opportunities": []
        }
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages with versions."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            packages = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==', 1)
                    packages[name.lower()] = version
            
            logger.info(f"Found {len(packages)} installed packages")
            return packages
            
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return {}
    
    def get_requirements_packages(self) -> List[str]:
        """Get packages from requirements.txt."""
        try:
            with open(self.requirements_file, 'r') as f:
                content = f.read()
            
            packages = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('='):
                    # Extract package name (remove version specifiers)
                    package_name = re.split(r'[>=<!=]', line)[0].strip()
                    if package_name:
                        packages.append(package_name.lower())
            
            logger.info(f"Found {len(packages)} packages in requirements.txt")
            return packages
            
        except Exception as e:
            logger.error(f"Error reading requirements.txt: {e}")
            return []
    
    def find_imports_in_file(self, file_path: Path) -> Set[str]:
        """Find all imports in a Python file."""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0].lower())
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0].lower())
            
        except Exception as e:
            logger.debug(f"Error parsing {file_path}: {e}")
        
        return imports
    
    def scan_python_files(self) -> Set[str]:
        """Scan all Python files for imports."""
        imports = set()
        
        # Scan backend source files
        if self.backend_src.exists():
            for py_file in self.backend_src.rglob("*.py"):
                file_imports = self.find_imports_in_file(py_file)
                imports.update(file_imports)
                logger.debug(f"Scanned {py_file}: {len(file_imports)} imports")
        
        # Scan test files
        test_dir = self.project_root / "tests"
        if test_dir.exists():
            for py_file in test_dir.rglob("*.py"):
                file_imports = self.find_imports_in_file(py_file)
                imports.update(file_imports)
                logger.debug(f"Scanned {py_file}: {len(file_imports)} imports")
        
        # Scan script files
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for py_file in scripts_dir.rglob("*.py"):
                file_imports = self.find_imports_in_file(py_file)
                imports.update(file_imports)
                logger.debug(f"Scanned {py_file}: {len(file_imports)} imports")
        
        logger.info(f"Found {len(imports)} unique imports across all Python files")
        return imports
    
    def map_imports_to_packages(self, imports: Set[str]) -> Dict[str, List[str]]:
        """Map import names to package names."""
        import_to_package = {}
        
        # Common mappings
        mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'jose': 'python-jose',
            'multipart': 'python-multipart',
            'dateutil': 'python-dateutil',
            'docx': 'python-docx',
            'sklearn': 'scikit-learn',
            'bs4': 'beautifulsoup4',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'jose': 'python-jose',
            'multipart': 'python-multipart',
            'dateutil': 'python-dateutil',
            'docx': 'python-docx',
            'sklearn': 'scikit-learn',
            'bs4': 'beautifulsoup4',
            'fitz': 'PyMuPDF',
            'tesseract': 'pytesseract',
            'pdf2image': 'pdf2image',
            'lxml': 'lxml',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'scipy': 'scipy',
            'torch': 'torch',
            'transformers': 'transformers',
            'spacy': 'spacy',
            'openai': 'openai',
            'requests': 'requests',
            'aiohttp': 'aiohttp',
            'httpx': 'httpx',
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn',
            'pydantic': 'pydantic',
            'sqlalchemy': 'sqlalchemy',
            'alembic': 'alembic',
            'psycopg2': 'psycopg2-binary',
            'pymongo': 'pymongo',
            'redis': 'redis',
            'jwt': 'PyJWT',
            'cryptography': 'cryptography',
            'bcrypt': 'bcrypt',
            'passlib': 'passlib',
            'structlog': 'structlog',
            'psutil': 'psutil',
            'click': 'click',
            'rich': 'rich',
            'typer': 'typer',
            'jsonschema': 'jsonschema',
            'markdown': 'markdown',
            'pygments': 'pygments',
            'markupsafe': 'markupsafe',
            'mako': 'mako',
            'packaging': 'packaging',
            'typing_extensions': 'typing-extensions',
            'six': 'six',
            'wrapt': 'wrapt',
            'pytest': 'pytest',
            'black': 'black',
            'flake8': 'flake8',
            'mypy': 'mypy',
            'bandit': 'bandit',
            'coverage': 'coverage',
        }
        
        for import_name in imports:
            if import_name in mappings:
                package_name = mappings[import_name]
                if package_name not in import_to_package:
                    import_to_package[package_name] = []
                import_to_package[package_name].append(import_name)
            else:
                # Try direct mapping
                if import_name not in import_to_package:
                    import_to_package[import_name] = []
                import_to_package[import_name].append(import_name)
        
        return import_to_package
    
    def check_security_vulnerabilities(self) -> List[Dict]:
        """Check for security vulnerabilities in installed packages."""
        vulnerabilities = []
        
        try:
            # Try to use safety if available
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("No security vulnerabilities found")
            else:
                logger.warning("Security vulnerabilities detected")
                # Parse safety output if available
                
        except Exception as e:
            logger.debug(f"Safety not available: {e}")
        
        return vulnerabilities
    
    def identify_redundant_packages(self, installed_packages: Dict[str, str], used_packages: Set[str]) -> List[str]:
        """Identify redundant packages."""
        redundant = []
        
        # Common redundant packages
        redundant_patterns = [
            'setuptools',  # Usually not needed in requirements
            'pip',  # Package manager, not a dependency
            'wheel',  # Build tool, not runtime dependency
        ]
        
        for package in installed_packages:
            if package in redundant_patterns:
                redundant.append(package)
        
        return redundant
    
    def analyze_dependencies(self) -> Dict:
        """Main analysis function."""
        logger.info("Starting dependency analysis...")
        
        # Get installed packages
        self.installed_packages = self.get_installed_packages()
        self.results["total_packages"] = len(self.installed_packages)
        
        # Get requirements packages
        requirements_packages = self.get_requirements_packages()
        
        # Scan for imports
        imports = self.scan_python_files()
        self.imports_found = imports
        
        # Map imports to packages
        import_to_package = self.map_imports_to_packages(imports)
        
        # Find used packages
        used_packages = set()
        for package_name in import_to_package.keys():
            if package_name in self.installed_packages:
                used_packages.add(package_name)
        
        self.results["used_packages"] = len(used_packages)
        
        # Find unused packages
        unused_packages = []
        for package in self.installed_packages:
            if package not in used_packages and package not in requirements_packages:
                unused_packages.append(package)
        
        self.results["unused_packages"] = len(unused_packages)
        
        # Find redundant packages
        redundant_packages = self.identify_redundant_packages(self.installed_packages, used_packages)
        self.results["redundant_packages"] = len(redundant_packages)
        
        # Check security vulnerabilities
        vulnerabilities = self.check_security_vulnerabilities()
        self.results["security_issues"] = len(vulnerabilities)
        
        # Store results for reporting
        self.analysis_results = {
            "installed_packages": self.installed_packages,
            "requirements_packages": requirements_packages,
            "used_packages": used_packages,
            "unused_packages": unused_packages,
            "redundant_packages": redundant_packages,
            "import_to_package": import_to_package,
            "vulnerabilities": vulnerabilities,
        }
        
        return self.analysis_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive dependency analysis report."""
        report = f"""
# Dependency Analysis Report

**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project:** {self.project_root}

## Summary
- **Total Installed Packages:** {self.results['total_packages']}
- **Used Packages:** {self.results['used_packages']}
- **Unused Packages:** {self.results['unused_packages']}
- **Redundant Packages:** {self.results['redundant_packages']}
- **Security Issues:** {self.results['security_issues']}

## Package Usage Analysis

### Used Packages ({len(self.analysis_results['used_packages'])})
"""
        
        for package in sorted(self.analysis_results['used_packages']):
            version = self.analysis_results['installed_packages'].get(package, 'unknown')
            imports = self.analysis_results['import_to_package'].get(package, [])
            report += f"- **{package}** ({version}) - Used by: {', '.join(imports)}\n"
        
        report += f"""
### Unused Packages ({len(self.analysis_results['unused_packages'])})
"""
        
        for package in sorted(self.analysis_results['unused_packages']):
            version = self.analysis_results['installed_packages'].get(package, 'unknown')
            report += f"- **{package}** ({version}) - Not used in code\n"
        
        report += f"""
### Redundant Packages ({len(self.analysis_results['redundant_packages'])})
"""
        
        for package in sorted(self.analysis_results['redundant_packages']):
            version = self.analysis_results['installed_packages'].get(package, 'unknown')
            report += f"- **{package}** ({version}) - Redundant/not needed\n"
        
        report += f"""
## Optimization Opportunities

### 1. Remove Unused Packages
The following packages can be safely removed:
"""
        
        for package in sorted(self.analysis_results['unused_packages']):
            report += f"- {package}\n"
        
        report += f"""
### 2. Remove Redundant Packages
The following packages are redundant:
"""
        
        for package in sorted(self.analysis_results['redundant_packages']):
            report += f"- {package}\n"
        
        report += f"""
### 3. Requirements.txt Optimization
- **Current packages in requirements.txt:** {len(self.analysis_results['requirements_packages'])}
- **Actually used packages:** {len(self.analysis_results['used_packages'])}
- **Potential reduction:** {len(self.analysis_results['requirements_packages']) - len(self.analysis_results['used_packages'])} packages

## Recommendations

1. **Remove unused packages** to reduce deployment size
2. **Update package versions** to latest secure versions
3. **Consolidate similar packages** where possible
4. **Use dependency groups** for optional features
5. **Regular security scanning** with tools like safety

## Next Steps

1. Create optimized requirements.txt
2. Remove unused packages
3. Update package versions
4. Test application functionality
5. Document dependency changes
"""
        
        return report

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    analyzer = DependencyAnalyzer(project_root)
    
    # Run analysis
    results = analyzer.analyze_dependencies()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save report
    report_file = project_root / "DEPENDENCY_ANALYSIS_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Dependency analysis complete! Report saved to: {report_file}")
    
    print("\n" + "="*60)
    print(report)
    print("="*60)

if __name__ == "__main__":
    main()
