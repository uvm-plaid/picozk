from picowizpl import *
import numpy as np
from scipy.sparse import csr_matrix

N = 20
K = 5

with PicoWizPLCompiler('miniwizpl_test'):
    arr = np.random.randint(0, 2, size=(N, N))
    csr_mat = csr_matrix(arr)
    csr_mat.data = [SecretInt(x) for x in csr_mat.data]
    vec = np.random.randint(0, 5, size=N)
    output = [0 for _ in range(N)]

    #print(csr_mat)
    for row in range(N):
        lower = csr_mat.indptr[row]
        upper = csr_mat.indptr[row+1]
        for data_idx in range(3000):
            if lower <= data_idx and data_idx < upper:
                mat_val = csr_mat.data[data_idx]
                col_idx = csr_mat.indices[data_idx]
                vec_val = vec[col_idx]
                print(mat_val)
                print(vec_val)
                output[row] += mat_val * int(vec_val)
    print(output)
    print(arr @ vec)
