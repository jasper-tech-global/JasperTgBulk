## Jasper TG BULK

A modular Telegram bulk sender with an admin panel.

### Setup

1. Create and populate `.env` from `.env.sample`.
   - Generate a Fernet key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - Set `TELEGRAM_BOT_TOKEN` and admin credentials.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run admin API/UI: `scripts/run_admin.bat`.
4. Run Telegram bot: `scripts/run_bot.bat`.

### Default DB

SQLite at `./data/app.db`. Tables auto-created on first start. Admin user is bootstrapped from env.

### Command Format

In Telegram chat with the bot:

`/template_code recipient@example.com key1=value1 key2=value2`

Only allowed chat IDs can send. Manage allowlist and templates in the admin panel.
