from picozk import *

with PicoZKEMPCompiler('picozk_test'):
    x = SecretInt(5)
    z = x
    for _ in range(2000):
        z = z + x * x
    reveal(z)
