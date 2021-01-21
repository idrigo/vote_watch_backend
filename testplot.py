import pandas as pd
import numpy as np
import datetime

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, CustomJS, TapTool, DatetimeTickFormatter,HoverTool


from bokeh.plotting import figure, show,output_file,save
from bokeh.io import output_notebook
output_notebook()

import locale
locale.setlocale(locale.LC_TIME, "ru_RU")

df = pd.read_csv('data.csv')
df.set_index(pd.to_datetime(df['time']),inplace=True)
df.drop(['time'], axis=1, inplace=True)
df.index = df.index+ pd.DateOffset(hours=3)

df_row = df.loc['2020-04-25 18:05:29']
hist_data = df_row.to_frame()
date = df_row.name.strftime('%d %B %H:%M')

hist_data.columns=['votes']

hist_data.sort_values(by='votes', ascending=False, inplace=True)
hist_data['rank'] = hist_data.reset_index().index
hist_data['rank'] = hist_data['rank']+1
hist_data.sort_values(by='votes', ascending=True, inplace=True)

sourcebars = ColumnDataSource(hist_data)
names = hist_data.index.tolist()
TOOLS = "pan,wheel_zoom,box_zoom,hover,tap"

TOOLTIPS = [
    ("МЕСТО", "@rank"),
    ("КАНДИДАТ","@index"),
    ("ГОЛОСОВ", "@votes"),
]
p1 = figure(y_range=names,tools=TOOLS, tooltips=TOOLTIPS,plot_width=800, plot_height=1200,sizing_mode='scale_width' )
bars = p1.hbar(y='index', right='votes', height=0.9, source=sourcebars, alpha=0.7, hover_fill_alpha = 1.0, left=1)

df['y'] = 0
y_dummy = [0]*len(df)
sourcelines = ColumnDataSource(df)

p2 = figure(plot_width=1200, plot_height=800, tools=TOOLS,sizing_mode='scale_width')


p2.line(x = 'time', y = 'y', source = sourcelines)
p2.xaxis.formatter = DatetimeTickFormatter(days=['%d/%m %H:%M'])
p2.hover.tooltips = [("ВРЕМЯ", "@time{%m-%d %H:%M}"),("ГОЛОСОВ","@y")]
p2.hover.formatters = {'@time': 'datetime'}
p2.hover.mode='vline'
lines = p2

lines.visible = False

code = '''if (cb_data.source.selected.indices.length > 0){
            var data = source.data;
            lines.visible = true;
            var selected_index = cb_data.source.selected.indices[0];
            var sel_name = cb_data.source.data.index[selected_index];
            data['y'] = data[sel_name];
            source.change.emit();
            lines.visible = true;
          }'''

plots = row(p2,p1)

p1.select(TapTool).callback = CustomJS(args={'lines': lines, 'source': sourcelines}, code = code)
show(plots)

# html = file_html(plots, CDN, "my plot")

output_file('plot.html', mode='inline')
save(plots)
