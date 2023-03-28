from picozk import *

def kmp_zk(t, p):
    """return all matching positions of p in t"""
    next = ZKList([0 for _ in range(len(p))])
    j = 0
    for i in range(1, len(p)):
        for _ in range(len(p)):
            c0 = (j > 0) & (~(p[j] == p[i]))
            idx = mux(c0, j-1, 0)
            j = mux(c0,
                    next[idx],
                    j)
        j += mux(p[j] == p[i], 1, 0)
        next[i] = j
    j = 0
    found = 0
    for i in range(len(t)):
        for _ in range(len(p)):
            c = (j > 0) & (~(t[i] == p[j]))
            idx = mux(c, j-1, 0)
            j = mux(c,
                    next[idx],
                    j)
        j += mux(t[i] == p[j], 1, 0)

        c2 = j == len(p)
        found = mux(c2, 1, found)
        idx = mux(~c2, 0, j-1)
        j = mux(c2, next[idx], j)
    return found

with PicoZKCompiler('picozk_test', options=['ram']):
    p = ZKList([1, 2])
    t = ZKList([0, 1, 3, 2, 3, 1, 2, 3])
    r = kmp_zk(t, p)
    reveal(r)
    print(r)
