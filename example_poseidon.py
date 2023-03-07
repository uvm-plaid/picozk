from picowizpl import *
from poseidon_hash import *
import galois

p = 2**61-1
gf = galois.GF(p)
t = 3
poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = t, t = t)

with open('example_poseidon.py', 'r') as f:
    data = f.read()

with PicoWizPLCompiler('miniwizpl_test'):
    secret_data = [SecretInt(ord(c)).as_gf(gf) for c in data]
    blocks = [secret_data[i * t:(i + 1) * t] for i in range((len(secret_data) + t - 1) // t )]

    for block in blocks:
        digest = poseidon_hash.hash(block)
    print(digest)
    assert0(digest - val_of(digest))
