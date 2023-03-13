from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    df = pd.DataFrame(np.random.randint(0,100,size=(50000, 4)), columns=list('ABCD'))
    sdf = df.applymap(SecretInt)
    output = sdf['A'].sum()
    print(output)
    assert0(output - val_of(output))
