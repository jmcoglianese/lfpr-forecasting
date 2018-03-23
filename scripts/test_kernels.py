
import os
import pandas as pd
import numpy as np
from scipy.special import logit, expit
import GPy

try:
    os.chdir('/Users/johncoglianese/Dropbox/Documents/Research/LFPR/Forecasting')
except OSError:
    os.chdir('/n/home00/jcoglianese/Dropbox/Documents/Research/LFPR/Forecasting')

logit_link = {'transform': lambda x: logit(x / 100), 
             'untransform': lambda x: expit(x) * 100} 
iden_link = {'transform': lambda x: x, 
             'untransform': lambda x: x}

def transform_y(input, link = iden_link, baseline = None):
    if baseline is None:
        return link['transform'](input)
    else:
        return link['transform'](input) - link['transform'](baseline)
def untransform_y(input, link = iden_link, baseline = None):
    if baseline is None: 
        return link['untransform'](input)
    else:
        return link['untransform'](input + link['transform'](baseline))
    
def normdata(input, mean = None, std = None):
    mean_hat = mean if mean is not None else np.mean(input, axis = 0)
    std_hat = std if std is not None else np.std(input, axis = 0)
    normalized_input = (input - mean_hat) / std_hat
    
    if mean is not None:
        return normalized_input
    else:
        return normalized_input, mean_hat, std_hat


data = pd.read_csv("data/lfpr_age_sex_cohort.csv")
data[data[['lfp']] == 0] = 1


k_se_tagesex = GPy.kern.RBF(input_dim = 3, variance = 0.2 ** 2, lengthscale = [0.1, 1.0, 1.0], ARD = True, active_dims = [0, 1, 2])
k_se_agesex = GPy.kern.RBF(input_dim = 2, variance = 0.2 ** 2, lengthscale = [0.1, 1.0], ARD = True, active_dims = [0, 1])
k_se_cohort = GPy.kern.RBF(input_dim = 1, variance = 0.2 ** 2, lengthscale = [1.0], active_dims = [3])
k_lin_t = GPy.kern.Linear(input_dim = 1, variances = [0.2 ** 2], active_dims = [2])
k_lin_cohort = GPy.kern.Linear(input_dim = 1, variances = [0.2 ** 2], active_dims = [3])
k_lin_ugap = GPy.kern.Linear(input_dim = 1, variances = [0.2 ** 2], active_dims = [4])
k_lin_ugapl1 = GPy.kern.Linear(input_dim = 1, variances = [0.2 ** 2], active_dims = [5])
k_lin_ugapl2 = GPy.kern.Linear(input_dim = 1, variances = [0.2 ** 2], active_dims = [6])

k1 = k_se_agesex + k_lin_t * k_se_agesex
k2 = k_se_agesex + k_lin_t * k_se_tagesex
k3 = k_se_agesex + k_lin_cohort * k_se_cohort * k_se_agesex
k4 = k_se_agesex + k_lin_t * k_se_tagesex + k_se_cohort
k5 = k_se_agesex + k_lin_cohort * k_se_cohort
k6 = k_se_agesex + k_lin_t * k_se_tagesex + k_lin_ugap * k_se_agesex
k7 = k_se_agesex + k_lin_t * k_se_tagesex + k_lin_ugap * k_se_agesex + k_lin_ugapl1 * k_se_agesex + k_lin_ugapl2 * k_se_agesex

kernels = [k1, k2, k3, k4, k5, k6, k7]

for i, kern in enumerate(kernels):
    proc_data = data.copy()
    train = proc_data[proc_data['year'] < 2000].copy()
    
    X_train = train[['sex', 'age', 'year', 'cohort', 'ugap', 'ugap_lag1', 'ugap_lag2']].copy().values
    y_train = transform_y(train['lfp'].copy().values, logit_link)
    X_all = proc_data[['sex', 'age', 'year', 'cohort', 'ugap', 'ugap_lag1', 'ugap_lag2']].copy().values
    
    XN_train, X_mean, X_std = normdata(X_train)
    XN_all = normdata(X_all, X_mean, X_std)
    yN_train, y_mean, y_std = normdata(y_train)
    
    yN_train = yN_train.reshape(yN_train.shape[0], 1)
    
    m = GPy.models.GPRegression(XN_train, yN_train, kernel = kern)
    m.Gaussian_noise.variance = 0.2 ** 2
    m.optimize()
    print m
    print m['']
    
    pred, var = m.predict(XN_all)
    y_pred = untransform_y(np.squeeze(pred) * y_std + y_mean, logit_link)
    y_se = np.sqrt(var * y_std ** 2)
    data['lfp_pred{}'.format(i+1)] = y_pred
    data['lfp_se{}'.format(i+1)] = y_se
    
data.to_csv('data/lfpr_gpy_testkernels_pred.csv')