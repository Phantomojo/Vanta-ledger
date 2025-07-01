# <img src="vanta_ledger_flutter/assets/images/app_logo_placeholder.svg" alt="Vanta Ledger Logo" height="60" style="vertical-align:middle;"> Vanta Ledger

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS%20%7C%20Desktop-purple)

---

> **A modern, offline-first finance app with MPesa/Instagram-inspired UI, analytics, and blazing performance.**

---

## ✨ Features

- **Modern UI/UX:** Instagram-inspired timeline, beautiful dark theme
- **Automatic Analytics:** Real-time reports, category breakdowns, net worth, and more
- **MPesa & Bank Ready:** (Planned) SMS/notification parsing for all major providers
- **Offline-First:** Works without internet, with optional cloud backup
- **Multi-Account Support:** Track all your wallets and banks
- **Security:** Biometric/PIN lock
- **Export/Import:** CSV/JSON backup and restore
- **Custom Categories:** Visual icons, easy management
- **Test Data:** Demo-ready with 1-year and 10,000+ transaction datasets

---

## 🚀 Screenshots

<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="250"/>
  <img src="docs/screenshots/reports.png" alt="Reports" width="250"/>
  <img src="docs/screenshots/transactions.png" alt="Transactions" width="250"/>
</p>

---

## 🛠️ Tech Stack

| Layer        | Technology                                   |
| ------------ | -------------------------------------------- |
| Language     | Dart (Flutter)                               |
| UI           | Flutter, fl_chart, Provider                  |
| Local DB     | SQLite (sqflite)                             |
| Backup       | Manual export/import, Google Drive (planned) |
| Analytics    | Custom, fl_chart                             |
| SMS Parsing  | telephony (planned)                          |

---

## ⚡ Quick Start

```sh
# Clone the repo
https://github.com/Phantomojo/Vanta-ledger.git
cd Vanta-ledger/vanta_ledger_flutter

# Get dependencies
flutter pub get

# Run on emulator/device
flutter run

# Build release APK (for sharing/demo)
flutter build apk --release --no-tree-shake-icons
```

---

## 📦 Demo APK

- Download the latest APK from the [Releases page](https://github.com/Phantomojo/Vanta-ledger/releases)
- Pre-filled with demo/test data for instant exploration

---

## 🖼️ Logo & Animation

<p align="center">
  <img src="vanta_ledger_flutter/assets/images/app_logo_placeholder.svg" alt="Vanta Ledger Logo" height="120"/>
</p>

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Original concept by Phantomojo
- Developed with assistance from Manus AI
- Inspired by MPesa, Instagram, and modern fintech apps
