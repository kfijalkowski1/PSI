from cryptography.fernet import Fernet
from config import aes_key
import logger


def encrypt(message):
    f = Fernet(aes_key)
    encrypted = f.encrypt(message)
    logger.debug(f"encrypted: {encrypted}")
    return encrypted


def decrypt(my_encrypted_message):
    f = Fernet(aes_key)
    decrypted = f.decrypt(my_encrypted_message)
    logger.debug(f"encrypted: {decrypted}")
    return decrypted
