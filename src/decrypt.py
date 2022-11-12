from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.number import *

from lib.compression import *
from lib.obfuscation import *

compress = Compress()

fp = open("result.encrypted", "rb")
encrypted_result = fp.read()
fp.close()

fp = open('private_key.pem', 'rb')
private_key = fp.read()
fp.close()

fp = open('encrypted_key.pem', 'rb')
encrypted_key = fp.read()

try:
    tag = encrypted_result[-16:]
    iv = encrypted_result[:12]
    ciphertext = encrypted_result[12:len(encrypted_result) - 16]

    priv_key = RSA.import_key(private_key)
    decrypt_rsa = PKCS1_OAEP.new(priv_key)
    key = decrypt_rsa.decrypt(encrypted_key)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    plaintext = cipher.decrypt_and_verify(ciphertext, tag).decode('ISO-8859-1')
except (ValueError, KeyError):
    print("Incorrect decryption")
    exit(1)

shuffle_block = ShuffleBlock(bytes_to_long(iv))
unshuffled_seq = shuffle_block.decode(plaintext)
decoded = compress.decode(unshuffled_seq)

fp = open("result.txt", "w")
fp.write(decoded)
fp.close()
