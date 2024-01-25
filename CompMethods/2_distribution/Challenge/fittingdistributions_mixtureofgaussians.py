# -*- coding: utf-8 -*-
"""FittingDistributions_MixtureOfGaussians.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XuMJI_SOrJTqWE1iCCFOzcz-lxLukIkh

The Mixture of Gaussians model for the VaR
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib.pyplot as plt

column_names = ['price']
df_prices = pd.read_csv('IBM_prices.csv', index_col=0)
df_prices.rename(columns={'Adj. Close Price': 'Price'}, inplace=True)
df_prices['r'] = np.log(df_prices['Price'] / df_prices['Price'].shift(1))
r = df_prices['r'][1:].to_numpy()

r_min = r.min()
r_max = np.max(r)
n = r.shape[0]
d = 100

deltas = np.linspace(r_min,r_max,d)
deltastep = (r_max-r_min)/d
epsilon = deltastep/2

alpha = 0.01
C = 1000

"""ML estimate of the three parameters (p, sigmaN, sigmaF) of the model"""

def logLikelihood_forMG(x, data):
  # extract and name the three parameters of the model stored in x
  p = x[0]
  sigmaN = x[1]
  sigmaF = x[2]
  # define and return the (negative) log likelihood function
  logLikelihood = -np.sum(np.log(p * norm.pdf(data, loc= 0, scale=sigmaN) + (1-p) * norm.pdf(data, loc= 0, scale=sigmaF)))
  return logLikelihood
  
initialGuess = [0.5, 0.15/np.sqrt(250), 0.3/np.sqrt(250)]
bounds = [(0, 1), (0, None), (0, None)]

# set up the minimization problem using the initial guesses and the bounds above
# use the 'Nelder-Mead' minimization method

MLEoutput_forMG = minimize(logLikelihood_forMG, initialGuess, args = r, bounds = bounds, method = 'Nelder-Mead')

p_MG, sigmaN_MG, sigmaF_MG = MLEoutput_forMG.x
print(p_MG, sigmaN_MG*np.sqrt(250), sigmaF_MG*np.sqrt(250))

"""Computation of the PDF of the mixture of Gaussians using the optimal parameters found above and comparison to the empirical PDF"""

PDF_MG = np.zeros(shape=(d,1))

mu_hat = r.mean()

for i in range(int(d)):
  PDF_MG[i] = p_MG * (norm.pdf(deltas[i], loc=mu_hat, scale=sigmaN_MG)) + (1-p_MG) * norm.pdf(deltas[i], loc=mu_hat, scale=sigmaF_MG)

plt.figure(figsize=(10, 5))
plt.hist(r, density = True, label='Histrogram', alpha = 0.5, bins = d)
plt.plot(deltas, PDF_MG, linewidth = 2, label = 'Mixture of Gaussian r.v.s PDF')
plt.legend();

"""Computation of the CDF of the mixture of Gaussians using the optimal parameters found"""

CDF_MG = np.zeros(shape=(d,1))
CDF_MG[0] = 0


print(deltas)

for i in range(int(d)-1):
  CDF_MG[i+1] = CDF_MG[i]+ PDF_MG[i] * deltastep

plt.figure(figsize=(10,5))
plt.plot(deltas,CDF_MG, linewidth = 2, label = 'Empirical CDF')
plt.legend();

print(CDF_MG)

"""Computation of the quantile (and of the VaR) according to the model
Notice tha you have both the Mixture of Gaussian CDF sampled at the points in deltas. One way to find the relevant quantile is to find the point of the CDF that is the closest to alpha...
"""




