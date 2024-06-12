from picozk import *
import sys

party = int(sys.argv[1])

with PicoZKCompiler(party):
    x = SecretInt(5)
    for _ in range(10000000):
        z = x * x
    #assert0(z + -30)

