#!/usr/bin/env python3
"""
Unified Launcher for Vanta-ledger Enhanced

This script automatically detects the platform, checks and installs dependencies,
and launches the application in the appropriate way for the current environment.

Features:
- Cross-platform detection (Windows, macOS, Linux, Android)
- Environment detection (PowerShell, WSL, native Linux)
- Dependency checking and safe installation
- Appropriate launch method for each platform
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import re
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vanta_launcher.log')
    ]
)
logger = logging.getLogger('vanta_launcher')

# Constants
REQUIRED_PYTHON_VERSION = (3, 11, 0)
VANTA_APP_NAME = "Vanta-ledger Enhanced"
VANTA_PACKAGE_NAME = "vanta_ledger"
GITHUB_REPO = "https://github.com/Phantomojo/Vanta-ledger.git"

# Required packages with version constraints
REQUIRED_PACKAGES = {
    "kivy": ">=2.1.0",
    "requests": ">=2.28.0",
    "matplotlib": ">=3.5.0",
    "pillow": ">=9.0.0",
    "pyyaml": ">=6.0",
}

# Android-specific constants
ANDROID_KIVY_LAUNCHER_DIR = "/sdcard/kivy"


class PlatformInfo:
    """Information about the current platform and environment."""
    
    def __init__(self):
        """Initialize and detect platform information."""
        self.os_name = platform.system().lower()
        self.os_version = platform.version()
        self.is_64bit = sys.maxsize > 2**32
        self.python_version = sys.version_info
        self.is_android = self._detect_android()
        self.is_wsl = self._detect_wsl()
        self.is_powershell = self._detect_powershell()
        self.temp_dir = tempfile.gettempdir()
        self.home_dir = str(Path.home())
        self.venv_dir = os.path.join(self.home_dir, ".vanta_venv")
        
        # Detect pip command
        self.pip_cmd = self._get_pip_command()
        
        logger.info(f"Detected platform: {self.os_name} ({self.os_version})")
        if self.is_android:
            logger.info("Running on Android")
        elif self.is_wsl:
            logger.info("Running in Windows Subsystem for Linux")
        elif self.is_powershell:
            logger.info("Running in PowerShell")
    
    def _detect_android(self) -> bool:
        """Detect if running on Android."""
        if self.os_name == 'linux':
            # Check for Android-specific paths
            return os.path.exists("/system/build.prop") or os.path.exists("/sdcard")
        return False
    
    def _detect_wsl(self) -> bool:
        """Detect if running in Windows Subsystem for Linux."""
        if self.os_name == 'linux':
            try:
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
            except:
                pass
        return False
    
    def _detect_powershell(self) -> bool:
        """Detect if running in PowerShell."""
        if self.os_name == 'windows':
            # Check if running in PowerShell
            return 'powershell' in os.environ.get('PSModulePath', '').lower()
        return False
    
    def _get_pip_command(self) -> str:
        """Get the appropriate pip command for the current environment."""
        # Try different pip commands
        pip_commands = [
            f"python{self.python_version.major}.{self.python_version.minor} -m pip",
            f"python{self.python_version.major} -m pip",
            "python -m pip",
            "pip3",
            "pip"
        ]
        
        for cmd in pip_commands:
            try:
                subprocess.run(f"{cmd} --version", shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return cmd
            except subprocess.CalledProcessError:
                continue
        
        # If no pip command works, return a default
        return "pip"
    
    def get_platform_name(self) -> str:
        """Get a descriptive name for the current platform."""
        if self.is_android:
            return "Android"
        elif self.is_wsl:
            return "WSL Ubuntu"
        elif self.is_powershell:
            return "Windows PowerShell"
        elif self.os_name == 'linux':
            # Try to get Linux distribution name
            try:
                with open('/etc/os-release', 'r') as f:
                    os_info = {}
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            os_info[key] = value.strip('"')
                    if 'NAME' in os_info:
                        return os_info['NAME']
            except:
                pass
            return "Linux"
        elif self.os_name == 'darwin':
            return "macOS"
        elif self.os_name == 'windows':
            return "Windows"
        else:
            return self.os_name.capitalize()


class DependencyManager:
    """Manage dependencies for the application."""
    
    def __init__(self, platform_info: PlatformInfo):
        """Initialize with platform information."""
        self.platform = platform_info
    
    def check_python_version(self) -> bool:
        """Check if the Python version meets requirements."""
        current_version = self.platform.python_version
        required_version = REQUIRED_PYTHON_VERSION
        
        if (current_version.major, current_version.minor, current_version.micro) >= required_version:
            logger.info(f"Python version {current_version.major}.{current_version.minor}.{current_version.micro} meets requirements")
            return True
        else:
            logger.error(f"Python version {current_version.major}.{current_version.minor}.{current_version.micro} does not meet minimum requirement {required_version[0]}.{required_version[1]}.{required_version[2]}")
            return False
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Check if all required packages are installed.
        
        Returns:
            Tuple of (all_installed, missing_packages)
        """
        missing_packages = []
        
        for package, version_constraint in REQUIRED_PACKAGES.items():
            if not self._is_package_installed(package, version_constraint):
                missing_packages.append(f"{package}{version_constraint}")
        
        all_installed = len(missing_packages) == 0
        if all_installed:
            logger.info("All required packages are installed")
        else:
            logger.warning(f"Missing packages: {', '.join(missing_packages)}")
        
        return all_installed, missing_packages
    
    def _is_package_installed(self, package: str, version_constraint: str) -> bool:
        """Check if a package is installed with the required version."""
        try:
            # Try to import the package
            __import__(package)
            
            # Check version if needed
            if version_constraint:
                # Get installed version
                cmd = f"{self.platform.pip_cmd} show {package}"
                result = subprocess.run(cmd, shell=True, check=True, 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       text=True)
                
                # Parse version from output
                version_match = re.search(r'Version: ([\d\.]+)', result.stdout)
                if version_match:
                    installed_version = version_match.group(1)
                    
                    # Parse constraint
                    constraint_type = re.match(r'([<>=]+)', version_constraint)
                    if constraint_type:
                        op = constraint_type.group(1)
                        required_version = version_constraint[len(op):]
                        
                        # Compare versions
                        from pkg_resources import parse_version
                        if op == '>=':
                            return parse_version(installed_version) >= parse_version(required_version)
                        elif op == '>':
                            return parse_version(installed_version) > parse_version(required_version)
                        elif op == '==':
                            return parse_version(installed_version) == parse_version(required_version)
                        elif op == '<=':
                            return parse_version(installed_version) <= parse_version(required_version)
                        elif op == '<':
                            return parse_version(installed_version) < parse_version(required_version)
            
            # If no version constraint or couldn't parse version, assume it's fine
            return True
        except (ImportError, subprocess.CalledProcessError):
            return False
    
    def install_dependencies(self, missing_packages: List[str], use_venv: bool = True) -> bool:
        """
        Install missing dependencies.
        
        Args:
            missing_packages: List of packages to install
            use_venv: Whether to use a virtual environment
            
        Returns:
            True if installation was successful
        """
        if not missing_packages:
            return True
        
        logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
        
        # Create virtual environment if needed
        if use_venv and not self.platform.is_android:
            if not os.path.exists(self.platform.venv_dir):
                logger.info(f"Creating virtual environment at {self.platform.venv_dir}")
                try:
                    subprocess.run(f"python -m venv {self.platform.venv_dir}", 
                                  shell=True, check=True)
                except subprocess.CalledProcessError:
                    logger.warning("Failed to create virtual environment, falling back to system Python")
                    use_venv = False
        
        # Determine pip command
        pip_cmd = self.platform.pip_cmd
        if use_venv and not self.platform.is_android:
            if self.platform.os_name == 'windows':
                pip_cmd = f"{self.platform.venv_dir}\\Scripts\\pip"
            else:
                pip_cmd = f"{self.platform.venv_dir}/bin/pip"
        
        # Install packages
        try:
            # First try installing all at once
            packages_str = ' '.join(missing_packages)
            cmd = f"{pip_cmd} install {packages_str} --user"
            
            # On Android, don't use --user flag
            if self.platform.is_android:
                cmd = f"{pip_cmd} install {packages_str}"
            
            logger.info(f"Running: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            # If that fails, try installing one by one
            success = True
            for package in missing_packages:
                try:
                    cmd = f"{pip_cmd} install {package} --user"
                    if self.platform.is_android:
                        cmd = f"{pip_cmd} install {package}"
                    
                    logger.info(f"Running: {cmd}")
                    subprocess.run(cmd, shell=True, check=True)
                except subprocess.CalledProcessError:
                    logger.error(f"Failed to install {package}")
                    success = False
            
            return success


class AppManager:
    """Manage the Vanta-ledger application."""
    
    def __init__(self, platform_info: PlatformInfo):
        """Initialize with platform information."""
        self.platform = platform_info
        self.app_dir = self._find_app_directory()
    
    def _find_app_directory(self) -> str:
        """Find the application directory."""
        # First check if we're already in the app directory
        current_dir = os.getcwd()
        if os.path.exists(os.path.join(current_dir, "src", VANTA_PACKAGE_NAME)):
            return current_dir
        
        # Check if we're in the src directory
        if os.path.exists(os.path.join(current_dir, VANTA_PACKAGE_NAME)):
            return os.path.dirname(current_dir)
        
        # Check parent directory
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(parent_dir, "src", VANTA_PACKAGE_NAME)):
            return parent_dir
        
        # If not found, use current directory and warn
        logger.warning(f"Could not find application directory, using current directory: {current_dir}")
        return current_dir
    
    def check_app_files(self) -> bool:
        """Check if all required application files exist."""
        # Check for main application files
        main_py = os.path.join(self.app_dir, "src", VANTA_PACKAGE_NAME, "main.py")
        if not os.path.exists(main_py):
            logger.error(f"Main application file not found: {main_py}")
            return False
        
        # Check for frontend directory
        frontend_dir = os.path.join(self.app_dir, "frontend")
        if not os.path.exists(frontend_dir):
            logger.error(f"Frontend directory not found: {frontend_dir}")
            return False
        
        logger.info("All required application files found")
        return True
    
    def launch_app(self) -> bool:
        """
        Launch the application in the appropriate way for the current platform.
        
        Returns:
            True if launch was successful
        """
        logger.info(f"Launching {VANTA_APP_NAME} on {self.platform.get_platform_name()}")
        
        # Different launch methods based on platform
        if self.platform.is_android:
            return self._launch_on_android()
        elif self.platform.is_wsl:
            return self._launch_on_wsl()
        elif self.platform.os_name == 'windows':
            return self._launch_on_windows()
        elif self.platform.os_name == 'darwin':
            return self._launch_on_macos()
        else:  # Linux and other Unix-like systems
            return self._launch_on_linux()
    
    def _launch_on_android(self) -> bool:
        """Launch the application on Android."""
        # Check if Kivy Launcher is installed
        kivy_dir = ANDROID_KIVY_LAUNCHER_DIR
        if not os.path.exists(kivy_dir):
            logger.error(f"Kivy Launcher directory not found: {kivy_dir}")
            logger.error("Please install Kivy Launcher from Google Play Store")
            return False
        
        # Copy application files to Kivy Launcher directory
        app_name = "vanta_ledger"
        app_dir = os.path.join(kivy_dir, app_name)
        
        # Create app directory if it doesn't exist
        os.makedirs(app_dir, exist_ok=True)
        
        # Copy main.py and other required files
        src_main = os.path.join(self.app_dir, "src", VANTA_PACKAGE_NAME, "main.py")
        dst_main = os.path.join(app_dir, "main.py")
        shutil.copy2(src_main, dst_main)
        
        # Copy frontend directory
        src_frontend = os.path.join(self.app_dir, "frontend")
        dst_frontend = os.path.join(app_dir, "frontend")
        if os.path.exists(dst_frontend):
            shutil.rmtree(dst_frontend)
        shutil.copytree(src_frontend, dst_frontend)
        
        # Create android.txt file
        with open(os.path.join(app_dir, "android.txt"), "w") as f:
            f.write(f"title={VANTA_APP_NAME}\n")
            f.write("author=Phantomojo\n")
            f.write("orientation=portrait\n")
        
        logger.info(f"Application files copied to {app_dir}")
        logger.info("Please open Kivy Launcher and select 'vanta_ledger' to launch the application")
        return True
    
    def _launch_on_windows(self) -> bool:
        """Launch the application on Windows."""
        # Determine Python executable
        python_exe = sys.executable
        
        # Check if we should use virtual environment
        venv_python = os.path.join(self.platform.venv_dir, "Scripts", "python.exe")
        if os.path.exists(venv_python):
            python_exe = venv_python
        
        # Build command
        main_py = os.path.join(self.app_dir, "src", VANTA_PACKAGE_NAME, "main.py")
        cmd = f'"{python_exe}" "{main_py}"'
        
        # Launch in a new window if in PowerShell
        if self.platform.is_powershell:
            cmd = f'Start-Process "{python_exe}" -ArgumentList "{main_py}" -NoNewWindow'
            try:
                subprocess.Popen(["powershell", "-Command", cmd], 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info(f"Application launched with PowerShell: {cmd}")
                return True
            except Exception as e:
                logger.error(f"Failed to launch with PowerShell: {e}")
                # Fall back to regular launch
        
        # Regular launch
        try:
            subprocess.Popen(cmd, shell=True)
            logger.info(f"Application launched: {cmd}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch application: {e}")
            return False
    
    def _launch_on_macos(self) -> bool:
        """Launch the application on macOS."""
        # Determine Python executable
        python_exe = sys.executable
        
        # Check if we should use virtual environment
        venv_python = os.path.join(self.platform.venv_dir, "bin", "python")
        if os.path.exists(venv_python):
            python_exe = venv_python
        
        # Build command
        main_py = os.path.join(self.app_dir, "src", VANTA_PACKAGE_NAME, "main.py")
        cmd = f'"{python_exe}" "{main_py}"'
        
        # Launch in Terminal
        try:
            subprocess.Popen(["open", "-a", "Terminal", cmd])
            logger.info(f"Application launched in Terminal: {cmd}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch in Terminal: {e}")
            
            # Fall back to regular launch
            try:
                subprocess.Popen(cmd, shell=True)
                logger.info(f"Application launched: {cmd}")
                return True
            except Exception as e:
                logger.error(f"Failed to launch application: {e}")
                return False
    
    def _launch_on_linux(self) -> bool:
        """Launch the application on Linux."""
        # Determine Python executable
        python_exe = sys.executable
        
        # Check if we should use virtual environment
        venv_python = os.path.join(self.platform.venv_dir, "bin", "python")
        if os.path.exists(venv_python):
            python_exe = venv_python
        
        # Build command
        main_py = os.path.join(self.app_dir, "src", VANTA_PACKAGE_NAME, "main.py")
        cmd = f'"{python_exe}" "{main_py}"'
        
        # Try to launch in a terminal if available
        terminal_cmds = [
            f'x-terminal-emulator -e {cmd}',
            f'gnome-terminal -- {cmd}',
            f'konsole -e {cmd}',
            f'xterm -e {cmd}'
        ]
        
        for term_cmd in terminal_cmds:
            try:
                subprocess.Popen(term_cmd, shell=True)
                logger.info(f"Application launched in terminal: {term_cmd}")
                return True
            except Exception:
                continue
        
        # Fall back to regular launch
        try:
            subprocess.Popen(cmd, shell=True)
            logger.info(f"Application launched: {cmd}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch application: {e}")
            return False
    
    def _launch_on_wsl(self) -> bool:
        """Launch the application on WSL."""
        # Similar to Linux launch, but with WSL considerations
        return self._launch_on_linux()


def main():
    """Main entry point for the launcher."""
    print(f"\n=== {VANTA_APP_NAME} Launcher ===\n")
    
    # Detect platform
    platform_info = PlatformInfo()
    print(f"Detected platform: {platform_info.get_platform_name()}")
    
    # Check Python version
    dependency_manager = DependencyManager(platform_info)
    if not dependency_manager.check_python_version():
        print(f"Error: Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]} or higher is required.")
        print(f"Current version: {platform_info.python_version.major}.{platform_info.python_version.minor}.{platform_info.python_version.micro}")
        sys.exit(1)
    
    # Check dependencies
    print("\nChecking dependencies...")
    all_installed, missing_packages = dependency_manager.check_dependencies()
    
    # Install missing dependencies if needed
    if not all_installed:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        install = input("Do you want to install missing packages? (y/n): ").lower()
        
        if install == 'y':
            use_venv = False
            if not platform_info.is_android:
                use_venv_input = input("Use virtual environment? (recommended) (y/n): ").lower()
                use_venv = use_venv_input == 'y'
            
            success = dependency_manager.install_dependencies(missing_packages, use_venv)
            if not success:
                print("Error: Failed to install some dependencies.")
                print("Please install them manually and try again.")
                sys.exit(1)
        else:
            print("Cannot continue without required packages.")
            sys.exit(1)
    
    # Check application files
    app_manager = AppManager(platform_info)
    if not app_manager.check_app_files():
        print("Error: Some required application files are missing.")
        
        # Offer to clone from GitHub
        clone = input(f"Do you want to clone the repository from {GITHUB_REPO}? (y/n): ").lower()
        if clone == 'y':
            try:
                # Clone to a temporary directory
                temp_dir = os.path.join(platform_info.temp_dir, "vanta_ledger_clone")
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                print(f"Cloning repository to {temp_dir}...")
                subprocess.run(f"git clone {GITHUB_REPO} {temp_dir}", shell=True, check=True)
                
                # Copy files to current directory
                print("Copying files...")
                for item in os.listdir(temp_dir):
                    src = os.path.join(temp_dir, item)
                    dst = os.path.join(os.getcwd(), item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                
                # Clean up
                shutil.rmtree(temp_dir)
                
                # Reinitialize app manager
                app_manager = AppManager(platform_info)
                if not app_manager.check_app_files():
                    print("Error: Still missing required files after cloning.")
                    sys.exit(1)
            except Exception as e:
                print(f"Error cloning repository: {e}")
                sys.exit(1)
        else:
            print("Cannot continue without required files.")
            sys.exit(1)
    
    # Launch application
    print("\nLaunching application...")
    success = app_manager.launch_app()
    
    if success:
        print(f"\n{VANTA_APP_NAME} launched successfully!")
    else:
        print(f"\nFailed to launch {VANTA_APP_NAME}. Please check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        print("Please check the log file for details.")
        sys.exit(1)
