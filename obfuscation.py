import math
import random

class ShuffleBlock():

  def encode(self, string, nonce):
    block_size = int(math.sqrt(len(string)))
    block_num = math.ceil(len(string) / block_size)
    shuffle_seq = list(range(block_num))
    random.seed(nonce)
    random.shuffle(shuffle_seq)
    shuffled_seq = ""
    for i in shuffle_seq:
      shuffled_seq += string[i * block_size:(i + 1) * block_size]
    return shuffled_seq
