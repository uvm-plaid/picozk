from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    x = SecretInt(5)
    z = x + x
    z = z + 1
    z = z + SecretInt(10)
    print(z)


