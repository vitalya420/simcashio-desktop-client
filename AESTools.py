import base64

from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class AESTools:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, message: str) -> tuple:
        message = pad(message.encode('utf-8'), 16)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        cipher_bytes = base64.b64encode(cipher.encrypt(message))
        return bytes.decode(cipher_bytes), iv

    def decrypt(self, encoded: bytes, iv: bytes) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_bytes = unpad(cipher.decrypt(encoded), 16)
        return bytes.decode(plain_bytes)

    def decrypt_client_msg(self, data: bytes) -> str:
        iv = data[:16]
        payload = data[16:-4]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_bytes = unpad(cipher.decrypt(payload), 16)
        return bytes.decode(plain_bytes)
