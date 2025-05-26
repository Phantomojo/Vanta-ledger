# Vanta-ledger Enhanced

A modern financial ledger application for company bookkeepers managing transactions for multiple owners.

## Overview

Vanta-ledger Enhanced is a comprehensive financial management application designed specifically for bookkeepers who manage transactions for multiple company owners. The application features a modern, Instagram/MPesa-inspired interface with robust multi-owner support, advanced analytics, and secure authentication.

## Features

- **Modern UI/UX**: Clean, card-based interface with intuitive navigation and responsive design
- **Multi-Owner Support**: Manage transactions for up to 4 company owners with ownership percentage tracking
- **Role-Based Access Control**: Dedicated bookkeeper role with appropriate permissions
- **Financial Analytics**: Visual reports and insights with filtering by owner and time period
- **Secure Authentication**: Robust user authentication and session management
- **Cross-Platform Compatibility**: Works on Windows (VS Code/PowerShell), WSL Ubuntu, Linux (Parrot Security), and Android
- **Offline Support**: Continue working without internet connection with automatic synchronization

## Installation & Running the Application

### Prerequisites

- Python 3.11 or higher

### Quick Start (All Platforms)

The application includes a unified launcher script that automatically detects your platform, installs required dependencies, and starts the application in the most appropriate way.

1. Clone the repository:
   ```
   git clone https://github.com/Phantomojo/Vanta-ledger.git
   cd Vanta-ledger
   ```

2. Run the launcher:
   ```
   python launch.py
   ```

The launcher will:
- Detect your operating system and environment (Windows/PowerShell, WSL, Linux, Android)
- Check for required dependencies and offer to install them if missing
- Launch the application using the appropriate method for your platform

### Platform-Specific Notes

#### Windows
- The launcher works in both Command Prompt and PowerShell
- Dependencies will be installed in user mode to avoid permission issues
- A virtual environment can be used if selected during the launcher process

#### WSL Ubuntu
- The launcher detects WSL automatically and adjusts paths accordingly
- GUI applications require WSL to be properly configured with X server

#### Linux (Parrot Security)
- The launcher will attempt to use your preferred terminal emulator
- All security features are preserved

#### Android
- The launcher will prepare files for Kivy Launcher
- You'll need to install Kivy Launcher from the Google Play Store
- The application will appear in the Kivy Launcher app list

## Platform-Specific Setup

### Windows (VS Code with PowerShell)

1. Install Python 3.11+ from the [official website](https://www.python.org/downloads/)
2. Install VS Code and the Python extension
3. Open the project folder in VS Code
4. Open a PowerShell terminal and run the installation steps above

### WSL Ubuntu

1. Ensure WSL Ubuntu is installed and configured
2. Open a WSL terminal
3. Navigate to the project directory
4. Run the installation steps above

### Linux (Parrot Security)

1. Open a terminal
2. Navigate to the project directory
3. Run the installation steps above

### Android

1. Install the Kivy Launcher app from the Google Play Store
2. Copy the project files to your Android device in the Kivy Launcher directory
3. Launch the app through Kivy Launcher

## Usage

### Login

The application comes with pre-configured user accounts:

- **Bookkeeper**: 
  - Username: `bookkeeper`
  - Password: `password123`

- **Owner** (for testing):
  - Username: `owner1`
  - Password: `password123`

### Main Features

1. **Dashboard**: Overview of financial status with income, expenses, and balance
2. **Transactions**: Add, edit, and delete transactions with owner attribution
3. **Owners**: Manage company owners and their ownership percentages
4. **Analytics**: View financial reports and insights with filtering options
5. **Settings**: Configure application preferences and user settings

## Architecture

Vanta-ledger Enhanced follows a modular architecture:

- **Frontend**: Kivy-based UI with modular components
- **Models**: Data models for transactions, owners, and users
- **Utils**: Utility functions for API communication, validation, and formatting
- **Theme**: Comprehensive theming system for consistent UI

## Development

### Directory Structure

```
Vanta-ledger-enhanced/
├── frontend/
│   ├── components/     # Reusable UI components
│   ├── models/         # Data models
│   ├── screens/        # Application screens
│   ├── theme/          # Theming system
│   └── utils/          # Utility functions
├── src/
│   └── vanta_ledger/   # Backend code
└── tests/              # Test suite
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Testing

The application has been thoroughly tested on all required platforms:
- VS Code on PowerShell (Windows)
- WSL Ubuntu
- Linux (Parrot Security)
- Android phones

See the [testing plan](testing_plan.md) and [test results](test_results.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Vanta-ledger project by Phantomojo
- Enhanced version developed by Manus AI
