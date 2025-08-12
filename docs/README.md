# Vanta Ledger Documentation

## Access
- Backend API: http://localhost:8500
- API Docs: http://localhost:8500/docs

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Node.js 16+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vanta-ledger
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Start the system**
   ```bash
   ./scripts/start.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8500
   - MongoDB Admin: http://localhost:8081
   - Login: Use configured credentials (see environment setup)

Note: Initial admin credentials are not hardcoded. Set `ADMIN_PASSWORD` (12+ chars) in your environment before running the database init script. Do not commit secrets.

## 📁 Project Structure

```
vanta-ledger/
├── src/                    # Source code
│   ├── vanta_ledger/      # Main application package
│   │   ├── main.py        # Main application
│   │   ├── config.py      # Configuration
│   │   ├── auth.py        # Authentication
│   │   ├── models/        # Database models
│   │   ├── routes/        # API routes
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
├── frontend/              # React frontend
│   └── frontend-web/
├── database/              # Database setup
│   ├── docker-compose.yml # Database services
│   ├── init/             # Database initialization
│   └── migrations/       # Database migrations
├── scripts/              # Management scripts
│   ├── setup.sh         # Initial setup
│   ├── start.sh         # Start services
│   ├── stop.sh          # Stop services
│   └── status.sh        # Check status
├── docs/                 # Documentation
├── data/                 # Data storage
│   ├── processed_documents/ # OCR processed documents
│   └── uploads/            # File uploads
└── logs/                 # Application logs
```

## 🔧 Management Commands

### Start Services
```bash
./scripts/start.sh
```

### Stop Services
```bash
./scripts/stop.sh
```

### Check Status
```bash
./scripts/status.sh
```

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

## 📊 Features

### Document Management
- **OCR Processing**: Automatic text extraction from scanned documents
- **Document Analysis**: AI-powered content analysis and categorization
- **Search & Filter**: Advanced search capabilities with filters
- **Metadata Extraction**: Automatic extraction of dates, amounts, companies

### Financial Tracking
- **Invoice Management**: Track invoices and payments
- **Project Tracking**: Monitor project progress and costs
- **Company Management**: Manage client and vendor information
- **Financial Analytics**: Generate reports and insights

### User Management
- **Authentication**: Secure JWT-based authentication
- **Role-based Access**: Different permission levels
- **User Profiles**: Manage user information and preferences

## 🗄️ Database

The system uses a hybrid database approach:
- **PostgreSQL**: Primary relational data (users, companies, projects)
- **MongoDB**: Document storage and unstructured data
- **Redis**: Caching and session management

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Secure API endpoints
- Input validation and sanitization
- GitHub Advanced Security integration
- Automated vulnerability scanning

## 🚀 Deployment

### Development
```bash
./scripts/start.sh
```

### Production
1. Set environment variables
2. Configure production database
3. Set up reverse proxy (nginx)
4. Use PM2 or similar for process management

## 📝 API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8500/docs
- ReDoc: http://localhost:8500/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation in `/docs`
- Review the API documentation
- Check the logs in `/logs`
- Open an issue on GitHub
