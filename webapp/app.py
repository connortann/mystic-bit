# coding=utf-8
import json
import sys
from os import path
from datetime import datetime as dt
import random, threading, webbrowser

from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.append(path.abspath('..'))
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data as web
from mysticbit import munging, ml

import dash
import dash_core_components as dcc
import dash_html_components as html 
from dash.dependencies import Input, Output

import plotly
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot, iplot, download_plotlyjs


app = Flask(__name__)
Bootstrap(app)

wells = ['B03','B05','B06','B08','B12','B13','B14','B200','G06','G08','G09','G10','G12','G15','G16','G070','B0700','G17']
wells_names = [{'name': v} for v in wells]
wells_labels = [{'label': 'well {0}'.format(v), 'value' : v} for v in wells]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

@app.route('/')
def home():
    return redirect('/mystic-bit')

@app.route('/mystic-bit')
def run_mystic_bit():
    df = pd.read_csv('./static/HACKA_DS_WELL_SPATIAL.csv')
    x = df['X'].tolist()
    y = df['Y'].tolist()
    labels = df['hackname'].tolist()
    # sns_wells = sns.load_dataset(df)
    plt = sns.relplot(x="X", y="Y", hue="hackname", size="hackname", 
    sizes=(150, 150), facet_kws=dict({'legend_out':True}),data=df)

    new_title = 'Wells'
    plt._legend.set_title(new_title)

    # plt.subplots_adjust(bottom = 0.1)
    # plt.scatter(x, y, s=8**2, marker='o',facecolors='none', edgecolors='r', label="Well")
    # plt.xlabel("X Axis")
    # plt.ylabel("Y Axis")
    # plt.legend(loc='upper left')
    # for label, x,y in zip(labels, x, y):
    #     plt.annotate(
    #         label,
    #         xy=(x,y), xytext=((x-42), (y+42)),
    #         textcoords='offset points', ha='right', va='bottom',
    #         bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
    #         arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
    # plt.plot()
    plt.set(xlim=(0, 30))
    plt.set(ylim=(0, 30))
    plt.savefig('static/map_plot.png')
    return render_template('my_template.html', name ='map', url='/static/map_plot.png')
    

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

@app.route('/home')
def index():
    return render_template(
        'test_drop.html',
        data=wells_names)

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
    trace1 = go.Scatter(x = filtered_df['DT'], y = depth,name = 'DT',line = dict(color = ('rgb(205, 12, 24)'), width = 4))
    #trace1 = go.Scatter(x = gr_p10, y = depth, name = 'gr P10', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace2 = go.Scatter(x = gr_p50, y = depth, name = 'gr P50', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))
    #trace3 = go.Scatter(x = gr_p90, y = depth, name = 'gr P90', line = dict(color = ('rgb(22, 96, 167)'), width = 4, dash = 'dash'))

    data = [trace0, trace1]
    layout = dict(title = 'Mystic Predict', xaxis=dict(title='G RAPI', fixedrange=True), yaxis=dict(title='Depth', autorange='reversed'))

    subfig = tools.make_subplots(cols=2, shared_yaxes=True)
    subfig.append_trace(trace0, 1, 1)
    subfig.append_trace(trace1, 1, 2)
    subfig['layout'].update(**layout)
    #fig = dict(data=data, layout=layout)
    plot(subfig, filename='templates/test_predicted')
    # return render_template('test_predicted.html')
    return(str(select)) # just to see what select is

	
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

@app.route('/dash-test')
def run_dash_test():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    dash_app = dash.Dash(__name__, 
    external_stylesheets=external_stylesheets,
    server=app,
    url_base_pathname='/dashtest/')

    dash_app.layout = html.Div(children=[
        
        html.H1(children='Hello Dash'),
        html.Div(children='''Dash: A web application framework for Python.'''),

        dcc.Graph(id='example graph', figure={
            'data' : [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualisation'
            }
        })
    ])
    return redirect('/dashtest/')

@app.route('/dash-slider')
def run_dash_slider():
    df = munging.load_log_data()

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    dash_app = dash.Dash(__name__, 
    external_stylesheets=external_stylesheets,
    server=app,
    url_base_pathname='/dashslider/')


    dash_app.layout = html.Div([
        dcc.Graph(id='graph-with-slider',),
        dcc.Slider(
            id='tvdss-slider',
            min=df['GR'].min(),
            max=df['GR'].max(),
            value=df['GR'].min(),
            marks={str(tvdss): str(tvdss) for tvdss in df['GR'].unique()}
        )
    ])


    @dash_app.callback(
        dash.dependencies.Output('graph-with-slider', 'figure'),
        [dash.dependencies.Input('tvdss-slider', 'value')])
    
    def update_figure(selected_tvdss):
        filtered_df = df[df.tvdss == selected_tvdss]
        traces = []
        for i in filtered_df.HACKANAME.unique():
            df_by_well = filtered_df[filtered_df['HACKANAME'] == i]
            traces.append(go.Scatter(
                x=df_by_well['GR'],
                y=df_by_well['TVDSS'],
                text=df_by_well['HACKANAME'],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ))
        return {
            'data': traces,
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'tvdss'},
                yaxis={'title': 'gr', 'range': [0, 5000]},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    return redirect('/dashslider/')

@app.route('/models-predictions')
def run_dash_scatter():
    dash_app =  dash.Dash(__name__,
        server=app,
        url_base_pathname='/modelspredictions/')

    df_logs = munging.load_log_data()
    df_ml = munging.create_ml_dataframe(df_logs)
    X_cols = [c for c in df_ml.columns if 'lag' in c]
    y_cols = [c for c in df_ml.columns if 'futr' in c]
    models = ml.make_multiple_models(df_ml, X_cols, y_cols)
    df_pred = ml.make_predictions(models, df_ml, X_cols, y_cols)

    dash_app.layout = html.Div([
        html.A(html.Button('Home Page', id='home-button'), href='/mystic-bit'),
        html.H1('Preditcions'),
        dcc.Dropdown(
            id='my-dropdown',
            options=wells_labels,
            value='B05'
        ),
        dcc.Slider(
        id='my-slider',
        min=1700,
        max=1900,
        step=2,
        value=1800,
        ),
        dcc.Graph(id='my-graph', style={'height': 1000, 'width': 300})
    ])

    @dash_app.callback(Output('my-graph', 'figure'), [
        Input('my-dropdown', 'value'),
        Input('my-slider', 'value')])
    def update_graph(selected_dropdown_value, selected_depth):
            # Filtering on update
        well_name = selected_dropdown_value
        bit_depth = selected_depth
        try:
            df_pred_filtered = munging.get_log_predictions(df_pred, well_name, bit_depth)
        except AssertionError:
            df_pred_filtered = None

        # df_logs = munging.load_log_data()
        filtered_df = df_logs.loc[df_logs['HACKANAME'] == selected_dropdown_value]
        return {
            'data': [{
                'x': filtered_df.GR,
                'y': filtered_df.TVDSS
            }, {
                'x': df_pred_filtered.value,
                'y': df_pred_filtered.TVDSS,
                'type': 'scatter',
            }],
            'layout': go.Layout(yaxis={'autorange': 'reversed'})
        }

    return redirect('/modelspredictions/')

# launch the app in a new web browser page
port = 5000
url = "http://127.0.0.1:{0}/mystic-bit".format(port)
threading.Timer(1.25, lambda: webbrowser.open(url)).start()
app.run(port=port, debug=False)