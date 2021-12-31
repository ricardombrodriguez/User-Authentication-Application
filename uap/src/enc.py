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

    key = binascii.hexlify(pbkdf2_hmac("sha256",  bytes(password, encoding="utf8"), salt, iterations, 32))
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

    fi = open(infile, 'rb')
    if key:
        print("Há dados")

        digestkey = SHA256.new(key).digest()
            
        # supported algorithms
        block_size = 256
        block_size = algorithms.AES.block_size // 8
        cmode = modes.ECB()
        cipher = Cipher(algorithms.AES(digestkey), cmode, backend=default_backend())
        
        fo = open(outfile, 'wb')
        decryptor = cipher.decryptor()
        
        total_bytes = os.path.getsize(infile) 
        print("block size", block_size)
        print("total bytes", total_bytes)
        read_bytes = 0
        
        while True:
            cgram = fi.read(block_size)
            read_bytes += len(cgram)
            if read_bytes == total_bytes:
                # this is the last block
                print("esta no padding")
                text = decryptor.update(cgram)
                print(text)
                if not text:break
                padding = text[-1]
                text = text[0:block_size - padding]
                fo.write(text)
                break
            else:
                print("não esta no padding")
        
            text = decryptor.update(cgram)
            print(text)
            fo.write(text)
        
        print("Data decrypted")
        
        fi.close()
        fo.close()
    
    else:
        print("Não há dados")
    
""" 
if __name__ == "__main__":

    # TODO : fazer que user faça input da key
    #! PROBLEM : a key tem de ser de 16, 32, 64, ... bytes, ou seja, n pode ser qqlr uma
    # TO RUN: python3 enc.py credentials.json password       ---- acho q ja consegui

    infile = 'credentials.json'
    outfile = 'cred.json'
    outfile2 = 'cred2.json'
    password = 'admin'

    # decrypt(infile, outfile, returned_key, 'AES', 'ECB')

    returned_key = encrypt(infile, outfile, password, 'AES', 'ECB')

    decrypt(outfile, outfile2, returned_key, 'AES', 'ECB')
     """

