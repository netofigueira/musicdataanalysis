#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 18:34:27 2020

@author: neto
"""

import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from bokeh.palettes import brewer
from bokeh.palettes import d3
from bokeh.palettes import Category20
from bokeh.models import Legend


output_file('columndatasource_example.html')

df = pd.read_csv('DATA_.csv')
df.drop(df.columns.difference(['coverUrl','track_name', 'track_album', 'valence', 'energy']),1,
        inplace=True)

#create colors or each album

colors = d3['Category20'][len(df.track_album.unique())]

#create a map between factor (album name) and color
colormap = CategoricalColorMapper(factors=df.track_album.unique(), palette=colors)



source = ColumnDataSource(data = dict(df, imgs = list(df['coverUrl'])))

p = figure(plot_width=800, plot_height=600, toolbar_location = None )

p.scatter(x='valence', y = 'energy', source=source, color={'field': 'track_album',
                                                          'transform': colormap},
          size = 7)



p.title.text = 'Energy x Valence Chart'
p.xaxis.axis_label = 'valence'
p.yaxis.axis_label = 'energy'

hover = HoverTool(
        tooltips="""
        <div>
            <div>
                <img
                    src="@imgs" height="42" alt="@imgs" width="42"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">track:</span>
                <span style="font-size: 15px; color: #966;">@track_name</span>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;">album:</span>
                <span style="font-size: 15px; color: #966;">@track_album</span>
            </div>
        </div>
        """
    )


p.add_tools(hover)

show(p)
