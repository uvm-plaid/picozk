import dask
from picowizpl import *

open_picowizpl('miniwizpl_test')

df = dask.datasets.timeseries()
s = df['id'].apply(SecretInt)
#print(len(s))
print(s.sum().compute())

close_picowizpl()
