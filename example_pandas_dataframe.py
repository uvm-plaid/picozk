from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    df = pd.DataFrame(np.random.randint(0,100,size=(500000, 4)), columns=list('ABCD'))
    sdf = df.applymap(SecretInt)
    output = sdf['A'].sum()
    print(output)
