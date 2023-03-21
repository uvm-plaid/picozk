from picowizpl import *

def kmp(t, p):
    """return all matching positions of p in t"""
    next = [0 for _ in p]
    j = 0
    for i in range(1, len(p)):
        for _ in range(len(p)):
            if j > 0 and p[j] != p[i]:
                j = next[j - 1]
        if p[j] == p[i]:
            j += 1
        next[i] = j

    # the search part and build part is almost identical.
    ans = []
    j = 0
    for i in range(len(t)):
        for _ in range(len(p)):
            if j > 0 and t[i] != p[j]:
                j = next[j - 1]
        if t[i] == p[j]:
            j += 1
        if j == len(p):
            ans.append(i - (j - 1))
            j = next[j - 1]
    return ans

def kmp_zk_t(t, p):
    """return all matching positions of p in t"""
    next = [0 for _ in p]
    j = 0
    for i in range(1, len(p)):
        for _ in range(len(p)):
            if j > 0 and p[j] != p[i]:
                j = next[j - 1]
        if p[j] == p[i]:
            j += 1
        next[i] = j

    next = SecretIndexList(next)
    p = SecretIndexList(p)
    # the search part and build part is almost identical.
    ans = SecretStack(max_size=5)
    j = 0
    for i in range(len(t)):
        for _ in range(len(p)):
            c = (j > 0) & (~(t[i] == p[j]))
            idx = mux(c, j-1, 0)
            j = mux(c,
                    next[idx],
                    j)
        j += mux(t[i] == p[j], 1, 0)

        c = j == len(p)
        ans.cond_push(c, i - (j - 1))
        #print(j, .is_negative())
        idx = mux(~c, 0, j-1)
        j = mux(c, next[idx], j)
    return ans


def kmp_zk_both(t, p):
    """return all matching positions of p in t"""
    next = SecretIndexList([0 for _ in p])
    j = 0
    for i in range(1, len(p)):
        for _ in range(len(p)):
            j = mux(j > 0 and ~(p[j] == p[i]),
                    next[j - 1],
                    j)
        j += mux(p[j] == p[i], 1, 0)
        next[i] = j

    # TODO: fix below

    # the search part and build part is almost identical.
    ans = []
    j = 0
    for i in range(len(t)):
        for _ in range(len(p)):
            if j > 0 and t[i] != p[j]:
                j = next[j - 1]
        if t[i] == p[j]:
            j += 1
        if j == len(p):
            ans.append(i - (j - 1))
            j = next[j - 1]
    return ans

# def test():
#     p1 = "aa"
#     t1 = "aaaaaaaa"

#     assert(kmp(t1, p1) == [0, 1, 2, 3, 4, 5, 6])
#     print(kmp(t1, p1))

#     p2 = "abc"
#     t2 = "abdabeabfabc"

#     assert(kmp(t2, p2) == [9])

#     p3 = "aab"
#     t3 = "aaabaacbaab"

#     assert(kmp(t3, p3) == [1, 8])

#     print("all test pass")


# if __name__ == "__main__":
#     test()

with PicoWizPLCompiler('miniwizpl_test', options=['ram']):
    p = [1, 2]
    t = SecretIndexList([3, 4, 1, 2, 3, 1, 2])
    r = kmp_zk_t(t, p)
    print(r.ram.val)
