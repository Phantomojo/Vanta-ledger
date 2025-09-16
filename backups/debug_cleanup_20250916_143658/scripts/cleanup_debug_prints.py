#!/usr/bin/env python3
"""
Debug Print Cleanup Script for Vanta Ledger

This script systematically finds and replaces print() statements with proper logging.
It creates backups and provides detailed reporting.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DebugPrintCleaner:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "backups" / f"debug_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "files_processed": 0,
            "print_statements_found": 0,
            "print_statements_replaced": 0,
            "files_modified": 0,
            "errors": []
        }
        
        # Patterns to match different types of print statements
        self.print_patterns = [
            r'print\s*\(\s*["\'].*?["\']\s*\)',  # logger.info("string")
            r'print\s*\(\s*f["\'].*?["\']\s*\)',  # logger.info(f"string")
            r'print\s*\(\s*[^)]+\s*\)',  # logger.info(variable) or print(expression)
        ]
        
        # Files to exclude from processing
        self.exclude_patterns = [
            r'.*\.pyc$',
            r'.*__pycache__.*',
            r'.*\.venv.*',
            r'.*venv.*',
            r'.*node_modules.*',
            r'.*\.git.*',
            r'.*backups.*',
            r'.*\.log$',
            r'.*test_.*\.py$',  # Exclude test files for now
        ]
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing."""
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in self.exclude_patterns)
    
    def find_print_statements(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Find all print statements in a file."""
        print_statements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern in self.print_patterns:
                    if re.search(pattern, line):
                        # Extract the print statement
                        match = re.search(pattern, line)
                        if match:
                            print_statements.append((
                                line_num,
                                line.strip(),
                                match.group(0)
                            ))
                            break
                            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            self.results["errors"].append(f"Error reading {file_path}: {e}")
            
        return print_statements
    
    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create relative path structure in backup
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def replace_print_with_logging(self, file_path: Path, print_statements: List[Tuple[int, str, str]]) -> bool:
        """Replace print statements with proper logging."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if logging is already imported
            has_logging_import = 'import logging' in content or 'from logging import' in content
            
            # Replace print statements
            replacements_made = 0
            for line_num, original_line, print_statement in print_statements:
                # Determine log level based on content
                log_level = self.determine_log_level(print_statement)
                
                # Create replacement
                if 'f"' in print_statement or "f'" in print_statement:
                    # Handle f-strings
                    content_between_quotes = re.search(r'f["\'](.*?)["\']', print_statement)
                    if content_between_quotes:
                        log_message = content_between_quotes.group(1)
                        replacement = f'logger.{log_level}(f"{log_message}")'
                    else:
                        replacement = f'logger.{log_level}("Debug message")'
                else:
                    # Handle regular strings
                    content_between_quotes = re.search(r'["\'](.*?)["\']', print_statement)
                    if content_between_quotes:
                        log_message = content_between_quotes.group(1)
                        replacement = f'logger.{log_level}("{log_message}")'
                    else:
                        # Handle variables/expressions
                        content_inside = re.search(r'print\s*\(\s*(.*?)\s*\)', print_statement)
                        if content_inside:
                            expression = content_inside.group(1)
                            replacement = f'logger.{log_level}({expression})'
                        else:
                            replacement = f'logger.{log_level}("Debug message")'
                
                # Replace in content
                content = content.replace(print_statement, replacement)
                replacements_made += 1
            
            # Add logging import if needed
            if replacements_made > 0 and not has_logging_import:
                # Find the best place to add the import
                lines = content.split('\n')
                import_line = 'import logging'
                
                # Look for existing imports
                import_index = -1
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_index = i
                
                if import_index >= 0:
                    lines.insert(import_index + 1, import_line)
                else:
                    lines.insert(0, import_line)
                
                content = '\n'.join(lines)
            
            # Add logger setup if needed
            if replacements_made > 0 and 'logger = logging.getLogger(__name__)' not in content:
                lines = content.split('\n')
                logger_line = 'logger = logging.getLogger(__name__)'
                
                # Add after imports
                import_end = -1
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i
                
                if import_end >= 0:
                    lines.insert(import_end + 1, logger_line)
                else:
                    lines.insert(0, logger_line)
                
                content = '\n'.join(lines)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.results["errors"].append(f"Error processing {file_path}: {e}")
            
        return False
    
    def determine_log_level(self, print_statement: str) -> str:
        """Determine appropriate log level based on print statement content."""
        content_lower = print_statement.lower()
        
        if any(word in content_lower for word in ['error', 'exception', 'failed', 'fail']):
            return 'error'
        elif any(word in content_lower for word in ['warning', 'warn', 'caution']):
            return 'warning'
        elif any(word in content_lower for word in ['debug', 'trace', 'verbose']):
            return 'debug'
        elif any(word in content_lower for word in ['info', 'status', 'progress']):
            return 'info'
        else:
            return 'info'  # Default to info level
    
    def process_file(self, file_path: Path) -> Dict:
        """Process a single file."""
        result = {
            "file": str(file_path),
            "print_statements_found": 0,
            "print_statements_replaced": 0,
            "modified": False,
            "error": None
        }
        
        try:
            # Create backup
            backup_path = self.create_backup(file_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Find print statements
            print_statements = self.find_print_statements(file_path)
            result["print_statements_found"] = len(print_statements)
            
            if print_statements:
                logger.info(f"Found {len(print_statements)} print statements in {file_path}")
                
                # Replace with logging
                if self.replace_print_with_logging(file_path, print_statements):
                    result["print_statements_replaced"] = len(print_statements)
                    result["modified"] = True
                    logger.info(f"Replaced {len(print_statements)} print statements in {file_path}")
                else:
                    logger.warning(f"Failed to replace print statements in {file_path}")
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            logger.error(error_msg)
            result["error"] = error_msg
            self.results["errors"].append(error_msg)
        
        return result
    
    def scan_project(self) -> List[Path]:
        """Scan project for Python files with print statements."""
        python_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            if not self.should_exclude_file(py_file):
                print_statements = self.find_print_statements(py_file)
                if print_statements:
                    python_files.append(py_file)
        
        return python_files
    
    def run_cleanup(self, max_files: int = 20) -> Dict:
        """Run the cleanup process."""
        logger.info(f"Starting debug print cleanup for {self.project_root}")
        logger.info(f"Backup directory: {self.backup_dir}")
        
        # Scan for files with print statements
        files_to_process = self.scan_project()
        logger.info(f"Found {len(files_to_process)} files with print statements")
        
        # Limit processing for safety
        if len(files_to_process) > max_files:
            logger.info(f"Limiting to first {max_files} files for safety")
            files_to_process = files_to_process[:max_files]
        
        # Process files
        processed_files = []
        for file_path in files_to_process:
            logger.info(f"Processing: {file_path}")
            result = self.process_file(file_path)
            processed_files.append(result)
            
            # Update results
            self.results["files_processed"] += 1
            self.results["print_statements_found"] += result["print_statements_found"]
            self.results["print_statements_replaced"] += result["print_statements_replaced"]
            if result["modified"]:
                self.results["files_modified"] += 1
        
        self.results["processed_files"] = processed_files
        return self.results
    
    def generate_report(self) -> str:
        """Generate a cleanup report."""
        report = f"""
# Debug Print Cleanup Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project:** {self.project_root}
**Backup Directory:** {self.backup_dir}

## Summary
- **Files Processed:** {self.results['files_processed']}
- **Print Statements Found:** {self.results['print_statements_found']}
- **Print Statements Replaced:** {self.results['print_statements_replaced']}
- **Files Modified:** {self.results['files_modified']}
- **Errors:** {len(self.results['errors'])}

## Detailed Results
"""
        
        for file_result in self.results.get("processed_files", []):
            report += f"""
### {file_result['file']}
- Print statements found: {file_result['print_statements_found']}
- Print statements replaced: {file_result['print_statements_replaced']}
- File modified: {file_result['modified']}
"""
            if file_result.get('error'):
                report += f"- Error: {file_result['error']}\n"
        
        if self.results['errors']:
            report += "\n## Errors\n"
            for error in self.results['errors']:
                report += f"- {error}\n"
        
        return report

def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    cleaner = DebugPrintCleaner(project_root)
    
    # Run cleanup (limit to 20 files for safety)
    results = cleaner.run_cleanup(max_files=20)
    
    # Generate and save report
    report = cleaner.generate_report()
    report_file = project_root / "DEBUG_CLEANUP_REPORT.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Cleanup complete! Report saved to: {report_file}")
    logger.info(f"Backup directory: {cleaner.backup_dir}")
    
    logger.info("\n")
    logger.info(report)
    logger.info("=")

if __name__ == "__main__":
    main()
