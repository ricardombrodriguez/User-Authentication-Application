import os
import secrets
import binascii
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
def encrypt(content, infile, password):

    # if the content received is null, there is nothing to encrypt    
    if not content:
        return

    verification = "success"                                            # message stored to later check if the decryption was successful (with the correct credentials)
    content = verification.encode('utf-8') + content.encode('utf-8')    # encode both the verification message and content to bytes
    padder = padding.PKCS7(128).padder()                                # initialize the padder
    data = padder.update(content) + padder.finalize()                   # add padding

    salt = bytes(secrets.token_hex(8), encoding="utf-8")                                                # generate salt (16 bytes)
    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf8"), salt, 50000, 32))   # generate key 
    digestkey = SHA256.new(key).digest()                                                                # hash of the generated key

    cipher = Cipher(algorithms.AES(digestkey), modes.CBC(salt), backend=default_backend())              # create aes cipher with the digestkey, CBC mode
    encryptor = cipher.encryptor()                                                                      # prepare to encrypt
    encrypted_data = salt + encryptor.update(data) + encryptor.finalize()                               # salt (not encrypted) + encrypted data

    fi = open(infile, 'wb')         
    fi.write(encrypted_data)        # store the salt + encrypted data in the file
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
    decryptor = cipher.decryptor()                                        # prepare to decrypt
    decrypted_data = decryptor.update(content) + decryptor.finalize()

    verification = decrypted_data[:7]
    if verification.decode('latin-1') != 'success':
        return False,False

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(decrypted_data) + unpadder.finalize()
    data = data[7:]
    fi.close()
    return data, False
