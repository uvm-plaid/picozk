from functools import wraps
from io import StringIO

import picozk
from picozk import util, config
from picozk.wire import *

use_numpy = True
try:
    import numpy as np
except ImportError:
    use_numpy = False

def picozk_function(func):
    return func
