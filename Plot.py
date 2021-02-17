#!/usr/bin/env python3
# coding=utf-8


"""
import plotly.graph_objects as go
import plotly.offline as py
from plotly.graph_objs import *
 
trace0 = Scatter(
    x=[1, 2, 3, 4],
    y=[10, 15, 13, 17]
)
trace1 = Scatter(
    x=[1, 2, 3, 4],
    y=[16, 5, 11, 9]
)
data = Data([trace0, trace1])
 
unique_url = py.plot(data, filename = 'basic-line.html')

"""
import plotly.graph_objects as go
fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
fig.write_html('first_figure.html', auto_open=True)

