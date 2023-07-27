from picozk import *

import numpy as np
import pandas as pd

with PicoZKCompiler('picozk_test'):
    df = pd.DataFrame(np.random.randint(0,100,size=(50000, 4)), columns=list('ABCD'))
    sdf = df.applymap(SecretInt)
    output = sdf['A'].sum()
    print(output)
    reveal(output)
