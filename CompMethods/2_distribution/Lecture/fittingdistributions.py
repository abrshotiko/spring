# -*- coding: utf-8 -*-
"""FittingDistributions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Peg4s6F8KZMR09MKjj7045J_X6W0mgG0

Analysis of the distribution of daily (log) returns of IBM over the last 10 years
"""

import pandas as pd

column_names = ['price']
df_prices = pd.read_csv('IBM_prices.csv', index_col=0)

df_prices.plot(figsize=(10,5));

df_prices.rename(columns={'Adj. Close Price': 'Price'}, inplace=True)
df_prices

import numpy as np
df_prices['r'] = np.log(df_prices['Price'] / df_prices['Price'].shift(1))
df_prices

df_prices['r'].plot(figsize=(10,5));

"""Empirical CDF"""

r = df_prices['r'][1:].to_numpy()
r

r_min = r.min()
r_max = np.max(r)

n = r.shape[0]
print(r_min,r_max,n)

d = 100
deltas = np.linspace(r_min,r_max,d)
deltas

deltastep = (r_max-r_min)/d
deltastep

(r <= 0)

np.sum( r <= 0)/n

CDF_hat = np.zeros(shape=(d,1))

for i in range(int(d)):
  CDF_hat[i] = np.sum( r <= deltas[i] )/n

import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))
plt.plot(deltas,CDF_hat, linewidth = 2, label = 'Empirical CDF')
plt.legend();

mu_hat = r.mean()
sigma_hat = r.std()

from scipy.stats import norm
CDF_norm = norm.cdf(deltas, loc = mu_hat, scale = sigma_hat)

print(mu_hat, sigma_hat)
print(mu_hat*250, sigma_hat*np.sqrt(250))

plt.figure(figsize=(10,5))
plt.plot(deltas,CDF_hat, linewidth = 2, label = 'Empirical CDF')
plt.plot(deltas,CDF_norm, linewidth = 2, label = 'Theoretical CDF')
plt.legend();

plt.hist(r, label='Histogram', bins = d)

epsilon = deltastep/2

PDF_hat = np.zeros(shape=(d,1))

for i in range(int(d)):
  PDF_hat[i] = ( np.sum( r <= deltas[i]+epsilon )/n - np.sum( r <= deltas[i]-epsilon )/n  )/(2*epsilon)

PDF_norm = norm.pdf(deltas, loc = mu_hat, scale = sigma_hat)

from scipy.stats import gaussian_kde

kde = gaussian_kde(r)
PDF_kde = kde(deltas)

plt.figure(figsize=(10,5))
plt.plot(deltas,PDF_hat, linewidth = 2, label = 'Empirical PDF')
plt.hist(r, density = True, label='Histogram', bins = d, alpha = 0.5)
plt.plot(deltas,PDF_norm, linewidth = 2, label = 'Theoretical PDF')
plt.plot(deltas,PDF_kde, linewidth = 2, label = 'KDE')
plt.legend();

alpha = 0.01
quantile_alpha_N = norm.ppf(alpha, loc = mu_hat, scale = sigma_hat)
quantile_alpha_N

C = 1000
VaR_alpha_N = -C*(np.exp(quantile_alpha_N)-1)
VaR_alpha_N

print(mu_hat,sigma_hat)

from scipy.optimize import minimize

def logLikelihood_forN(x, dataPoints):
 # x: set of parameters I'm minimizing w.r.t: mu and sigma
 mu = x[0]
 sigma = x[1]
 logLikelihood = -np.sum( np.log( norm.pdf(dataPoints, loc = mu, scale = sigma) ) )
 return logLikelihood

initialGuess = [0, 0.3/np.sqrt(250)]
myBounds = [(None, None), (0, None)]

MLEoutput_forN = minimize(logLikelihood_forN, initialGuess, args = r, bounds = myBounds, method = 'Nelder-Mead')
mu_MLE, sigma_MLE = MLEoutput_forN.x
print(mu_MLE, sigma_MLE)

from scipy.stats import t

def logLikelihood_forT(x, dataPoints):
 # x: set of parameters I'm minimizing w.r.t: ni, mu and sigma
 ni = x[0]
 mu = x[1]
 sigma = x[2]
 logLikelihood = -np.sum( np.log( t.pdf(dataPoints, df = ni, loc = mu, scale = sigma) ) )
 return logLikelihood

initialGuess = [3, 0, 0.3/np.sqrt(250)]
myBounds = [(2, None), (None, None), (0, None)]

MLEoutput_forT = minimize(logLikelihood_forT, initialGuess, args = r, bounds = myBounds, method = 'Nelder-Mead')
ni_MLE, mu_MLE, sigma_MLE = MLEoutput_forT.x
print(ni_MLE, mu_MLE, sigma_MLE)

PDF_T = t.pdf(deltas, df = ni_MLE, loc = mu_MLE, scale = sigma_MLE)

plt.figure(figsize=(10,5))
plt.plot(deltas,PDF_kde, linewidth = 2, label = 'KDE')
plt.plot(deltas,PDF_norm, linewidth = 2, label = 'Normal PDF')
plt.plot(deltas,PDF_T, linewidth = 2, label = 'Student t PDF')
plt.legend();

quantile_alpha_T = t.ppf(alpha, df = ni_MLE, loc = mu_MLE, scale = sigma_MLE)
VaR_alpha_T = -C*(np.exp(quantile_alpha_T)-1)
VaR_alpha_T

