import pandas as pd
import os

from bokeh.models import ColumnDataSource, TapTool, CustomJS, DatetimeTickFormatter
from bokeh.layouts import column, row
from bokeh.plotting import figure, output_file, save, curdoc
from bokeh.embed import components
from bokeh.resources import CDN

from jinja2 import Template

import locale

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

template = Template(
    '''
<html lang="en">
    <head>
        <meta charset="utf-8">
            <title>Результаты голосования</title>
            {{ resources }}
            {{ script }}
        <script>
        var end = new Date('05/12/2020 11:0 AM');

        var _second = 1000;
        var _minute = _second * 60;
        var _hour = _minute * 60;
        var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distance = end - now;
        if (distance < 0) {

            clearInterval(timer);
            document.getElementById('countdown').innerHTML = 'EXPIRED!';

            return;
        }
        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);

        document.getElementById('countdown').innerHTML = days + ' дней ';
        document.getElementById('countdown').innerHTML += hours + ' час ';
        document.getElementById('countdown').innerHTML += minutes + ' мин ';
    }

    timer = setInterval(showRemaining, 1000);
    </script>
    </head>
    <body>
        <div class="padding: 60px;text-align: center;font-size: 30px">
        <h1>Голосование проходит на <a href="http://vote.educom.ru">vote.educom.ru</a> </h1>
        </div>
        До конца голосования осталось <div id="countdown"></div>
        <div class="embed-wrapper">
        {{ div }}
        </div>
    </body>
</html>
        ''')

path_script = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(path_script, 'data.csv'))
df.set_index(pd.to_datetime(df['time']), inplace=True)
df.drop(['time'], axis=1, inplace=True)
df.index = df.index + pd.DateOffset(hours=3)

date = df.tail(1).index.strftime('%d %B %H:%M')[0]
hist_data = df.tail(1).T
hist_data.columns = ['votes']

hist_data.sort_values(by='votes', ascending=False, inplace=True)
hist_data['rank'] = hist_data.reset_index().index
hist_data['rank'] = hist_data['rank'] + 1
hist_data.sort_values(by='votes', ascending=True, inplace=True)
sourcebars = ColumnDataSource(hist_data)
names = hist_data.index.tolist()
TOOLS = "hover,tap"

TOOLTIPS = [
    ("МЕСТО", "@rank"),
    ("КАНДИДАТ","@index"),
    ("ГОЛОСОВ", "@votes"),
]
p1 = figure(y_range=names,tools=TOOLS, tooltips=TOOLTIPS,plot_width=800, plot_height=1200,sizing_mode='scale_width' )
bars = p1.hbar(y='index', right='votes', height=0.9, source=sourcebars, alpha=0.7, hover_fill_alpha = 1.0, left=1)

# title = f'Данные по состоянию на {date}'
# p1.title.text = title
# p1.title.text_font_size = "17px"


df['y'] = 0
y_dummy = [0]*len(df)
sourcelines = ColumnDataSource(df)

p2 = figure(plot_width=1200, plot_height=800, tools=TOOLS,sizing_mode='scale_width')

p2.title.text = f'Данные по состоянию на {date}'
p2.title.text_font_size = "17px"
p2.line(x = 'time', y = 'y', source = sourcelines)
p2.xaxis.formatter = DatetimeTickFormatter(days=['%d/%m %H:%M'])
p2.hover.tooltips = [("ВРЕМЯ", "@time{%m-%d %H:%M}"), ("ГОЛОСОВ","@y")]
p2.hover.formatters = {'@time': 'datetime'}
p2.hover.mode = 'vline'
lines = p2

lines.visible = True

code = '''if (cb_data.source.selected.indices.length > 0){
            var data = source.data;
            lines.visible = true;
            var selected_index = cb_data.source.selected.indices[0];
            var sel_name = cb_data.source.data.index[selected_index];
            data['y'] = data[sel_name];
            source.change.emit();
            lines.visible = true;
          }'''


p1.select(TapTool).callback = CustomJS(args={'lines': lines, 'source': sourcelines}, code = code)
plots = row(p2,p1)

# add a button widget and configure with the call back
output_file(os.path.join(path_script, 'vote_watch', 'docs', "index.html"))
save(plots)

script, div = components(plots)
resources_bokeh = CDN.render()

html = template.render(resources=resources_bokeh,
                       script=script,
                       div=div)

out_file_path = os.path.join(path_script, 'vote_watch', '_includes', "plot.html")
with open(out_file_path, mode='w') as f:
    f.write(html)

out_file_path = os.path.join(path_script, 'vote_watch', 'docs', "index.html")
with open(out_file_path, mode='w') as f:
    f.write(html)
