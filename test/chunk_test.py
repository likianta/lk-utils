from lk_utils import chunkwise

seq = (1, 2, 3, 4)

print(tuple(chunkwise(seq, 2)))
print(tuple(chunkwise(seq, 2, 1)))
print(tuple(chunkwise(seq, 3)))
print(tuple(chunkwise(seq, 3, 1)))
print(tuple(chunkwise(seq, 3, 2)))

print(tuple(chunkwise(seq, 2, 0, False)))
print(tuple(chunkwise(seq, 2, 1, False)))
print(tuple(chunkwise(seq, 3, 0, False)))
print(tuple(chunkwise(seq, 3, 1, False)))
print(tuple(chunkwise(seq, 3, 2, False)))
