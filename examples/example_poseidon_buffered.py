from picozk import *
from picozk.poseidon_hash import BufferedPoseidonHash

p = 2**61-1
t = 3

with open('example_poseidon.py', 'r') as f:
    data = f.read()

with PicoZKCompiler('picozk_test'):
    poseidon_hash = BufferedPoseidonHash(p, alpha = 17, input_rate = t, t = t)
    for _ in range(10):
        for c in data:
            poseidon_hash.hash([SecretInt(ord(c))])
    digest = poseidon_hash.get_digest()
    reveal(digest)
