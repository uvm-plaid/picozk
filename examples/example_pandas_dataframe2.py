from picowizpl import *
import pandas as pd

# def series_eq(a, b):
#     if isinstance(b, int):
#         return a.apply(lambda x: x == b)
#     else:
#         raise Exception('unsupported')

# pd.Series.__eq__ = series_eq

with PicoWizPLCompiler('miniwizpl_test'):
    df = pd.DataFrame(np.random.randint(0,10,size=(500, 4)), columns=list('ABCD'))
    sdf = df.applymap(SecretInt)
    idx = sdf['A'].apply(lambda x: (x == 5).to_arith())
    filtered = sdf.mul(idx, axis=0)
    total = filtered['D'].sum()
    print('total sum after filtering:', total)

    assert0(total - val_of(total))
