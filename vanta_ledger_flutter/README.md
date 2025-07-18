# Vanta Ledger Flutter

![Vanta Ledger Logo](assets/images/app_logo_placeholder.png)

*A modern, cross-platform finance app for personal wealth management, inspired by MPesa and Instagram.*

---

## Overview

Vanta Ledger Flutter is a next-generation, offline-first financial management application built with Flutter. It offers a seamless, visually engaging experience for tracking income, expenses, investments, and budgets across Android, iOS, Windows, macOS, Linux, and Web.

---

## Key Features

- **Modern UI/UX**: Clean, professional interface with timeline-inspired navigation
- **Transaction Management**: Quick, intuitive income and expense tracking
- **Category System**: Predefined & custom categories with visual icons
- **Recurring Transactions**: Schedule repeating transactions with notifications
- **Budget Planning**: Set and track budgets by category with alerts
- **Reports & Analytics**: Visual breakdowns of spending and income patterns
- **Multi-Account Support**: Track multiple financial accounts
- **Investments Tracking**: Manage and analyze investment portfolios
- **Security**: Optional biometric and PIN protection
- **Offline-First**: Full functionality without internet connection
- **Backup & Restore**: Manual export/import to JSON/CSV, Google Drive integration
- **Theme Support**: Light/Dark mode, Material 3 design
- **Accessibility**: Designed for usability and inclusivity

---

## Screenshots

*Coming soon!*

---

## Project Structure

```
vanta_ledger_flutter/
├── lib/
│   ├── models/         # Data models (Account, Transaction, etc.)
│   ├── providers/      # State management (Provider)
│   ├── screens/        # App screens (Dashboard, Transactions, etc.)
│   ├── services/       # Business logic, database, notifications
│   ├── theme/          # App theming and styles
│   └── main.dart       # App entry point
├── assets/             # Icons, images, fonts
├── test/               # Unit and widget tests
├── pubspec.yaml        # Dependencies and configuration
└── ...
```

---

## Getting Started

### Prerequisites
- [Flutter SDK](https://flutter.dev/docs/get-started/install) (3.10+ recommended)
- Android Studio, VS Code, or compatible IDE
- Dart 3.0+

### Setup
1. **Clone the repository:**
   ```
   git clone https://github.com/Phantomojo/Vanta-ledger.git
   cd Vanta-ledger/vanta_ledger_flutter
   ```
2. **Install dependencies:**
   ```
   flutter pub get
   ```
3. **Run the app:**
   - For Android/iOS: Launch an emulator or connect a device, then run:
     ```
     flutter run
     ```
   - For Web:
     ```
     flutter run -d chrome
     ```
   - For Desktop (Windows/macOS/Linux):
     ```
     flutter run -d windows  # or macos/linux
     ```

---

## Usage
- **Onboarding:** Set up your profile and preferences on first launch
- **Add Transactions:** Tap the "+" button to quickly add income or expenses
- **Budgets:** Set monthly budgets by category and receive alerts
- **Reports:** Visualize your spending, income, and investments
- **Settings:** Switch themes, manage security, backup/restore data

---

## Architecture
- **State Management:** Provider pattern
- **Database:** Local (sqflite/Isar/Drift, depending on platform)
- **UI:** Material 3, responsive layouts
- **Notifications:** Local notifications for reminders and recurring transactions
- **Backup:** Manual export/import, Google Drive integration (optional)

---

## Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments
- Original concept by Phantomojo
- Developed with assistance from Manus AI

---

## Logo
*A modern finance logo will be added here soon. If you are a designer and want to contribute, please submit a PR!* 

---

## Important Notice

- **Flutter is the only supported mobile app.**
- Native Android (android/ and android-app/) projects have been deprecated and removed.
- Large test data files (e.g., transactions_huge.json) are now in `dev_assets/` for local development only and are not required for production or normal usage.

--- 