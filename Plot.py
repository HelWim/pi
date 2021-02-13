#!/usr/bin/env python3
# coding=utf-8

"""
import csv
import plotly.express as px


df = px.data.gapminder().query("country=='Canada'")
fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
fig.show()
"""

import plotly.plotly as py
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
 
unique_url = py.plot(data, filename = 'basic-line')



