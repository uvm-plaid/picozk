import numpy as np
from picozk import *

with PicoZKCompiler('picozk_test'):
    y = np.random.randint(1, 10, 10000)
    sy = np.array([SecretInt(x) for x in y])
    z = sy.sum()
    print(z)
