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

class DnaRunLength():
  mp = {
      'A': 0,
      'T': 1,
      'C': 2,
      'G': 3,
      'N': 4,
      'a': 5,
      't': 6,
      'c': 7,
      'g': 8,
      chr(0): 9,
      chr(1): 10,
  }
  inv = {v: k for k, v in mp.items()}

  def encode(self, s):
    ofcnt = 0
    current = s[0]
    count = 0
    result = []
    for i in range(1, len(s)):
      if s[i] != current or count == 15:
        if count == 15:
          ofcnt += 1
        result.append(chr(self.mp[current] << 4 | count))
        current = s[i]
        count = 0
      else:
        count += 1
    result.append(chr(self.mp[current] << 4 | count))
    return ''.join(result)

  def decode(self, s):
    result = []
    for i in s:
      char = ord(i) >> 4
      count = ord(i) & 15
      result.append((count + 1) * self.inv[char])
    return ''.join(result)

class SplitPart():
  def encode(self, s):
    Dna = []
    Label = []
    for line in s.split('\n'):
      if line == '':
        continue
      if line[0] == '>':
        Label.append(line)
        Dna.append("")
      else:
        Dna[len(Dna) - 1] += line
    Label = chr(1).join(Label)
    Dna = chr(1).join(Dna)
    return [Dna, Label]

  def decode(self, Dna, Label):
    Dna = Dna.split(chr(1))
    Label = Label.split(chr(1))
    result = []
    for i in range(len(Label)):
      result.append(Label[i])

      # Add \n to every 80 characters in Dna
      for j in range(0, len(Dna[i]), 80):
        result.append(Dna[i][j:j + 80])
        
    return '\n'.join(result)


class Compress():
  bwt = BWT()
  runlength = RunLength()
  dnarunlength = DnaRunLength()
  splitPart = SplitPart()

  def encode(self, s):
    [Dna, Label] = self.splitPart.encode(s)

    encodeDna = self.bwt.encode(Dna)
    encodeDna = self.dnarunlength.encode(encodeDna)

    encodeLabel = self.bwt.encode(Label)
    encodeLabel = self.runlength.encode(encodeLabel)

    last_bit = []
    length = len(encodeLabel)
    for _ in range(12):
        last_bit.append(length % 256)
        length //= 256
    last_bit = last_bit[::-1]

    encodedResult = encodeLabel + encodeDna + "".join([chr(i) for i in last_bit])
    return encodedResult

  def decode(self, data):
    label_size = data[-12:]
    label_size = [ord(i) for i in label_size][::-1]
    now = 0
    for i in range(12):
        now += label_size[i] * (256 ** i)

    Label = data[:now]
    Dna = data[now:-12]

    Dna = self.dnarunlength.decode(Dna)
    Dna = self.bwt.decode(Dna)

    Label = self.runlength.decode(Label)
    Label = self.bwt.decode(Label)

    return self.splitPart.decode(Dna, Label)
