import base64
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import settings

logger = logging.getLogger(__name__)


class PasswordEncryption:
    """Utility class for encrypting and decrypting database passwords."""

    def __init__(self):
        self._fernet = None
        self._initialize_fernet()

    def _initialize_fernet(self):
        """Initialize the Fernet cipher using the secret key."""
        try:
            # Derive a key from the secret key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"dmcp_salt",  # Fixed salt for consistency
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
            self._fernet = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise

    def encrypt_password(self, password: str) -> str:
        """Encrypt a password."""
        if not password:
            return ""

        try:
            encrypted = self._fernet.encrypt(password.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt password: {e}")
            raise

    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt a password."""
        if not encrypted_password:
            return ""

        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            raise

    def is_encrypted(self, password: str) -> bool:
        """Check if a password is already encrypted."""
        if not password:
            return False

        try:
            # Try to decode as base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(password.encode())
            self._fernet.decrypt(encrypted_bytes)
            return True
        except Exception:
            return False


# Global instance
password_encryption = PasswordEncryption()
