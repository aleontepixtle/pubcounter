# Web Automation UI

A secure web interface for managing and running the JW.org inventory submission automation script. This application allows multiple users to securely submit their credentials and run automated inventory submissions through a user-friendly web interface.

## 🔒 Security Features

- **End-to-end TLS encryption** via Cloudflare Tunnel
- **AES-256 credential encryption** at rest
- **Secure session management** with HttpOnly cookies
- **CSRF protection** on all forms
- **Rate limiting** to prevent abuse
- **Admin approval system** for new users
- **Temporary credential handling** - credentials are only decrypted during job execution
- **Job queue system** - prevents concurrent access issues

## 📋 Prerequisites

### Development Machine (Your Desktop)
- Python 3.11+
- Git
- Docker and Docker Compose (for testing the automation script)

### Production Machine (Your Server)
- Python 3.11+
- Docker and Docker Compose
- Redis
- Cloudflare Tunnel configured
- Domain with Cloudflare DNS

## 🚀 Quick Start - Development Setup

### 1. Clone the Repository

```bash
# If starting fresh
cd /home/a-robut/Documents/Github/pubcounter
git pull origin main

# Navigate to the web UI directory
cd web-automation-ui
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Generate required secrets
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
python3 -c "from cryptography.fernet import Fernet; print('CREDENTIAL_ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env

# Edit .env and update the following:
nano .env  # or your preferred editor
```

Required changes in `.env`:
```bash
# Update these paths to match your system
DOCKER_AUTOMATION_PATH=/home/a-robut/Documents/Github/pubcounter/src/utilities/selenium-inventory-submit

# Optional: Add n8n webhook URL for Discord notifications
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/discord-notification
```

### 5. Initialize Database

```bash
python3 init_db.py
```

This will:
- Create the database schema
- Create an admin user (you'll be prompted for credentials)

### 6. Start Redis (Required for Job Queue)

```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Or install Redis locally and run:
# redis-server
```

### 7. Run the Application

You need **three terminal windows**:

**Terminal 1 - Flask App:**
```bash
source venv/bin/activate
python3 run.py
```

**Terminal 2 - RQ Worker:**
```bash
source venv/bin/activate
python3 run_worker.py
```

**Terminal 3 - Redis (if not using Docker):**
```bash
redis-server
```

### 8. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

Default admin credentials (if you used init_db.py defaults):
- Username: `admin`
- Password: (what you set during init_db.py)

## 📦 Production Deployment

### 1. Push Code to GitHub

From your development machine:

```bash
cd /home/a-robut/Documents/Github/pubcounter

# Stage the web-automation-ui directory
git add web-automation-ui/

# Commit
git commit -m "Add web automation UI with secure credential management"

# Push to GitHub
git push origin main
```

### 2. Clone on Production Server

SSH into your production server:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pubcounter.git
cd pubcounter/web-automation-ui
```

### 3. Production Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Generate production secrets (IMPORTANT!)
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
python3 -c "from cryptography.fernet import Fernet; print('CREDENTIAL_ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env
```

Edit `.env` for production:
```bash
nano .env
```

Update these critical settings:
```bash
FLASK_ENV=production
SESSION_COOKIE_SECURE=true  # REQUIRED for HTTPS

# Update paths for your production server
DOCKER_AUTOMATION_PATH=/path/to/your/selenium-inventory-submit

# Redis (if using Docker)
REDIS_URL=redis://localhost:6379/0

# n8n webhook for Discord
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/discord-notification

# Set this to true to require admin approval for new users
REQUIRE_ADMIN_APPROVAL=true
```

### 4. Initialize Production Database

```bash
python3 init_db.py
```

### 5. Set Up Services

#### Option A: Using systemd (Recommended)

Create Flask service file:
```bash
sudo nano /etc/systemd/system/automation-web.service
```

```ini
[Unit]
Description=Automation Web UI
After=network.target redis.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/pubcounter/web-automation-ui
Environment="PATH=/path/to/pubcounter/web-automation-ui/venv/bin"
ExecStart=/path/to/pubcounter/web-automation-ui/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create RQ Worker service file:
```bash
sudo nano /etc/systemd/system/automation-worker.service
```

```ini
[Unit]
Description=Automation RQ Worker
After=network.target redis.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/pubcounter/web-automation-ui
Environment="PATH=/path/to/pubcounter/web-automation-ui/venv/bin"
ExecStart=/path/to/pubcounter/web-automation-ui/venv/bin/python run_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable automation-web automation-worker
sudo systemctl start automation-web automation-worker

# Check status
sudo systemctl status automation-web
sudo systemctl status automation-worker
```

### 6. Configure Cloudflare Tunnel

Update your Cloudflare Tunnel configuration to route `/submit` to your Flask app:

```yaml
# In your Cloudflare Tunnel config.yml
ingress:
  - hostname: yourdomain.com
    path: /submit
    service: http://localhost:5000
  - hostname: yourdomain.com
    service: http://localhost:80  # Your other services
  - service: http_status:404
```

Restart Cloudflare Tunnel:
```bash
sudo systemctl restart cloudflared
```

### 7. Test Production Deployment

Navigate to: `https://yourdomain.com/submit`

## 📁 Project Structure

```
web-automation-ui/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models
│   ├── auth.py                  # Authentication routes
│   ├── main.py                  # Main app routes
│   ├── jobs.py                  # Job management routes
│   ├── crypto.py                # Encryption utilities
│   ├── forms.py                 # WTForms definitions
│   ├── worker.py                # RQ worker for job execution
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   └── submit.html
│   └── static/                  # Static assets
│       ├── css/
│       └── js/
├── config/                      # Configuration files
├── logs/                        # Application logs
├── config.py                    # Configuration classes
├── requirements.txt             # Python dependencies
├── run.py                       # Flask app entry point
├── run_worker.py                # RQ worker entry point
├── init_db.py                   # Database initialization script
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔧 Development Workflow

### Making Changes

1. **On your development machine:**
```bash
cd /home/a-robut/Documents/Github/pubcounter/web-automation-ui
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

2. **On your production server:**
```bash
cd /path/to/pubcounter
git pull origin main
cd web-automation-ui

# Restart services
sudo systemctl restart automation-web automation-worker
```

### Database Migrations

If you make changes to models:

```bash
# Development
flask db migrate -m "Description of changes"
flask db upgrade

# Commit migration files
git add migrations/
git commit -m "Add database migration"
git push origin main

# Production
git pull origin main
flask db upgrade
sudo systemctl restart automation-web
```

## 🎯 Usage

### For Admin Users

1. **Approve New Users:**
   - Log in as admin
   - Navigate to Admin Dashboard
   - Review pending user registrations
   - Approve or reject users

2. **Monitor Jobs:**
   - View all running and completed jobs
   - Check system health
   - View user statistics

### For Regular Users

1. **First Time Setup:**
   - Register an account
   - Wait for admin approval
   - Log in once approved

2. **Save Credentials (Optional but Recommended):**
   - Go to Profile Settings
   - Enter JW.org credentials
   - Credentials are encrypted with AES-256
   - You'll only need to do this once

3. **Submit a Job:**
   - Click "Submit New Job"
   - Select language
   - If credentials are saved, just click "Submit"
   - If not saved, enter credentials for this run only
   - Watch real-time progress
   - Receive Discord notification when complete

## 🔐 Security Best Practices

### For Deployment

1. **Never commit `.env` files** - they contain secrets
2. **Use strong SECRET_KEY** - generate with `secrets.token_hex(32)`
3. **Use unique CREDENTIAL_ENCRYPTION_KEY** - never reuse across environments
4. **Enable SESSION_COOKIE_SECURE** - requires HTTPS in production
5. **Keep dependencies updated** - regularly run `pip list --outdated`
6. **Use firewall** - only expose ports 80/443 via Cloudflare
7. **Regular backups** - backup the SQLite database regularly
8. **Monitor logs** - check `logs/` directory for suspicious activity

### For Users

1. **Use strong passwords** - minimum 12 characters
2. **Don't share accounts** - each user should have their own
3. **Verify HTTPS** - ensure you see the lock icon in browser
4. **Log out when done** - especially on shared computers

## 🐛 Troubleshooting

### "CREDENTIAL_ENCRYPTION_KEY not set"
```bash
# Generate a new key and add to .env
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Redis Connection Failed
```bash
# Check if Redis is running
docker ps | grep redis

# Or if installed locally
ps aux | grep redis-server

# Restart Redis
docker restart redis
# or
sudo systemctl restart redis
```

### Jobs Not Processing
```bash
# Check worker status
sudo systemctl status automation-worker

# View worker logs
sudo journalctl -u automation-worker -f

# Manually run worker for debugging
source venv/bin/activate
python3 run_worker.py
```

### Docker Compose Fails in Worker
```bash
# Check Docker socket permissions
sudo usermod -aG docker $USER

# Verify Docker path in .env
cat .env | grep DOCKER_AUTOMATION_PATH

# Test Docker manually
cd /path/to/selenium-inventory-submit
docker-compose up
```

## 📊 Monitoring

### View Application Logs
```bash
tail -f logs/app.log
```

### View Job Queue
```bash
source venv/bin/activate
python3
>>> from redis import Redis
>>> from rq import Queue
>>> redis_conn = Redis()
>>> queue = Queue(connection=redis_conn)
>>> print(f"Jobs in queue: {len(queue)}")
```

### Database Statistics
```bash
sqlite3 app.db "SELECT COUNT(*) FROM users;"
sqlite3 app.db "SELECT COUNT(*) FROM jobs WHERE status='completed';"
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit changes: `git commit -m "Add your feature"`
4. Push to GitHub: `git push origin feature/your-feature`
5. Create a Pull Request

## 📝 License

This project is private and proprietary.

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in `logs/app.log`
3. Check GitHub Issues
4. Contact the administrator

---

**Important Security Note:** This application handles sensitive authentication credentials. Always:
- Keep your `.env` file secure and never commit it to Git
- Use strong encryption keys
- Keep your server updated
- Monitor access logs
- Use HTTPS only in production