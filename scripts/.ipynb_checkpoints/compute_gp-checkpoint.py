
import os
import pandas as pd
import numpy as np
from scipy.special import logit, expit
import GPy

os.chdir("/Users/johncoglianese/Documents/Research/LFPR/Forecasting/")

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
data[data[['lfp']] == 0] = 0.01

procedures = [{}, {'age-mean': True}, {'age-mean': True, 'logit-transform': True}]

for i, proc in enumerate(procedures):
    proc_data = data.copy()
    train = proc_data[proc_data['year'] < 2000].copy()
    
    X_train = train[['sex', 'age', 'cohort']].copy().values
    y_train = transform_y(train['lfp'].copy().values, logit_link if 'logit-transform' in proc else iden_link,
                         train['lfp_age_avg'].copy() if 'age-mean' in proc else None)
    X_all = proc_data[['sex', 'age', 'cohort']].copy().values
    
    XN_train, X_mean, X_std = normdata(X_train)
    XN_all = normdata(X_all, X_mean, X_std)
    yN_train, y_mean, y_std = normdata(y_train)
    
    yN_train = yN_train.reshape(yN_train.shape[0], 1)
    
    k = GPy.kern.RBF(input_dim = 3, variance = 0.2 ** 2, lengthscale = [0.1, 1.0, 1.0], ARD = True)
    m = GPy.models.GPRegression(XN_train, yN_train, kernel = k)
    m.Gaussian_noise.variance = 0.2 ** 2
    m.optimize()
    
    pred, var = m.predict(XN_all)
    y_pred = untransform_y(np.squeeze(pred) * y_std + y_mean, logit_link if 'logit-transform' in proc else iden_link,
                         proc_data['lfp_age_avg'].copy() if 'age-mean' in proc else None)
    y_se = np.sqrt(var * y_std ** 2)
    data['lfp_pred{}'.format(i+1)] = y_pred
    data['lfp_se{}'.format(i+1)] = y_se
    
data.to_csv('data/lfpr_gpy_pred.csv')