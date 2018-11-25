# coding=utf-8
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import json
from mysticbit import ml
from mysticbit import munging
import dash
import dash_core_components as dcc
import dash_html_components as html 

import plotly
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot, iplot, download_plotlyjs
from dash.dependencies import Input, Output
from datetime import datetime as dt
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data as web


# dash_app = dash.Dash(__name__)
# server = dash_app.server
app = Flask(__name__)
Bootstrap(app)

wells = [{'name':'B03'}, {'name':'B05'}, {'name':'B06'}, {'name':'B08'}, {'name':'B12'}, {'name':'B13'}, {'name':'B14'}, {'name':'B200'}, {'name':'G06'}, {'name':'G08'}, {'name':'G09'}, {'name':'G10'}, {'name':'G12'}, {'name':'G15'}, {'name':'G16'}, {'name':'G070'}, {'name':'B0700'}, {'name':'G17'}]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/mystic-bit')
def run_mystic_bit():
    df = pd.read_csv('./static/HACKA_DS_WELL_SPATIAL.csv')
    x = df['X'].tolist()
    y = df['Y'].tolist()
    labels = df['hackname'].tolist()
    plt.subplots_adjust(bottom = 0.1)
    plt.scatter(x, y, marker='o',cmap=plt.get_cmap('Spectral'))
    for label, x,y in zip(labels, x, y):
        plt.annotate(
            label,
            xy=(x,y), xytext=((x-42), (y+42)),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
            arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
    plt.plot()
    plt.xlim(-15,30)
    plt.ylim(-15,30)
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

@app.route('/dash-scatter')
def run_dash_scatter():
    dash_app =  dash.Dash(__name__,
        server=app,
        url_base_pathname='/dashscatter/')

    df_logs = munging.load_log_data()
    #TODO get the new data frame
    df_ml = munging.create_ml_dataframe(df_logs)
    X_cols = [c for c in df_ml.columns if 'lag' in c]
    y_cols = [c for c in df_ml.columns if 'futr' in c]
    models = ml.make_multiple_models(df_ml, X_cols, y_cols)
    df_pred = ml.make_predictions(models, df_ml, X_cols, y_cols)

    dash_app.layout = html.Div([
        html.H1('Stock Tickers'),
        dcc.Dropdown(
            id='my-dropdown',
            options=[
                {'label': 'B03' ,'value':'B03'},
                {'label': 'B05' ,'value':'B05'}, 
                {'label': 'B06' ,'value':'B06'}, 
                {'label': 'B08' ,'value':'B08'}, 
                {'label': 'B12' ,'value':'B12'}, 
                {'label': 'B13' ,'value':'B13'}
            ],
            value='B03'
        ),
        dcc.Graph(id='my-graph', style={'height': 1000, 'width': 300})
    ])

    @dash_app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
            # Filtering on update
        well_name = selected_dropdown_value
        bit_depth = '999'
        df_pred_filtered = munging.get_log_predictions(df_pred, well_name, bit_depth)

        # df_logs = munging.load_log_data()
        filtered_df = df_logs.loc[df_logs['HACKANAME'] == selected_dropdown_value]
        return {
            'data': [{
                'x': filtered_df.GR,
                'y': filtered_df.TVDSS
            }, {
                'x': filtered_df.DT,
                'y': filtered_df.TVDSS
            }]
        }

    return redirect('/dashscatter/')



if __name__ == "__main__":
    # for debug
    app.run(port=5000, debug=True)
    # for production
    # app.run()