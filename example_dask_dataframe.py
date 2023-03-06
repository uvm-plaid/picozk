import dask
from picowizpl import *

with PicoWizPLCompiler('miniwizpl_test'):
    df = dask.datasets.timeseries()
    s = df['id'].apply(SecretInt)
    #print(len(s))
    print(s.sum().compute())

