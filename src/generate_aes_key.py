
from Crypto.Random.random import getrandbits
from Crypto.Util.number import *

if __name__ == '__main__':
    bit_key_size = 256

    encryption_key = getrandbits(bit_key_size)
    encryption_key_byte = long_to_bytes(encryption_key, blocksize=32)

    fp = open('encryption_key.pem', 'wb')
    fp.write(encryption_key_byte)
    fp.close()
    
    