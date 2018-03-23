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
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from collections import OrderedDict

data = pd.read_csv("data/lfpr_gpy_testkernels_pred.csv").sort_values(by = ['age', 'year'])

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
    disabled=False,
    style={'description_width': 'initial'}
)
forecast_label = widgets.Label('Include Forecast with Kernel:')
forecast_widget = widgets.Dropdown(
    options=OrderedDict(sorted({'None': 0, '1 - Krueger': 1, '2 - Local Trends': 2, '3 - Cohort Trends': 3, '4 - Local Trends + Cohort': 4, '5 - Age/Gender/Cohort FE': 5, '6 - Local Trends + UR': 6, '7 - Local Trends + UR & Lags': 7}.items())),
    value=0,
    description='',
    disabled=False,
)
forecast_box = widgets.Box([forecast_label, forecast_widget])
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

display(age_widget, year_widget, forecast_box)

fig = plt.figure(figsize = (12, 16))
ax0 = fig.add_subplot(2, 1, 1, projection='3d')
ax0.set_title("Men")
ax0.set_xlabel("Age")
ax0.set_ylabel("Year")
ax0.set_zlabel("LFPR (p.p.)")
ax0.set_xlim([16, 80])
ax0.set_ylim([1976, 2016])
ax0.set_zlim([0, 100])
ax1 = fig.add_subplot(2, 1, 2, projection='3d')
ax1.set_title("Women")
ax1.set_xlabel("Age")
ax1.set_ylabel("Year")
ax1.set_zlabel("LFPR (p.p.)")
ax1.set_xlim([16, 80])
ax1.set_ylim([1976, 2016])
ax1.set_zlim([0, 100])
cb = {}
plt.tight_layout(rect = (0., 0.2, 1., 1.))
plt.show()

def cohort_plots(change):
    # Select only the values that are needed
    forecast_value = forecast_widget.value
    mask_age = np.logical_and(data['age'] >= age_widget.value[0], data['age'] <= age_widget.value[1])
    mask_year = np.logical_and(data['year'] >= year_widget.value[0], data['year'] <= year_widget.value[1])
    mask_men = np.logical_and.reduce((data['sex'] == 1, mask_age, mask_year))
    mask_women = np.logical_and.reduce((data['sex'] == 2, mask_age, mask_year))
    
    for key in cb.keys():
        cb.pop(key).remove()
        
    # Create male subplot
    ax0.clear()
    ax0.set_title("Men")
    ax0.set_xlabel("Age")
    ax0.set_ylabel("Year")
    ax0.set_zlabel("LFPR (p.p.)")
    ax0.set_xlim([age_widget.value[0], age_widget.value[1]])
    ax0.set_ylim([year_widget.value[0], year_widget.value[1]])
    ax0.set_zlim([0, 100])
    
    surf0_a = ax0.plot_trisurf(data['age'][mask_men], data['year'][mask_men], data['lfp'][mask_men], 
                     cmap = cm.viridis, linewidth = 0, antialiased = False)
    cb['cb0_a'] = plt.colorbar(surf0_a, shrink = 0.5, aspect = 5, label = "Actual", ax = ax0)
    if forecast_value is not 0:
        surf0_b = ax0.plot_trisurf(data['age'][mask_men], data['year'][mask_men], 
                                   data['lfp_pred{}'.format(forecast_value)][mask_men],
                                   cmap = cm.magma, linewidth = 0, antialiased = False)
        cb['cb0_b'] = plt.colorbar(surf0_b, shrink = 0.5, aspect = 5, label = "Forecast", ax = ax0)    
    
    # Create female subplot
    ax1.clear()
    ax1.set_title("Women")
    ax1.set_xlabel("Age")
    ax1.set_ylabel("Year")
    ax1.set_zlabel("LFPR (p.p.)")
    ax1.set_xlim([age_widget.value[0], age_widget.value[1]])
    ax1.set_ylim([year_widget.value[0], year_widget.value[1]])
    ax1.set_zlim([0, 100])
    
    surf1_a = ax1.plot_trisurf(data['age'][mask_women], data['year'][mask_women], data['lfp'][mask_women], 
                     cmap = cm.viridis, linewidth = 0, antialiased = False)
    cb['cb1_a'] = plt.colorbar(surf1_a, shrink = 0.5, aspect = 5, label = "Actual", ax = ax1)
    if forecast_value is not 0:
        surf1_b = ax1.plot_trisurf(data['age'][mask_women], data['year'][mask_women], 
                                   data['lfp_pred{}'.format(forecast_value)][mask_women],
                                   cmap = cm.magma, linewidth = 0, antialiased = False)
        cb['cb1_b'] = plt.colorbar(surf1_b, shrink = 0.5, aspect = 5, label = "Forecast", ax = ax1)    
        
    fig.canvas.draw()
    
for widget in [age_widget, year_widget, forecast_widget]:
    widget.observe(cohort_plots, names = 'value')
cohort_plots(None)