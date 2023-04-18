import numpy as np
from picozk import *

with PicoZKCompiler('picozk_test'):

    SecretMatrix = np.vectorize(SecretInt)
    a = SecretMatrix(np.random.randint(1, 10, size=(50, 5)))
    b = SecretMatrix(np.random.randint(1, 10, size=(5, 3)))
    c = a @ b

    reveal_matrix = np.vectorize(reveal)
    reveal_matrix(c)
