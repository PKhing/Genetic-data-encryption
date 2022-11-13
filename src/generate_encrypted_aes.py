from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

if __name__ == "__main__":
    fp = open('encryption_key.pem', 'rb')
    encryption_key_byte = fp.read()
    fp.close()

    fp = open('public_key.pem', 'rb')
    public_key = fp.read()
    fp.close()

    public_key = RSA.import_key(public_key)

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_key = cipher_rsa.encrypt(encryption_key_byte)

    fp = open('encrypted_key.pem', 'wb')
    fp.write(encrypted_key)
    fp.close()