import json
import os
import secrets
import binascii
from Crypto.Hash import SHA256
from backports.pbkdf2 import pbkdf2_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt(infile, outfile, password, algorithm='AES', mode='ECB', iv=None):

    if not os.path.exists(outfile):
        print(f"[ERROR] File {outfile} not found")
        return
    
    dkey = SHA256.new(key).digest()
    print(dkey)

    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(dkey), cmode, backend=default_backend())
            
    fi = json.dumps(infile)
    print(fi)
    fo = open(outfile, 'wb')
    
    encryptor = cipher.encryptor()

    binary = ' '.join(format(ord(letter), 'b') for letter in fi)
    total_bytes = len(binary)
    print("total bytes", total_bytes)

    print("X:")
    for x in range(0, total_bytes, 16):
        print(x)
        print(len(binary))
        if len(binary) < 16:
            print("len menor que 16")
            missing_len = 16 - len(binary)
            binary += bytes([missing_len]*missing_len)
            cryptogram = encryptor.update(binary) + encryptor.finalize()
            fo.write(cryptogram)
        
        block = binary[x:x+16]
        bin_block = bytes(block,'UTF-8')
        cryptogram = encryptor.update(bin_block)
        #binary = binary[x+16:]
        fo.write(cryptogram)
    
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

    fo.close()
    
    return fo


def decrypt(infile, password, algorithm='AES', mode='ECB'):
    
    if not os.path.exists(infile):
        print(f"[ERROR] File {infile} not found")
        return
    
    password = password.encode('utf-8').strip()
    salt = bytes(secrets.token_hex(8), encoding="utf8")
    iterations = 100000
    key = binascii.hexlify(pbkdf2_hmac("sha256", password, salt, iterations, 32))
    print(key)
    dkey = SHA256.new(key).digest()
    print(dkey)

    block_size = 256
    block_size = algorithms.AES.block_size // 8
    cmode = modes.ECB()
    cipher = Cipher(algorithms.AES(dkey), cmode, backend=default_backend())
    
    fi = open(infile, 'rb')
    decryptor = cipher.decryptor()
    
    total_bytes = os.path.getsize(infile) 
    read_bytes = 0

    print("total bytes")
    print(total_bytes)

    content = ""
    
    while True:
        cgram = fi.read(32)
        read_bytes += len(cgram)
        if read_bytes == total_bytes:
            # padding block
            print("padding block")
            text = decryptor.update(cgram)
            if not text: break
            padding = text[-1]
            text = text[0:block_size - padding]
            content += text.decode("utf-8")
            break
        else:
            print("reading...")
    
        text = decryptor.update(cgram)
        print("--------> TEXT ", text)
        content += text.decode("utf-8")
    
    print("Data decrypted")
    print(content)
    print(type(content))
    fi.close()
    if content:
        content = json.loads(content)
    return (content, salt, key) # esta  key é p ser usada no encrypt mas ainda n consigo fazer decrypt->encrypt, só encrypt->decrypt

    

""" if __name__ == "__main__":

    message = sys.argv[1]
    password = sys.argv[2].encode('utf-8').strip()

    salt = bytes(secrets.token_hex(8), encoding="utf8")
    iterations = 100000
    key = binascii.hexlify(pbkdf2_hmac("sha256", password, salt, iterations, 32))
    
    with open("supersecret.txt", 'a') as ss:
        ss.write("password given: " + password.decode() +"\n")
        ss.write("unique salt: " + salt.decode() + "\n")
        ss.write("unique key generated from password and salt: " + key.decode() + "\n")
        ss.write("iterations: " + str(iterations) + "\n\n")
    
    algorithm = 'AES'

    m = message.split(".")[0] + '.ecb'
    dm = m + '.bmp'
    #m2 = message+'.cbc' 
    #dm2 = m2+'.bmp'
    
    encrypt(message, m, key, algorithm, 'ECB')
    
    r = input(f"Want to decrypt {message}? ")
    if r.upper != 'Y': 
        decrypt(m, dm, key, algorithm, 'ECB')
    else:
        print("goodbye!")
    #iv = encrypt(message, m2, key, algorithm, 'CBC')
    #decrypt(m2, dm2, key, algorithm, 'CBC', iv)
 """