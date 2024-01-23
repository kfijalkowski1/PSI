from cryptography.fernet import Fernet
from config import aes_key


def encrypt(message):
    f = Fernet(aes_key)
    return f.encrypt(message)


def decrypt(my_encrypted_message):
    f = Fernet(aes_key)
    return f.decrypt(my_encrypted_message)