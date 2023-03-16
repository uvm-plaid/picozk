from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test', field=7):
    x = SecretInt(5)
    y = SecretInt(6)

    xb = x.to_binary()
    yb = y.to_binary()
    
    eq1 = xb == yb
    assert0(eq1)
    print('x == y?', eq1)

    eq2 = xb == xb
    print('x == x?', eq2)
    assert0(eq2+1)

    eq3 = xb == 6
    print('x == 6?', eq3)
    assert0(eq3)
    

