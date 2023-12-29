import numpy as np


def to_db(value):
    if value is None:
        return value

    if isinstance(value, np.ndarray):
        if value.ndim != 1:
            raise ValueError('expected ndim to be 1')

        if not np.issubdtype(value.dtype, np.integer) and not np.issubdtype(value.dtype, np.floating):
            raise ValueError('dtype must be numeric')

        value = value.tolist()
    
    return value