from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    a = SecretInt(5)
    b = SecretInt(6)
    assert0((a == a) - 1)
    assert0(a == b)
    assert0(mux(a == b, 30, 0))
