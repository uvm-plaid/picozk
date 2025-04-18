from picozk import *
import time

NUM_INTS = 100

with PicoZKCompiler('picozk_test', field=97):
    start = time.time()

    int_list = list()
    binint_list = list()
    arith_int = SecretInt(5)
    for i in range(NUM_INTS):
        int_list.append(arith_int)
    print("Time to create ints: ", (time.time() - start))
    for i in int_list:
        binint_list.append(i.to_binary())

    print("Time to run: ", (time.time() - start))
