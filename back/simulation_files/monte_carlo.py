import numpy as np
from numba import njit, jit, vectorize

# Aim to create the simulations in a numba friendly manner 
"""
    '# Numba likes loops'
    '# Numba likes NumPy functions'
    '# Numba likes NumPy broadcasting'
    
    '# Numba doesn't know about pd.DataFrame'
    
    @jit(nopython=True) or @njit
    also @jit(parallel = True) and @jit(fastmath = True) can be useful
    
    docs: https://numba.readthedocs.io/en/stable/index.html
    
    Numba also supports CUDA
    More about numba-cuda: https://numba.readthedocs.io/en/stable/cuda/overview.html#cuda-deprecation-status
"""