# Signal Preprocessing

## Standardization

Performs a standardization of data (Z-scoring), i.e., centering and scaling, so that the data is expressed in terms of standard deviation (i.e., mean = 0, SD = 1) or Median Absolute Deviance (median = 0, MAD = 1). The latter is more robust to outliers.
The rolling version of this standardization is available only for the standard deviation approach, since calculating rolling median's for signals with over 100k samples will take way too long.
