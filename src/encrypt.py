import sys

from Crypto.Random.random import getrandbits
from Crypto.Util.number import *
from Crypto.Cipher import AES

from lib.compression import *
from lib.obfuscation import *

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python encrypt.py <input_file> <encryption_key_file> <output_file>")
        exit(1)
    
    input_file = sys.argv[1]
    encryption_key_file = sys.argv[2]
    output_file = sys.argv[3]

    f = open(input_file, "r")
    data = f.read().strip()

    initial_vector_size = 96

    nonce = getrandbits(initial_vector_size)
    nonce_byte = long_to_bytes(nonce, blocksize=12)

    compress = Compress()
    seq_runlength = compress.encode(data)

    shuffle_block = ShuffleBlock(nonce)
    shuffled_seq = shuffle_block.encode(seq_runlength)

    encoded_data = shuffled_seq.encode('ISO-8859-1')

    fp = open(encryption_key_file, 'rb')
    key = fp.read()

    print(
        f"Original length: {len(shuffled_seq)} vs Encoded length: {len(encoded_data)}")
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce_byte)
    ciphertext, tag = cipher.encrypt_and_digest(encoded_data)

    print(f"Encrypted size compare: {len(ciphertext)}, {len(encoded_data)}")
    encrypted_result = nonce_byte + ciphertext + tag
    print(f"final result length: {len(encrypted_result)}")

    f = open(output_file, 'wb')
    f.write(encrypted_result)
    f.close()