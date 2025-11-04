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


if __name__ == '__main__':
    # Allow running this file directly to generate a key
    print("Generated Encryption Key:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file as:")
    print("ENCRYPTION_KEY=<key above>")