"""AES-256 encryption and password hashing"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from passlib.context import CryptContext
import base64
from ..config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_encryption_key() -> bytes:
    """Derive encryption key from settings"""
    kdf = PBKDF2(
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
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)

