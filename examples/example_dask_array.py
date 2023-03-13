import dask
import dask.array as da
import dask.dataframe as dd
from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    y = da.random.randint(1, 10, 100000)
    ddf = dd.from_dask_array(y, columns=['A'])
    sdf = ddf.applymap(SecretInt)
    ss = sdf['A']
    print(ss.sum().compute())

