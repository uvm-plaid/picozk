from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    x = SecretInt(5)
    z = x + x * x
    assert0(z + -30)



