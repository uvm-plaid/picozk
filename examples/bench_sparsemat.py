from picowizpl import *
import numpy as np
from scipy.sparse import csr_matrix
from dataclasses import dataclass

from typing import Dict, Tuple

N = 20
K = 5

ZKSparseMatrix = Dict[Tuple[ArithmeticWire, ArithmeticWire], ArithmeticWire]

def sparse_mult(sparse_mat: ZKSparseMatrix, vec: SecretIndexList) -> SecretIndexList:
    output = SecretIndexList([0 for _ in range(len(vec))])

    for (i, j), v in sparse_mat.items():
        output[i] = output[i] + secret_vec[j] * v

    return output

with PicoWizPLCompiler('miniwizpl_test', options=['ram']):
    arr = np.zeros((N, N))
    sparse_mat = {}
    all_is = np.random.choice(range(0, N), size=K)
    all_js = np.random.choice(range(0, N), size=K)
    for i, j in zip(all_is, all_js):
        v = np.random.randint(0, 100)
        arr[i, j] = v
        sparse_mat[(SecretInt(i), SecretInt(j))] = SecretInt(v)

    vec = np.random.randint(0, 5, size=N)
    secret_vec = SecretIndexList(list(vec))

    output = sparse_mult(sparse_mat, secret_vec)
    for i in range(len(output)):
        reveal(output[i])
