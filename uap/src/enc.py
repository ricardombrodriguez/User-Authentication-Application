import os
import sys
import uuid
import secrets
import binascii
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(infile, outfile, key, algorithm='AES', mode='ECB', iv=None):
    
    if not os.path.exists(infile):
        print(f"Infile {infile} not found")
        return
    
    ''' if os.path.exists(outfile):
        r = input(f"Overwrite outfile: {outfile}? ")
        if r.upper != 'Y':
            return '''
            
    # iv = None
    key = SHA256.new(key).digest()
    # print("key in encrypt", key)
        
    # supported algorithms
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(key), cmode, backend=default_backend())

    ''' if iv is not None: # added for cipher mode
        with open(outfile+'.iv', 'wb') as f:
            f.write(iv) '''
            
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
        
        
    #fo.write("\n".encode())
    
    print("Data encrypted")
    
    fi.close()
    fo.close()
    
    return iv


def decrypt(infile, outfile, key, algorithm='AES', mode='ECB', iv=None):
    
    if not os.path.exists(infile):
        print(f"Infile {infile} not found")
        return
    
    ''' if os.path.exists(outfile):
        r = input(f"Overwrite outfile: {outfile}? ")
        if r.upper != 'Y':
            return '''
        
    # iv = None
    key = SHA256.new(key).digest()

    # supported algorithms
    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(key), cmode, backend=default_backend())
        
    '''if iv is not None: # added for cipher mode
        with open(outfile+'.iv', 'wb') as f:
            f.write(iv) '''
        
    
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

    

if __name__ == "__main__":
    
    # TODO : fazer que user faça input da key
    #! PROBLEM : a key tem de ser de 16, 32, 64, ... bytes, ou seja, n pode ser qqlr uma
    # TO RUN: python3 enc.py credentials.json password       ---- acho q ja consegui
    
    #key = os.urandom(16)
    message = sys.argv[1]
    password = sys.argv[2].encode('utf-8').strip()
    # print("pw :", password)
    
    # to derive a key from a password using the PBKDF2 algorithm
    salt = bytes(secrets.token_hex(8), encoding="utf8") # random salt for each encryption
    print("salt :", salt)
    iterations = 50000
    key = binascii.hexlify(pbkdf2_hmac("sha256", password, salt, iterations, 64))
    # print("key derived from pw :", key)
    
    with open("supersecret.txt", 'a') as ss:
        ss.write("password given: " + password.decode() +"\n")
        ss.write("unique salt: " + salt.decode() + "\n")
        ss.write("unique key generated from password and salt: " + key.decode() + "\n")
        ss.write("iterations: " + str(iterations) + "\n\n")
    
    algorithm = 'AES'
    # encrypt(message, message+".cgram", key, algorithm)
    # decrypt(message+".cgram", message+".txt", key, algorithm)

    # added for cipher mode
    m = message.split(".")[0] + '.ecb'
    dm = m + '.bmp'
    #m2 = message+'.cbc' 
    #dm2 = m2+'.bmp'
    
    encrypt(message, m, key, algorithm, 'ECB')
    
    r = input(f"Want to decrypt: {message}? ")
    if r.upper != 'Y': 
        decrypt(m, dm, key, algorithm, 'ECB')
    else:
        print("goodbye!")
    #iv = encrypt(message, m2, key, algorithm, 'CBC')
    #decrypt(m2, dm2, key, algorithm, 'CBC', iv)
