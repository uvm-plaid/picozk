from picozk import *
import sys

with PicoZKCompiler('picozk_test'):
    party = int(sys.argv[1])
    x = emp_bridge.EMPIntFp(5, party)
    z = x + x * x
    assert0(z + -30)
