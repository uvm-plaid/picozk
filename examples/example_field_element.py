from picowizpl import *
import galois
import numpy as np

with PicoWizPLCompiler('miniwizpl_test'):
    gf = galois.GF(97)
    #print(gf(5).__slots__)
    x = [SecretInt(gf(x)) for x in [1,2,3]]
    y = [SecretInt(gf(x)) for x in [5,6,7]]
    print(np.dot(x, y))
