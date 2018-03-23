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


        
    