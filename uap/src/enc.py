from datetime import time
import os
import sys
import secrets
import binascii
import tempfile
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
def encrypt(infile, outfile, password, algorithm='AES', mode='ECB', iv=None):

    print("encryption:")
    
    if not infile:
        print(f"Infile {infile} is null")
        return

    salt = bytes(secrets.token_hex(8), encoding="utf8")
    iterations = 50000
    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf8"), salt, iterations, 32))
    digestkey = SHA256.new(key).digest()
    print("digest key (encrypt):")
    print(digestkey)
        
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(digestkey), cmode, backend=default_backend())

    print("fiii")

    with open(infile.name) as fi:

        fo = open(outfile, 'wb')
        fo.write(salt + "\n".encode('utf-8'))    

        
        encryptor = cipher.encryptor()
        
        print("text::::")
        while True:
            text = fi.read(block_size).encode('utf-8')
            print(text)
            if len(text) != block_size:
                missing_len = block_size - len(text)
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
        return 
    

def decrypt(infile, password, algorithm='AES', mode='ECB', iv=None):
    
    temp = tempfile.NamedTemporaryFile(mode="a+")

    if not os.path.exists(infile):
        print(f"Infile {infile} not found")
        return

    if os.path.getsize(infile) == 0:
        print("File is empty")
        return temp, True

    fi = open(infile, 'rb')

    salt = fi.readline().replace(b'\n',b'')
    print("salt: ", salt)
    iterations = 50000
    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf8"), salt, iterations, 32))
    digestkey = SHA256.new(key).digest()

    print("digest key (decrypt):")
    print(digestkey)
    
    # supported algorithms
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(digestkey), cmode, backend=default_backend())
    
    decryptor = cipher.decryptor()
    
    total_bytes = os.path.getsize(infile) - len(salt) + 1
    print(total_bytes)
    read_bytes = 0

    while True:
        fi.seek(read_bytes)
        cgram = fi.read(block_size)
        read_bytes += len(cgram)
        if read_bytes == total_bytes:
            print("padding!")
            text = decryptor.update(cgram)
            if not text:
                break
            padding = text[-1]
            text = text[0:block_size - padding]
            temp.write(text.decode('utf-8',errors='ignore'))
            break
    
        text = decryptor.update(cgram).decode('utf-8',errors='ignore')
        print(text)
        temp.write(text)
    
    print("Data decrypted")
    
    fi.close()
    return temp, False
    
 
if __name__ == "__main__":

    # TODO : fazer que user faça input da key
    #! PROBLEM : a key tem de ser de 16, 32, 64, ... bytes, ou seja, n pode ser qqlr uma
    # TO RUN: python3 enc.py credentials.json password       ---- acho q ja consegui

    infile = 'credentials.txt'
    outfile = 'cred.txt'
    outfile2 = 'cred2.txt'
    password = 'admin'

    # decrypt(infile, outfile, returned_key, 'AES', 'ECB')

    returned_key = encrypt(infile, outfile, password, 'AES', 'ECB')

    decrypt(outfile, outfile2, returned_key, 'AES', 'ECB')

