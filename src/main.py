
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random.random import getrandbits
from Crypto.Util.number import *
from obfuscation import ShuffleBlock
from compression import BWT, Compress, RunLength

# Get Data
cut_length = 1_000
f = open("sequences.fna", "r")
data = f.read().strip()

print("Original Data Length: ", len(data))

# Compress
# bwt = BWT()
# runlength = RunLength()

# seq_bwt = bwt.encode(data)
# seq_runlength = runlength.encode(seq_bwt)

compress = Compress()
seq_runlength = compress.encode(data)

# Generate Key

# Generate key for AES-GCM
bit_key_size = 256
initial_vector_size = 96

encryption_key = getrandbits(bit_key_size)
encryption_key_byte = long_to_bytes(encryption_key, blocksize=32)

nonce = getrandbits(initial_vector_size)
nonce_byte = long_to_bytes(nonce, blocksize=12)

# Generate RSA Pair Keys
rsa_key = RSA.generate(2048)
private_key = rsa_key.exportKey()

public_key = rsa_key.publickey()

cipher_rsa = PKCS1_OAEP.new(public_key)
encrypted_key = cipher_rsa.encrypt(encryption_key_byte)

# Shuffle
shuffle_block = ShuffleBlock(nonce)
shuffled_seq = shuffle_block.encode(seq_runlength)

# AES-GCM

encoded_data = shuffled_seq.encode('ISO-8859-1')
key = encryption_key_byte

print(
    f"Original length: {len(shuffled_seq)} vs Encoded length: {len(encoded_data)}")
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce_byte)
ciphertext, tag = cipher.encrypt_and_digest(encoded_data)

print(f"Encrypted size compare: {len(ciphertext)}, {len(encoded_data)}")
encrypted_result = nonce_byte + ciphertext + tag
print(f"final result length: {len(encrypted_result)}")

f = open('result.encrypted', 'wb')
f.write(encrypted_result)
f.close()


# Decryption
try:
    tag = encrypted_result[-16:]
    iv = encrypted_result[:12]
    ciphertext = encrypted_result[12:len(encrypted_result) - 16]

    priv_key = RSA.import_key(private_key)
    decrypt_rsa = PKCS1_OAEP.new(priv_key)
    key = decrypt_rsa.decrypt(encrypted_key)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)

    plaintext = cipher.decrypt_and_verify(ciphertext, tag).decode('ISO-8859-1')
    # print("The message was: " + str(plaintext))
except (ValueError, KeyError):
    print("Incorrect decryption")


# Decode Shuffle

unshuffled_seq = shuffle_block.decode(plaintext)
if unshuffled_seq == seq_runlength:
    print("Decode Shuffle OK")
else:
    print("Unshuffle not OK")

# Decompress
decoded = compress.decode(unshuffled_seq)

# seq_de_runlength = runlength.decode(unshuffled_seq)
# seq_de_bwt = bwt.decode(seq_de_runlength)

if decoded.replace('\n', '') == data.replace('\n', ''):
    print("Decode OK")
    
    diff = len(data) - len(encrypted_result)
    print(f"Compression Performace: {diff * 100 / len(data)}")

# if seq_de_bwt == data:
#     print("Decode BWT OK")
