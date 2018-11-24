from flask import Flask
from flask import request
from flask import render_template
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import json

import plotly



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

@app.route('/minimal')
def minimal():
    data = request.args.get('data', '')
    return render_template('minimal.html', data=data)


if __name__ == "__main__":
    # for debug
    app.run(port=5000, debug=True)
    # for production
    # app.run()