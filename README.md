# 🚀 Jasper TG BULK - Telegram Bot with Email Management

A powerful Telegram bot with a beautiful admin panel for managing email campaigns, SMTP profiles, and customer lists. Features random SMTP selection for optimal email deliverability.

## ✨ Features

- **🤖 Telegram Bot**: Automated messaging and customer management
- **📧 Smart Email System**: Random SMTP profile selection for better deliverability
- **🎨 Beautiful Admin Panel**: Modern, responsive UI with light/dark themes
- **🔒 Secure**: Encrypted SMTP passwords and admin authentication
- **📊 Analytics**: Dashboard with comprehensive statistics
- **📝 Template Management**: HTML email templates with live preview
- **🔍 SMTP Diagnostics**: Connection testing and inbox delivery optimization
- **👥 Customer Management**: Allowlist system for targeted messaging

## 🚀 Quick Start

### 1. **Complete Setup (Recommended)**
```bash
# Run the one-click setup script
scripts\setup_project.bat
```

### 2. **Manual Setup**
```bash
# Generate secure keys
scripts\generate_keys.bat

# Initialize database
scripts\init_db.bat

# Update .env file with your bot token
```

### 3. **Run the Application**
```bash
# Start admin panel
scripts\run_admin_full.bat

# Start Telegram bot
scripts\run_bot_full.bat
```

## 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

## 📧 SMTP Configuration

The system automatically selects random SMTP profiles for each email, providing:
- **Load balancing** across multiple servers
- **Better deliverability** through reputation distribution
- **Rate limit avoidance** by spreading emails
- **Professional headers** for inbox placement

### Supported Providers
- Gmail (App Password required)
- Outlook/Hotmail
- Custom SMTP servers
- Any provider supporting SMTP

## 🎨 Admin Panel Features

### Dashboard
- Real-time statistics
- System status monitoring
- Quick action buttons
- Bot connection testing

### SMTP Profiles
- Add/edit/delete profiles
- Connection testing
- Comprehensive diagnostics
- Active/inactive toggles

### Email Templates
- HTML editor with live preview
- Variable support
- Template activation/deactivation
- Professional formatting

### Customer Management
- Allowlist system
- Chat ID management
- Customer labeling
- Bulk operations

## 🔧 Technical Details

### Architecture
- **Backend**: FastAPI with SQLAlchemy
- **Database**: SQLite with automatic migrations
- **Frontend**: Modern HTML/CSS with Tailwind
- **Security**: Fernet encryption, bcrypt hashing
- **Email**: aiosmtplib with delivery optimization

### File Structure
```
JasperTgBulk/
├── app/                    # Core application
│   ├── admin/             # Admin panel routes
│   ├── bot/               # Telegram bot logic
│   ├── core/              # Configuration & database
│   ├── models/            # Database models
│   ├── services/          # Email & business logic
│   └── utils/             # Utility functions
├── scripts/               # Setup & utility scripts
├── templates/             # Admin panel HTML
├── static/                # Static assets
└── data/                  # Database & logs
```

## 🛠️ Development

### Prerequisites
- Python 3.8+
- Windows (batch scripts provided)
- Virtual environment support

### Dependencies
- FastAPI & Uvicorn
- SQLAlchemy & aiosqlite
- aiogram (Telegram bot)
- aiosmtplib (Email sending)
- Jinja2 (Templating)
- cryptography (Encryption)

### Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
SECRET_KEY=your_secret_key_here
FERNET_KEY=your_fernet_key_here
```

## 📱 Telegram Bot Usage

1. **Start the bot**: `/start`
2. **Add customers**: Use admin panel
3. **Send emails**: Configure templates and SMTP profiles
4. **Monitor**: Check dashboard for statistics

## 🎯 Email Deliverability Features

- **Professional Headers**: Message-ID, Date, From, Return-Path
- **Authentication**: SPF, DKIM, Domain verification
- **Reputation Management**: List-Unsubscribe, Feedback-ID
- **Content Optimization**: HTML structure, text alternatives
- **Security**: TLS/STARTTLS support

## 🔍 Troubleshooting

### Common Issues
1. **Database errors**: Run `scripts\init_db.bat`
2. **Import errors**: Ensure virtual environment is activated
3. **SMTP failures**: Check credentials and server settings
4. **Bot not responding**: Verify token in `.env` file

### Logs
- Admin panel: Console output
- Bot: `logs/bot.out` file
- Database: `data/app.db`

## 📈 Performance

- **Async operations** for better responsiveness
- **Connection pooling** for SMTP efficiency
- **Optimized queries** with SQLAlchemy
- **Lightweight frontend** with minimal dependencies

## 🔒 Security Features

- **Password encryption** with Fernet
- **Admin authentication** with bcrypt
- **Input validation** on all forms
- **SQL injection protection** with ORM
- **XSS prevention** with proper escaping

## 🌟 Advanced Features

- **Bulk email sending** with progress tracking
- **Template variables** for personalization
- **SMTP health monitoring** with diagnostics
- **Customer segmentation** with labels
- **Email analytics** and delivery reports

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs for errors
3. Ensure all dependencies are installed
4. Verify environment variables are set

## 🚀 Future Enhancements

- **Email scheduling** and automation
- **Advanced analytics** and reporting
- **API endpoints** for external integration
- **Multi-language support**
- **Mobile app** for on-the-go management

---

**Built with ❤️ for efficient email management and Telegram bot automation**
