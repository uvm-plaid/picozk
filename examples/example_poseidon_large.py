from picozk import *
from picozk.poseidon_hash import PoseidonHash

import ecdsa

# Curve & generator parameters
g = ecdsa.ecdsa.generator_secp256k1
p = g.curve().p()
print('field size:', p)

# Create the hash function object
print('calculating hash parameters...')
poseidon_hash = PoseidonHash(p, alpha = 5, input_rate = 2)
print('done calculating parameters')

# Read the data
with open('example_poseidon.py', 'r') as f:
    data = f.read()

# Hash
with PicoZKCompiler('picozk_test', field=p):
    print('hashing this many field elements:', len(data))
    secret_data = [SecretInt(ord(c)) for c in data]
    digest = poseidon_hash.hash(secret_data)
    print(digest)
    assert0(digest - val_of(digest))
