from picowizpl import *
from picowizpl.poseidon_hash import PoseidonHash

p = 2**61-1
t = 3
poseidon_hash = PoseidonHash(p, alpha = 17, input_rate = t, t = t)

with open('example_poseidon.py', 'r') as f:
    data = f.read()

with PicoWizPLCompiler('miniwizpl_test'):
    secret_data = [SecretInt(ord(c)) for c in data]
    digest = poseidon_hash.hash(secret_data)
    assert0(digest - val_of(digest))
