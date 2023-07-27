from picozk import *

import numpy as np

with PicoZKCompiler('picozk_test'):
    p = 2**31-1
    n = 100
    input_vec = [1,2,3,4]
    input_vec = [SecretInt(v) for v in input_vec]

    rvec = np.random.randint(0, p, (len(input_vec), len(input_vec)))

    state = np.array(input_vec)
    for _ in range(n):
        state = np.dot(rvec, state)

    print(state)
