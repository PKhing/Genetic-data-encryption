from Crypto.PublicKey import RSA

if __name__ == '__main__':
    key_size = 2048

    rsa_key = RSA.generate(key_size)
    private_key = rsa_key.exportKey()
    fp = open('private_key.pem', 'wb')
    fp.write(private_key)
    fp.close()

    public_key = rsa_key.publickey().exportKey()
    fp = open('public_key.pem', 'wb')
    fp.write(public_key)
    fp.close()




