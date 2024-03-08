import statsmodels.api as sm
import numpy as np
import numpy.typing as npt
import polars as pl

from statsmodels.gam.api import GLMGam
from IPython.lib import guisupport

def make_gam(data: pl.DataFrame, formula: str) -> GLMGam:
    data_array = data.to_numpy(structured=True)
    return GLMGam.from_formula(formula, data_array)