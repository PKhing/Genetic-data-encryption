from pysuffixarray.core import SuffixArray

class SuffixArrayFixed(SuffixArray):
  def __init__(self, string):
    self.string = string + chr(0)
    self.sa = self._construct_suffix_array(self.string)

class BWT():
  def __bwt_with_index(self, bwt):
    no = [0] * 256
    result = []
    for char in bwt:
      idx = ord(char)
      result.append((char, no[idx]))
      no[idx] += 1
    return result

  def __get_bwt_map(self, bwt):
    sortedBwt = sorted(bwt)
    return (sortedBwt[0], {sortedBwt[i]: bwt[i] for i in range(len(bwt))})

  def encode(self, s):
    suffix_array = SuffixArrayFixed(s).suffix_array()
    s = s + chr(0)
    return "".join([s[suffix_array[i] - 1] for i in range(len(s))])

  def decode(self, bwt):
    bwt = self.__bwt_with_index(bwt)
    (current, bwt_map) = self.__get_bwt_map(bwt)
    result = ""
    while True:
      result += current[0]
      current = bwt_map[current]
      if current == (chr(0), 0):
        return result[:0:-1]

class RunLength():
  def encode(self, s):
    current = s[0]
    count = 1
    charlen = []
    for i in range(1, len(s)):
      if s[i] != current or count == 255:
        charlen.append((current, count))
        current = s[i]
        count = 0
      count += 1
    charlen.append((current, count))
    while len(charlen) % 8 != 0:
      charlen.append((chr(0), 0))

    result = []
    for i in range(0, len(charlen), 8):
      cnt = 0
      for j in range(i, i + 8):
        cnt *= 2
        if charlen[j][1] == 1:
          cnt += 1
      result.append(chr(cnt))
      for j in range(i, i + 8):
        result.append(charlen[j][0])
        if charlen[j][1] != 1:
          result.append(chr(charlen[j][1]))
    return "".join(result)

  def decode(self, s):
    pos = 0
    result = []
    current = 0
    cnt = 8

    while pos < len(s):
      if cnt == 8:
        cnt = 0
        current = ord(s[pos])
        pos += 1

      a = s[pos]
      b = 1
      pos += 1
      if current & (1 << 7) == 0:
        b = ord(s[pos])
        pos += 1
      current *= 2
      cnt += 1
      result.append(a * b)
    return "".join(result)
