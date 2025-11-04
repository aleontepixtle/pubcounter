from cryptography.fernet import Fernet
from flask import current_app
import base64


class CredentialEncryption:
    """Handle encryption and decryption of sensitive credentials."""
    
    @staticmethod
    def get_cipher():
        """Get Fernet cipher from app config."""
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError(
                'ENCRYPTION_KEY not set in configuration. '
                'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )
        return Fernet(key.encode() if isinstance(key, str) else key)
    
    @staticmethod
    def encrypt(plaintext):
        """Encrypt a string and return base64 encoded encrypted data."""
        if not plaintext:
            return None
        
        cipher = CredentialEncryption.get_cipher()
        encrypted = cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypted_text):
        """Decrypt base64 encoded encrypted data and return plaintext."""
        if not encrypted_text:
            return None
        
        cipher = CredentialEncryption.get_cipher()
        encrypted = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted)
        return decrypted.decode('utf-8')
    
    @staticmethod
    def encrypt_credentials(username, password, totp_secret):
        """Encrypt all three credentials and return a dict."""
        return {
            'username': CredentialEncryption.encrypt(username),
            'password': CredentialEncryption.encrypt(password),
            'totp_secret': CredentialEncryption.encrypt(totp_secret)
        }
    
    @staticmethod
    def decrypt_credentials(encrypted_username, encrypted_password, encrypted_totp_secret):
        """Decrypt all three credentials and return a dict."""
        return {
            'username': CredentialEncryption.decrypt(encrypted_username),
            'password': CredentialEncryption.decrypt(encrypted_password),
            'totp_secret': CredentialEncryption.decrypt(encrypted_totp_secret)
        }


def generate_encryption_key():
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()

from flask import Blueprint, render_template, redirect, url_for, request, flash

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.forms import LoginForm
    from app.models import User
    from flask_login import login_user

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Account is deactivated. Contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))
            if not user.is_approved:
                flash('Your account is not yet approved. Please wait for administrator approval.', 'warning')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.forms import RegistrationForm
    from app.models import User

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user; by default users are not approved until an admin enables them
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_approved=False,
            is_admin=False
        )
        user.set_password(form.password.data)
        from app import db
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Your account will be reviewed by an administrator.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Allow running this file directly to generate a key
    print("Generated Encryption Key:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file as:")
    print("ENCRYPTION_KEY=<key above>")