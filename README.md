# VantaLedger Android App

A modern, offline-first financial management application with an MPesa/Instagram-inspired interface.

## Overview

VantaLedger is a standalone Android application for managing income and expenses. It features a professional financial interface inspired by MPesa combined with the engaging timeline feel of Instagram. The app is designed to be fully offline-first with optional manual cloud backups.

## Key Features

- **Modern UI/UX**: Clean, professional interface with Instagram-inspired timeline
- **Transaction Management**: Quick and intuitive income and expense tracking
- **Category System**: Predefined and custom categories with visual icons
- **Recurring Transactions**: Schedule repeating transactions with notifications
- **Budget Planning**: Set and track budgets by category with alerts
- **Reports & Analytics**: Visual breakdowns of spending and income patterns
- **Offline-First**: Full functionality without internet connection
- **Backup & Restore**: Manual export to JSON/CSV and Google Drive integration
- **Multi-Account Support**: Track multiple financial accounts
- **Security Features**: Optional biometric and PIN protection

## Tech Stack

| Layer        | Technology                                   |
| ------------ | -------------------------------------------- |
| Language     | Kotlin                                       |
| UI           | Jetpack Compose                              |
| Architecture | MVVM                                         |
| Local DB     | Room (SQLite abstraction)                    |
| Backup       | Manual file export / Google Drive (optional) |
| Tools        | Android Studio + Gradle                      |

## Project Structure

```
/VantaLedger/
├── data/
│   ├── model/      # Data entities
│   ├── db/         # Room database and DAOs
│   └── repository/ # Data access repositories
├── ui/
│   ├── screens/    # App screens
│   ├── components/ # Reusable UI components
│   └── theme/      # Design system
├── viewmodel/      # ViewModels for each screen
├── MainActivity.kt # Entry point
└── build.gradle    # Dependencies and configuration
```

## Development Timeline

The project is organized into five phases:

1. **Foundation & Core Transaction Management** (Weeks 1-3)
   - Project setup, architecture, transaction management, category system

2. **Enhanced Financial Features** (Weeks 4-6)
   - Recurring transactions, budget planning, reports & analytics

3. **User Experience & Security** (Weeks 7-9)
   - UI polish, notification system, security features

4. **Data Management & Backup** (Weeks 10-12)
   - Search & filtering, backup & restore, multi-account support

5. **Advanced Features & Polishing** (Weeks 13-15)
   - Widgets & quick actions, extended functionality, final testing

## Documentation

- [Feature Requirements](docs/feature_requirements.md) - Detailed breakdown of all app features
- [Project Plan](docs/project_plan.md) - Comprehensive development roadmap
- [Technical Architecture](docs/technical_architecture.md) - Detailed system design
- [UI/UX Guidelines](docs/ui_guidelines.md) - Design principles and patterns

## Getting Started

### Prerequisites

- Android Studio Arctic Fox or newer
- JDK 11 or higher
- Android SDK 31 (Android 12) or higher

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/Phantomojo/Vanta-ledger.git
   cd Vanta-ledger
   ```

2. Open the project in Android Studio

3. Sync Gradle and build the project

4. Run on an emulator or physical device

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original concept by Phantomojo
- Developed with assistance from Manus AI
