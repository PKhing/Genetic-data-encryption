import compression

# Get Data
cut_length = 1_000_000
f = open("protein_sequences.fasta", "r")
data = f.read()[:cut_length]

# Compress
bwt = compression.BWT()
runlength = compression.RunLength()

seq_bwt = bwt.encode(data)
seq_runlength = runlength.encode(seq_bwt)
