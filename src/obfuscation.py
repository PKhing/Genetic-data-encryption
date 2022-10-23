import math
import random

class ShuffleBlock():
  def __init__(self, nonce):
    self.nonce = nonce

  def encode(self, string):
    block_size = int(math.sqrt(len(string)))
    block_num = math.ceil(len(string) / block_size)
    shuffle_seq = list(range(block_num))
    random.seed(self.nonce)
    random.shuffle(shuffle_seq)
    shuffled_seq = ""
    for i in shuffle_seq:
      shuffled_seq += string[i * block_size:(i + 1) * block_size]
    return shuffled_seq

  def decode(self, string):
    tlen = len(string)

    uns_block_size = int(math.sqrt(tlen))
    uns_block_num = math.ceil(tlen / uns_block_size)
    last_block = (tlen - 1) % uns_block_size + 1

    unshuffle_index = list(range(uns_block_num))

    random.seed(self.nonce)
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
      unshuffled_seq += string[st:ed]
    return unshuffled_seq
