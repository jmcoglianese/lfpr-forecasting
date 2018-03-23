#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 17:30:17 2017

@author: johncoglianese
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import ipywidgets as widgets
import numpy as np
import pandas as pd
from IPython.display import display

mldata = pd.read_csv("data/lfpr_gp_pred.csv")
mldata2 = pd.read_csv("data/lfpr_gp_pred2.csv")
mldata['lfp_pred2'] = mldata2['lfp_pred']
mldata['lfp_se2'] = mldata2['lfp_se']
mldata['lfp_age_avg'] = mldata2['lfp_age_avg']
mldata3 = pd.read_csv("data/lfpr_gp_pred3.csv")
mldata['lfp_pred3'] = mldata3['lfp_pred']
mldata['lfp_se3'] = mldata3['lfp_se']

pydata = pd.read_csv("data/lfpr_gpy_pred.csv")
pydata['lfp_pred'] = pydata['lfp_pred1']
pydata['lfp_se'] = pydata['lfp_se1']

age_widget = widgets.IntRangeSlider(
    value=[16, 80],
    min=16,
    max=80,
    step=1,
    description='Age Range:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d',
)
actual_data_widget = widgets.Checkbox(
    value=True,
    description='Actual LFPR',
    disabled=False
)
gp_data_widget = widgets.Checkbox(
    value=True,
    description='GP without mean function',
    disabled=False
)
gp2_data_widget = widgets.Checkbox(
    value=True,
    description='GP with age-specific mean',
    disabled=False
)
gp3_data_widget = widgets.Checkbox(
    value=True,
    description='GP with age-specific mean and logistic transform',
    disabled=False
)
data_widget_box = widgets.Box([actual_data_widget, gp_data_widget, gp2_data_widget, gp3_data_widget])
year_widget = widgets.IntRangeSlider(
    value=[1976, 2016],
    min=1976,
    max=2016,
    step=1,
    description='Year Range:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d',
)
cohort_label = widgets.Label('List of Cohorts (separated by commas):')
cohort_widget = widgets.Text(
    value='1930,1940,1950,1960,1970,',
    placeholder='1930,',
    description='',
    disabled=False
)
cohort_box = widgets.Box([cohort_label, cohort_widget])
age_adjustment_widget = widgets.Checkbox(
    value=False,
    description='Display age adjusted values?',
    disabled=False
)
dataset_widget = widgets.Dropdown(
    options=['Matlab', 'Python'],
    value='Matlab',
    description='GP Method:',
    disabled=False,
)

linestyle_list = ['solid', 'dashed', 'dotted', 'dashdot']
color_list = ['b', 'g', 'r', 'c', 'm'] * 10
marker_list = ['o', '^', 'D', 'x', '+'] * 10
train_linewidth = 2
test_linewidth = 1
train_markersize = 4
test_markersize = 2
variables = ['lfp', 'lfp_pred', 'lfp_pred2', 'lfp_pred3']
vartitles = ['Actual', 'GP', 'GP w/ Mean', 'GP w/ Mean & Logistic Transform']

display(cohort_box, age_widget, year_widget, data_widget_box, age_adjustment_widget, dataset_widget)

fig, ax = plt.subplots(1, 2, figsize = (10, 5))
ax[0].set_title("Men")
ax[0].set_ylabel("LFPR (p.p.)")
ax[0].set_xlabel("Age")
ax[0].set_xlim([16, 80])
ax[0].set_ylim([0, 100])
ax[1].set_title("Women")
ax[1].set_ylabel("LFPR (p.p.)")
ax[1].set_xlabel("Age")
ax[1].set_xlim([16, 80])
ax[1].set_ylim([0, 100])
plt.tight_layout(rect = (0., 0.2, 1., 1.))
plt.show()

def cohort_plots(change):
    # Convert cohort list from text to list of ints
    cohort_list = [int(c) for c in cohort_widget.value.split(',') if c.strip().isdigit()]
    variable_values = [item.value for item in data_widget_box.children]
    
    if dataset_widget.value == 'Matlab':
        data = mldata
    else:
        data = pydata
    
    # Create male subplot
    ax[0].clear()
    ax[0].set_title("Men")
    ax[0].set_ylabel("LFPR (p.p.)")
    ax[0].set_xlabel("Age")
    ax[0].set_xlim([age_widget.value[0], age_widget.value[1]])
    for i, cohort in enumerate(cohort_list):
        temp = data[data['cohort'] == cohort]
        temp_train = temp['year'] < 2000
        temp_test = temp['year'] >= 2000
        temp_sex = temp['sex'] == 1
        temp_ages = np.logical_and(temp['age'] >= age_widget.value[0], temp['age'] <= age_widget.value[1])
        temp_years = np.logical_and(temp['year'] >= year_widget.value[0], temp['year'] <= year_widget.value[1])
        temp_adj = np.zeros(temp['lfp'].shape)
        if age_adjustment_widget.value:
            temp_adj = temp['lfp_age_avg']
        for j, (var, val) in enumerate(zip(variables, variable_values)):
            if val:
                ax[0].plot(temp['age'][np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))], 
                     (temp[var][np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))] -
                      temp_adj[np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))]), 
                     color = color_list[i], marker = marker_list[i], markersize = train_markersize,
                     linestyle = linestyle_list[j], linewidth = train_linewidth)
                ax[0].plot(temp['age'][np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))], 
                     (temp[var][np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))] - 
                      temp_adj[np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))]), 
                     color = color_list[i], marker = marker_list[i], markersize = test_markersize,
                     linestyle = linestyle_list[j], linewidth = test_linewidth)       
    
    # Create female subplot
    ax[1].clear()
    ax[1].set_title("Women")
    ax[1].set_ylabel("LFPR (p.p.)")
    ax[1].set_xlabel("Age")
    ax[1].set_xlim([age_widget.value[0], age_widget.value[1]])
    for i, cohort in enumerate(cohort_list):
        temp = data[data['cohort'] == cohort]
        temp_train = temp['year'] < 2000
        temp_test = temp['year'] >= 2000
        temp_sex = temp['sex'] == 2
        temp_ages = np.logical_and(temp['age'] >= age_widget.value[0], temp['age'] <= age_widget.value[1])
        temp_years = np.logical_and(temp['year'] >= year_widget.value[0], temp['year'] <= year_widget.value[1])
        temp_adj = np.zeros(temp['lfp'].shape)
        if age_adjustment_widget.value:
            temp_adj = temp['lfp_age_avg']
        for j, (var, val) in enumerate(zip(variables, variable_values)):
            if val:
                ax[1].plot(temp['age'][np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))], 
                     (temp[var][np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))] -
                      temp_adj[np.logical_and.reduce((temp_train, temp_sex, temp_ages, temp_years))]), 
                     color = color_list[i], marker = marker_list[i], markersize = train_markersize,
                     linestyle = linestyle_list[j], linewidth = train_linewidth)
                ax[1].plot(temp['age'][np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))], 
                     (temp[var][np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))] - 
                      temp_adj[np.logical_and.reduce((temp_test, temp_sex, temp_ages, temp_years))]), 
                     color = color_list[i], marker = marker_list[i], markersize = test_markersize,
                     linestyle = linestyle_list[j], linewidth = test_linewidth)
    
    # Legend   
    lines = []
    for i, cohort in enumerate(cohort_list):
        lines.append(mlines.Line2D([], [], color=color_list[i], marker=marker_list[i],
                          markersize=train_markersize, label=cohort))
    ax[0].legend(handles=lines, bbox_to_anchor=(0., -0.25, 2.2, .102), 
               loc = 2, ncol=len(lines), mode='expand', borderaxespad=0., 
                 frameon=False, title="Cohort:")
        
    series = []
    for j, (var, val, title) in enumerate(zip(variables, variable_values, vartitles)):
        series.append(mlines.Line2D([], [], color='black', marker=None, label=title, linestyle = linestyle_list[j]))
    ax[1].legend(handles=series, bbox_to_anchor=(-1.2, -0.4, 2.2, .102), 
               loc = 2, ncol=len(series), mode='expand', borderaxespad=0., 
                 frameon=False, title="Series:")
        
    fig.canvas.draw()
    
for widget in [cohort_widget, age_widget, year_widget, age_adjustment_widget]:
    widget.observe(cohort_plots, names = 'value')
for widget in data_widget_box.children:
    widget.observe(cohort_plots, names = 'value')
cohort_plots(None)