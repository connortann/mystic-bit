from flask import Flask
from flask import request
from flask import render_template
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import json
from mysticbit import ml
from mysticbit import munging

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot, iplot, download_plotlyjs



app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/mystic-bit')
def run_mystic_bit():
    df = pd.read_csv('./static/HACKA_DS_B03_WELL.csv')
    x = df.PSEUDO_DEPTH
    print(df.columns)
    y = df['TEMP       ']
    plt.plot(x, y)
    plt.savefig('static/my_plot.png')
    return render_template('my_template.html', name ='B03', url='/static/my_plot.png')

@app.route('/mystic-depth')
def run_mystic_depth():
    df = pd.read_csv('./static/HACKA_DS_B03_WELL.csv')
    y = df['PSEUDO_DEPTH']
    reversed_y = y.sort_values(0, True, False)
    x = df['GR         ']
    graphs = [dict(data=[dict(x=x,y=reversed_y,type='scatter'),],layout=dict(title='first graph',width=500,height=1000))]
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('depth_template.html', ids=ids, graphJSON=graphJSON)

""" @app.route('/mystic-predicted')
def run_mystic_predicted():
    df = munging.load_log_data()
    filtered_df = df.loc[df['HACKANAME'] == 'B03']
    depth = filtered_df['TVDSS'].tolist()
    gr_actual = filtered_df['GR'].tolist()
    #gr_p10 = df['GR_PREDICT_P10'].tolist()
    # gr_p50 = df['GR_PREDICT_P50'].tolist()
    # gr_p90 = df['GR_PREDICT_P90'].tolist()
    trace0 = go.Scatter(x = gr_actual, y = depth,name = 'gr actual',line = dict(color = ('rgb(205, 12, 24)'), width = 4))
    #trace1 = go.Scatter(x = gr_p10, y = depth, name = 'gr P10', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace2 = go.Scatter(x = gr_p50, y = depth, name = 'gr P50', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace3 = go.Scatter(x = gr_p90, y = depth, name = 'gr P90', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))

    data = [trace0]
    layout = dict(title = 'Mystic Predict', xaxis=dict(title='G RAPI'), yaxis=dict(title='Depth', autorange='reversed'))
    fig = dict(data=data, layout=layout)
    plot(fig, filename='templates/test_predicted')
    # return render_template('test_predicted.html') """

@app.route('/home')
def index():
    return render_template(
        'test_drop.html',
        data=[{'name':'B03'}, {'name':'B05'}, {'name':'B06'}, {'name':'B08'}, {'name':'B12'}, {'name':'B13'}, {'name':'B14'}, {'name':'B200'}, {'name':'G06'}, {'name':'G08'}, {'name':'G09'}, {'name':'G10'}, {'name':'G12'}, {'name':'G15'}, {'name':'G16'}, {'name':'G070'}, {'name':'B0700'}, {'name':'G17'}])

@app.route("/mystic-predicted" , methods=['GET', 'POST'])
def test():
    select = request.form.get('comp_select')
    df = munging.load_log_data()
    filtered_df = df.loc[df['HACKANAME'] == select]
    depth = filtered_df['TVDSS'].tolist()
    gr_actual = filtered_df['GR'].tolist()
    #gr_p10 = df['GR_PREDICT_P10'].tolist()
    # gr_p50 = df['GR_PREDICT_P50'].tolist()
    # gr_p90 = df['GR_PREDICT_P90'].tolist()
    trace0 = go.Scatter(x = gr_actual, y = depth,name = 'gr actual',line = dict(color = ('rgb(205, 12, 24)'), width = 4))
    #trace1 = go.Scatter(x = gr_p10, y = depth, name = 'gr P10', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace2 = go.Scatter(x = gr_p50, y = depth, name = 'gr P50', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace3 = go.Scatter(x = gr_p90, y = depth, name = 'gr P90', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))

    data = [trace0]
    layout = dict(title = 'Mystic Predict', xaxis=dict(title='G RAPI'), yaxis=dict(title='Depth', autorange='reversed'))
    fig = dict(data=data, layout=layout)
    plot(fig, filename='templates/test_predicted')
    # return render_template('test_predicted.html')
    return(str(select)) # just to see what select is

if __name__=='__main__':
    app.run(debug=True)


@app.route('/dashboard')
def run_main():
    df = munging.load_log_data()
    x = df['TVDSS']
    y = df['GR']
    plt.plot(x, y)
    plt.savefig('static/raw_data.png')
    return render_template('raw_data_template.html', url='/static/raw_data.png')

@app.route('/minimal')
def minimal():
    data = request.args.get('data', '')
    return render_template('minimal.html', data=data)

if __name__ == "__main__":
    # for debug
    app.run(port=5000, debug=True)
    # for production
    # app.run()