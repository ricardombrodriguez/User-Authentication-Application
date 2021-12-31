import os
import sys
import secrets
import binascii
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
def encrypt(infile, outfile, password, algorithm='AES', mode='ECB', iv=None):
    
    if not os.path.exists(infile):
        print(f"Infile {infile} not found")
        return

    # to derive a key from a password using the PBKDF2 algorithm
    salt = bytes(secrets.token_hex(8), encoding="utf8") # random salt for each encryption
    iterations = 50000
    key = binascii.hexlify(pbkdf2_hmac("sha256", password, salt, iterations, 32))
    digestkey = SHA256.new(key).digest()
        
    # supported algorithms
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(digestkey), cmode, backend=default_backend())

    fi = open(infile, 'rb')
    fo = open(outfile, 'wb')
    
    encryptor = cipher.encryptor()
    
    while True:
        text = fi.read(block_size)
        if len(text) != 16:
            missing_len = 16 - len(text)
            text += bytes([missing_len]*missing_len)
            cryptogram = encryptor.update(text) + encryptor.finalize()
            fo.write(cryptogram)
            break
    
        cryptogram = encryptor.update(text)
        fo.write(cryptogram)
        
    print("Data encrypted")
    
    fi.close()
    fo.close()
    
    print(key)
    return key

def decrypt(infile, outfile, key, algorithm='AES', mode='ECB', iv=None):
    
    if not os.path.exists(infile):
        print(f"Infile {infile} not found")
        return

    digestkey = SHA256.new(key).digest()
        
    # supported algorithms
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(digestkey), cmode, backend=default_backend())
    
    fi = open(infile, 'rb')
    fo = open(outfile, 'wb')
    decryptor = cipher.decryptor()
    
    total_bytes = os.path.getsize(infile) 
    read_bytes = 0
    
    while True:
        cgram = fi.read(block_size)
        read_bytes += len(cgram)
        if read_bytes == total_bytes:
            # this is the last block
            text = decryptor.update(cgram)
            padding = text[-1]
            text = text[0:block_size - padding]
            fo.write(text)
            break
    
        text = decryptor.update(cgram)
        fo.write(text)
    
    print("Data decrypted")
    
    fi.close()
    fo.close()
    

# FUNCIONA ENCRIPTAR CREDENTIALS.JSON E DEPOIS DESENCRIPTAR CREDENTIALS.ECB
if __name__ == "__main__":
    
    # TODO : fazer que user faça input da key
    #! PROBLEM : a key tem de ser de 16, 32, 64, ... bytes, ou seja, n pode ser qqlr uma
    # TO RUN: python3 enc.py credentials.json password       ---- acho q ja consegui

    message = sys.argv[1]
    password = sys.argv[2].encode('utf-8').strip()

    m = message.split(".")[0] + '.json'
    dm = m.split(".")[0] + '.json'
    
    returned_key = encrypt(message, m, password, 'AES', 'ECB')
    print(returned_key)
    
    decrypt(m, dm, returned_key, 'AES', 'ECB')
    

