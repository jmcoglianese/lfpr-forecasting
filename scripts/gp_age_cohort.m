% This file computes GP predictions for LFPR by age and cohort

% Load the data
cd ~/Documents/Research/LFPR/Forecasting
data = readtable("data/lfpr_age_sex_cohort.csv");
data.lfp(data.lfp == 0) = 0.01;

% Set up logistic transform
transform = @(x) icdf('Logistic', x / 100, 0, 1);
untransform = @(x) cdf('Logistic', x, 0, 1) * 100;

% Setup split data
train = data(data.year < 2000, :);
test = data(data.year >= 2000, :);

X_train = [train.sex train.age train.cohort];
y_train = transform(train.lfp) - transform(train.lfp_age_avg);
X_test = [test.sex test.age test.cohort];
y_test = transform(test.lfp) - transform(test.lfp_age_avg);
X_all = [data.sex data.age data.cohort];
y_all = transform(data.lfp) - transform(data.lfp_age_avg);

% Normalize data
[XN_train, X_mean, X_std] = normdata(X_train);
XN_all = normdata(X_all, X_mean, X_std);
XN_test = normdata(X_test, X_mean, X_std);
[yN_train, y_mean, y_std] = normdata(y_train);
yN_all = normdata(y_all, y_mean, y_std);
yN_test = normdata(y_test, y_mean, y_std);

% Set up likelihood and covariance
lik = lik_gaussian('sigma2', 0.2^2);
gpcf = gpcf_sexp('lengthScale', [0.1 1.0 1.0], 'magnSigma2', 0.2^2);

% Set some priors
pn = prior_logunif();
lik = lik_gaussian(lik,'sigma2_prior', pn);
pl = prior_unif();
pm = prior_sqrtunif();
gpcf = gpcf_sexp(gpcf, 'lengthScale_prior', pl, 'magnSigma2_prior', pm);

% Create GP
gp = gp_set('lik', lik, 'cf', gpcf);
	      
% Set the options for the scaled conjugate optimization
opt=optimset('TolFun', 1e-3, 'TolX', 1e-3, 'Display', 'iter');

% Optimize with the scaled conjugate gradient method
gp=gp_optim(gp, XN_train, yN_train, 'optimf', @fminscg, 'opt', opt);
	      
% Generate predicted values
[Eft_map, Varft_map] = gp_pred(gp, XN_train, yN_train, XN_all);

% Un-normalize
y_pred = untransform(Eft_map * y_std + y_mean + transform(data.lfp_age_avg));
y_se = sqrt(Varft_map * y_std.^2);

% Store and save
data.lfp_pred = y_pred;
data.lfp_se = y_se;
writetable(data,"data/lfpr_gp_pred4.csv");