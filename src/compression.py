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
      chr(0): 4,
      chr(1): 5,
  }
  inv = {v: k for k, v in mp.items()}

  def encode(self, s):
    ofcnt = 0
    current = s[0]
    count = 0
    result = []
    for i in range(1, len(s)):
      if s[i] != current or count == 31:
        if count == 31:
          ofcnt += 1
        result.append(chr(self.mp[current] << 5 | count))
        current = s[i]
        count = 0
      else:
        count += 1
    print(ofcnt)
    result.append(chr(self.mp[current] << 5 | count))
    return ''.join(result)

  def decode(self, s):
    result = []
    for i in s:
      char = ord(i) >> 5
      count = ord(i) & 31
      result.append((count + 1) * self.inv[char])
    return ''.join(result)

class SplitPart():
  def encode(self, s):
    Dna = []
    Label = []
    for line in s.split('\n'):
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
      result.append(Dna[i])
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

    return [encodeDna, encodeLabel]

  def decode(self, Dna, Label):

    Dna = self.dnarunlength.decode(Dna)
    Dna = self.bwt.decode(Dna)

    Label = self.runlength.decode(Label)
    Label = self.bwt.decode(Label)

    return self.splitPart.decode(Dna, Label)
