import os
import secrets
import binascii
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
def encrypt(content, infile, password):
    
    if not content:
        return

    content = content.encode('utf-8')
    padder = padding.PKCS7(128).padder()
    data = padder.update(content) + padder.finalize()

    salt = bytes(secrets.token_hex(8), encoding="utf-8")
    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf8"), salt, 50000, 32))
    digestkey = SHA256.new(key).digest()

    cipher = Cipher(algorithms.AES(digestkey), modes.CBC(salt), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = salt + encryptor.update(data) + encryptor.finalize()

    fi = open(infile, 'wb')
    fi.write(encrypted_data)
    fi.close()
    

def decrypt(infile, password):

    if os.path.getsize(infile) == 0:
        print("File is empty")
        return None, True

    fi = open(infile, 'rb')

    salt = fi.read(16)
    content = fi.read()
    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf-8"), salt, 50000, 32))
    digestkey = SHA256.new(key).digest()
    
    cipher = Cipher(algorithms.AES(digestkey), modes.CBC(salt), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(content) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()

    fi.close()
    return data, False
