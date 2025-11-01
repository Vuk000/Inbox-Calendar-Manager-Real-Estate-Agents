"""AES-256 encryption and password hashing"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
import base64
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing context - lazy initialization to avoid import-time errors
_pwd_context: Optional[CryptContext] = None


def _get_pwd_context() -> CryptContext:
    """Get or initialize password hashing context with error handling"""
    global _pwd_context
    if _pwd_context is None:
        try:
            _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            # Test initialization by hashing a test password
            _pwd_context.hash("test")
            logger.info("✅ Password hashing context initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize password hashing context: {e}")
            raise RuntimeError("Password hashing unavailable. Check bcrypt installation.") from e
    return _pwd_context


def _truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes (bcrypt limit).
    
    Args:
        password: Plain text password
        
    Returns:
        Truncated password (if needed)
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning("Password exceeds 72 bytes and will be truncated")
        truncated = password_bytes[:72].decode('utf-8', errors='ignore')
        return truncated
    return password


def _get_encryption_key() -> bytes:
    """Derive encryption key from settings"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.ENCRYPTION_SALT.encode(),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY.encode()))
    return key


# Initialize Fernet cipher
_cipher = Fernet(_get_encryption_key())


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt plaintext using AES-256.
    
    Args:
        plaintext: String to encrypt
        
    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""
    
    encrypted = _cipher.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt ciphertext using AES-256.
    
    Args:
        ciphertext: Base64-encoded encrypted string
        
    Returns:
        Decrypted plaintext
    """
    if not ciphertext:
        return ""
    
    decrypted = _cipher.decrypt(ciphertext.encode())
    return decrypted.decode()


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Truncate to 72 bytes (bcrypt limit)
    truncated_password = _truncate_password(password)
    
    try:
        pwd_context = _get_pwd_context()
        return pwd_context.hash(truncated_password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise RuntimeError("Failed to hash password") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches
    """
    if not plain_password or not hashed_password:
        return False
    
    # Truncate to 72 bytes (bcrypt limit)
    truncated_password = _truncate_password(plain_password)
    
    try:
        pwd_context = _get_pwd_context()
        return pwd_context.verify(truncated_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

