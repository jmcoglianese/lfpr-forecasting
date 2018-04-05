
import numpy as np
import plotly
import plotly.graph_objs as go


forecast_value = forecast_widget.value
mask_age = np.logical_and(data['age'] >= age_widget.value[0], data['age'] <= age_widget.value[1])
mask_year = np.logical_and(data['year'] >= year_widget.value[0], data['year'] <= year_widget.value[1])
mask_men = np.logical_and.reduce((data['sex'] == 1, mask_age, mask_year))
mask_women = np.logical_and.reduce((data['sex'] == 2, mask_age, mask_year))

plotly.offline.init_notebook_mode(connected=True)

fig = plotly.tools.make_subplots(rows = 2, cols = 1, 
                                specs = [[{'is_3d': True}], [{'is_3d': True}]],
                                    print_grid = False)

fig.append_trace(dict(type = 'surface', 
                      x = data[mask_men].pivot(index = 'age', columns = 'year', values = 'age').values, 
                      y = data[mask_men].pivot(index = 'age', columns = 'year', values = 'year').values, 
                      z = data[mask_men].pivot(index = 'age', columns = 'year', values = 'lfp').values, 
                      colorscale = 'Viridis', scene = 'scene1', showscale = True, name = 'Actual'), 1, 1)

fig.append_trace(dict(type = 'surface', 
                          x = data[mask_women].pivot(index = 'age', columns = 'year', values = 'age').values, 
                          y = data[mask_women].pivot(index = 'age', columns = 'year', values = 'year').values, 
                          z = data[mask_women].pivot(index = 'age', columns = 'year', values = 'lfp').values, 
                          colorscale = 'Viridis', scene = 'scene2', showscale = True, name = 'Actual'), 2, 1)

if forecast_value is not 0:
    fig.append_trace(dict(type = 'surface', 
                          x = data[mask_men].pivot(index = 'age', columns = 'year', values = 'age').values, 
                          y = data[mask_men].pivot(index = 'age', columns = 'year', values = 'year').values, 
                          z = data[mask_men].pivot(index = 'age', columns = 'year', 
                                                   values = 'lfp_pred{}'.format(forecast_value)).values, 
                          colorscale = 'RdBu', scene = 'scene1', showscale = True, opacity = 0.9, name = 'Predicted'), 1, 1)
    
if forecast_value is not 0:
    fig.append_trace(dict(type = 'surface', 
                              x = data[mask_women].pivot(index = 'age', columns = 'year', values = 'age').values, 
                              y = data[mask_women].pivot(index = 'age', columns = 'year', values = 'year').values, 
                              z = data[mask_women].pivot(index = 'age', columns = 'year', 
                                                         values = 'lfp_pred{}'.format(forecast_value)).values, 
                              colorscale = 'RdBu', scene = 'scene2', showscale = True, opacity = 0.9, name = 'Predicted'), 2, 1) 

fig['layout'].update(height = 1200, width = 800, 
                     autosize = False,
                    margin = dict(t = 0, b = 0, l = 0, r = 0))
                      
scene = dict(
    xaxis = dict(
        title = 'Age',
        range = [16, 80]
    ),
    yaxis = dict(
        title = 'Year',
        range = [1976, 2016]
    ),
    zaxis = dict(
        title = 'LFPR (p.p.)',
        range = [0, 100]
    ),
    aspectmode = 'cube',
    camera = dict(
        center = dict(
            x = 0.1,
            y = -0.1,
            z = -0.15
        ),
        eye = dict(
            x = 1.6, 
            y = 1.25, 
            z = 0.25
        )
    )
)  
    
scene['xaxis']['range'] = [age_widget.value[0], age_widget.value[1]]
scene['yaxis']['range'] = [year_widget.value[0], year_widget.value[1]]

fig['layout']['scene1'].update(scene)
fig['layout']['scene2'].update(scene)
fig['layout']['scene1']['domain'].update(dict(y=[0.5, 1]))
fig['layout']['scene2']['domain'].update(dict(y=[0, 0.5]))

for surf in fig['data']:
    surf['cauto'] = False
    surf['cmin'] = 0
    surf['cmax'] = 100
    surf['colorbar']['len'] = 0.4
    surf['colorbar']['titlefont']['size'] = 20

fig['data'][0]['colorbar']['y'] = 0.75
fig['data'][0]['colorbar']['title'] = 'Men'
fig['data'][1]['colorbar']['y'] = 0.25
fig['data'][1]['colorbar']['title'] = 'Women'
if forecast_value is not 0:
    fig['data'][2]['colorbar']['title'] = "_"
    fig['data'][2]['colorbar']['y'] = 0.75
    fig['data'][2]['colorbar']['x'] = 1.12
    fig['data'][3]['colorbar']['title'] = "_"
    fig['data'][3]['colorbar']['y'] = 0.25
    fig['data'][3]['colorbar']['x'] = 1.12

plotly.offline.iplot(fig)