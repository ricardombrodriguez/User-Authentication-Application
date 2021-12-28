from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64

class AES():

    # Symmetric key
    def __init__(self, key): 

        self.key = key
        self.block_size = AES.block_size
        AES.key_size[0]

    def encrypt(self, file):

        file = self.add_padding(file)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, IV=iv)
        return base64.b64encode(iv + cipher.encrypt(file.encode()))

    def decrypt(self, file):

        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, IV=iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def add_padding(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def remove_padding(s):
        return s[:-ord(s[len(s)-1:])]