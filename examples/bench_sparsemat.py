from picowizpl import *
import numpy as np
from scipy.sparse import csr_matrix

N = 20
K = 5

with PicoWizPLCompiler('miniwizpl_test', options=['ram']):
    arr = np.zeros((N, N))
    sparse_arr = {}
    all_is = np.random.choice(range(0, N), size=K)
    all_js = np.random.choice(range(0, N), size=K)
    for i, j in zip(all_is, all_js):
        v = np.random.randint(0, 100)
        arr[i, j] = v
        sparse_arr[(SecretInt(i), SecretInt(j))] = SecretInt(v)

    print(sparse_arr)

    vec = np.random.randint(0, 5, size=N)
    secret_vec = SecretIndexList(list(vec))
    output = SecretIndexList([0 for _ in range(N)])

    for (i, j), v in sparse_arr.items():
        output[i] = output[i] + secret_vec[j] * v

    # print(output)
    # print(arr @ vec == output)
