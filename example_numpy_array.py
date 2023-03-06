import numpy as np
from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    y = np.random.randint(1, 10, 10000)
    sy = np.array([SecretInt(x) for x in y])
    z = sy.sum()
    print(z)
