from obfuscation import ShuffleBlock
from Crypto.Util.number import bytes_to_long
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import json
import math
import random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Random.random import getrandbits
from Crypto.Util.number import *
from compression import BWT, RunLength

# Get Data
cut_length = 1_000
f = open("protein_sequences.fasta", "r")
data = f.read()[:cut_length]

# Compress
bwt = BWT()
runlength = RunLength()

seq_bwt = bwt.encode(data)
seq_runlength = runlength.encode(seq_bwt)

# Generate Key

# Generate key for AES-GCM
bit_key_size = 256
initial_vector_size = 96

encryption_key = getrandbits(bit_key_size)
encryption_key_byte = long_to_bytes(encryption_key)

nonce = getrandbits(initial_vector_size)
nonce_byte = long_to_bytes(nonce)

# Generate RSA Pair Keys
rsa_key = RSA.generate(2048)
private_key = rsa_key.exportKey()

public_key = rsa_key.publickey()

cipher_rsa = PKCS1_OAEP.new(public_key)
encrypted_key = cipher_rsa.encrypt(encryption_key_byte)

shuffle_block = ShuffleBlock()
# Shuffle
# block_size = int(math.sqrt(len(seq_runlength)))
# block_num = math.ceil(len(seq_runlength) / block_size)
# shuffle_seq = list(range(block_num))
# random.seed(nonce)
# random.shuffle(shuffle_seq)
# shuffled_seq = ""
# for i in shuffle_seq:
#   shuffled_seq += seq_runlength[i * block_size:(i + 1) * block_size]
shuffled_seq = shuffle_block.encode(seq_runlength, nonce)

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
  print("The message was: " + str(plaintext))
except (ValueError, KeyError):
  print("Incorrect decryption")


# Decode Shuffle

tlen = len(plaintext)

uns_block_size = int(math.sqrt(tlen))
uns_block_num = math.ceil(tlen / uns_block_size)
last_block = (tlen - 1) % uns_block_size + 1

unshuffle_index = list(range(uns_block_num))

random.seed(nonce)
random.shuffle(unshuffle_index)

index_dict = dict()
st = 0

for i in unshuffle_index:
  size = uns_block_size
  if i == uns_block_num - 1:
    size = last_block
  index_dict[i] = (st, st + size)
  st += size

unshuffled_seq = ""
for i in range(len(unshuffle_index)):
  st, ed = index_dict[i]
  unshuffled_seq += plaintext[st:ed]

if unshuffled_seq == seq_runlength:
  print("Decode Shuffle OK")
else:
  print("Unshuffle not OK")

# Decompress

seq_de_runlength = runlength.decode(unshuffled_seq)
seq_de_bwt = bwt.decode(seq_de_runlength)

if seq_de_runlength == seq_bwt:
  print("Decode Runlength OK")

if seq_de_bwt == data:
  print("Decode BWT OK")
