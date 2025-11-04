#!/bin/bash

# Web Automation UI Setup Script
# This script helps you set up the environment quickly

set -e  # Exit on error

echo "========================================="
echo "  Inventory Submission Portal Setup"
echo "========================================="
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Copy example environment file
cp .env.example .env
echo "✅ Created .env file from template"

# Generate SECRET_KEY
echo "🔐 Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i.bak "s/your-secret-key-here-change-this-to-something-random-and-long/$SECRET_KEY/" .env
echo "✅ SECRET_KEY generated"

# Generate ENCRYPTION_KEY
echo "🔐 Generating ENCRYPTION_KEY..."
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
sed -i.bak "s/your-fernet-encryption-key-here/$ENCRYPTION_KEY/" .env
echo "✅ ENCRYPTION_KEY generated"

# Clean up backup file
rm -f .env.bak

echo ""
echo "========================================="
echo "  Configuration Required"
echo "========================================="
echo ""
echo "Please edit .env and update the following:"
echo "  1. ADMIN_EMAIL - Your admin email address"
echo "  2. N8N_WEBHOOK_URL - Your n8n webhook for Discord notifications (optional)"
echo "  3. DOMAIN - Your production domain name"
echo "  4. AUTOMATION_SCRIPT_PATH - Path to your selenium automation script"
echo ""
echo "For development, you can leave other settings as-is."
echo ""

read -p "Would you like to edit .env now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    ${EDITOR:-nano} .env
fi

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Build and start services:"
echo "     docker-compose up --build -d"
echo ""
echo "  2. View logs:"
echo "     docker-compose logs -f"
echo ""
echo "  3. Access the application:"
echo "     http://localhost:5000"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the admin password immediately after first login!"
echo ""