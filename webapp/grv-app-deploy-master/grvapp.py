# imports
from flask import Flask, render_template, request
import numpy as np
import matplotlib
matplotlib.use('agg', warn=False, force=True)
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
from bokeh.embed import components
import holoviews as hv

app = Flask(__name__)

#routes

@app.route('/')
def home():

    ### BEHROOZ
    # read volume file and assign to vol data frame
    #volume_file = ('static/Volumes')
    #vol = pd.read_csv(volume_file, delim_whitespace=True)
    # update volume file with commas
    volume_file = ('/var/www/html/grv-app-deploy/static/Volumes_comma.csv')
    vol = pd.read_csv(volume_file, delimiter=',')

    # GRVQHC
    # For GRV vs GRV quantiles by HC Column charts
    brush = alt.selection(type='interval')

    points = alt.Chart(vol).mark_point().encode(
        x='Oil_GRV_10_6:Q',
        y='Oil_GRV_quantile:Q', tooltip=['Num', 'Oil_GRV_quantile'],
        color=alt.condition(brush, 'Hc_column__m_:Q', alt.value('darkgray'))).add_selection(brush)


    bars = alt.Chart().mark_bar().encode(
        alt.Color('Hc_column__m_:Q', scale=alt.Scale(scheme='viridis')),
        y='Hc_column__m_:Q',
        x='Oil_GRV_10_6:Q'   
    ).transform_filter(brush)

    GRVQHC=alt.vconcat(points, bars, data=vol)
    GRVQHC = GRVQHC.to_json()

    # GRVOWC
    brush = alt.selection(type='interval')

    points = alt.Chart(vol).mark_point().encode(
        alt.X('Oil_GRV_10_6:Q'),
        alt.Y('OWC_depth:Q', scale=alt.Scale(zero=False)), tooltip=['Num', 'Oil_GRV_quantile'],
        color=alt.condition(brush, 'Oil_GRV_quantile:Q', alt.value('darkgray'))).add_selection(brush)


    bars = alt.Chart().mark_bar().encode(
        alt.Color('Oil_GRV_quantile:Q', scale=alt.Scale(scheme='viridis')),
        y='Hc_column__m_:Q',
        x='Oil_GRV_10_6:Q'   
    ).transform_filter(brush)

    GRVOWC=alt.vconcat(points, bars, data=vol)
    GRVOWC = GRVOWC.to_json()

    # GRVDNS
    # For the histogram of GRV density with Min,Mean,Max HC column indicators

    brush = alt.selection(type='interval', encodings=['x'])

    bars = alt.Chart(vol).mark_bar().encode(
        
        alt.X("GRV_density__m_:Q", bin=alt.Bin(maxbins=20)),
        alt.Y('count()', axis=alt.Axis(title='Min,Mean,Max HC')),
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7))
    ).add_selection(
        brush).properties(width=600, height=400)

    line1 = alt.Chart(vol).mark_rule(color='firebrick').encode(
        y='max(Hc_column__m_):Q',
        size=alt.SizeValue(2)
    ).transform_filter(
        brush
    )

    line2 = alt.Chart(vol).mark_rule(color='yellow').encode(
        y='min(Hc_column__m_):Q',
        size=alt.SizeValue(2)
    ).transform_filter(
        brush
    )

    line3 = alt.Chart(vol).mark_rule(color='green').encode(
        y='mean(Hc_column__m_):Q',
        size=alt.SizeValue(2)
    ).transform_filter(
        brush
    )

    GRVDNS=alt.layer(bars, line1, line2,line3, data=vol)
    GRVDNS = GRVDNS.to_json()

    
     
    return render_template('index.html', GRVQHC = GRVQHC, GRVOWC = GRVOWC, GRVDNS = GRVDNS)

@app.route('/altair')
def altair():
    ### GRAHAM
    # Read in the pickles
    #mid_unit = np.load('/var/www/html/grv-app-deploy/s3bucket/mid_unit.npy')
    #all_surfaces = np.load('/var/www/html/grv-app-deploy/s3bucket/realisation_1_10.npy')

    # load and reshape arrays
    f2_array_reshaped = np.load('/var/www/html/grv-app-deploy/static/f2_array_flat.npy').reshape(250, 162, 100)
    f3_array_reshaped = np.load('/var/www/html/grv-app-deploy/static/f3_array_flat.npy').reshape(250, 162, 100, 200)
    mid_unit = f2_array_reshaped
    all_surfaces = f3_array_reshaped
    
    # Pick one scenario
    nb = 3
    scenario = all_surfaces[:,:,:,nb]

    # Inject the surfaces into the mid_unit
    combined = mid_unit
    mid_unit[scenario==1] = np.nan
    
    # Make the Holoviews DataSpaces
    ds1 = hv.Dataset((np.arange(0,100,1), np.linspace(0., 162., 162), np.linspace(0., 250., 250),
                combined),
                kdims=['depth', 'y', 'x'],
                vdims=['z'])
       
    renderer = hv.renderer('bokeh')

    # Plot
    plot1 = ds1.to(hv.Image, ['x', 'depth']).redim(z=dict(range=(0,1))).options(height=400, width=700, colorbar=True, invert_yaxis=True, cmap='viridis')
    
    html1 = renderer.html(plot1)
    
    
    plot2 = ds1.to(hv.Image, ['x', 'y']).redim(z=dict(range=(0,1))).options(height=400, width=700, colorbar=True, invert_yaxis=True, cmap='viridis')
    
    html2 = renderer.html(plot2)

    return render_template('altair.html', html1 = html1, html2 = html2)

@app.route('/entropy')
def entropy():
    # Read in the pickles 
    #entropy = np.load('/var/www/html/grv-app-deploy/s3bucket/entropy_20180610.npy')
    #all_surfaces = np.load('/var/www/html/grv-app-deploy/s3bucket/realisation_1_10.npy')

    # load and reshape arrays
    f1_array_reshaped = np.load('/var/www/html/grv-app-deploy/static/f1_array_flat.npy').reshape(250, 162, 100)
    f3_array_reshaped = np.load('/var/www/html/grv-app-deploy/static/f3_array_flat.npy').reshape(250, 162, 100, 200)
    entropy = f1_array_reshaped
    all_surfaces = f3_array_reshaped
    
    # Pick one scenario
    nb = 3
    scenario = all_surfaces[:,:,:,nb]

    # Inject the surfaces into the mid_unit
    #combined = entropy
    entropy[scenario==1] = np.nan
    
    # Make the Holoviews DataSpaces
    ds1 = hv.Dataset((np.arange(0,100,1), np.linspace(0., 162., 162), np.linspace(0., 250., 250),
                entropy),
                kdims=['depth', 'y', 'x'],
                vdims=['z'])
       
    renderer = hv.renderer('bokeh')

    # Plot
    entropy1 = ds1.to(hv.Image, ['x', 'depth']).redim(z=dict(range=(0,1.6))).options(height=400, width=700, colorbar=True, invert_yaxis=True, cmap='viridis')
    
    entropy1plot = renderer.html(entropy1)
    
    
    entropy2 = ds1.to(hv.Image, ['x', 'y']).redim(z=dict(range=(0,1.6))).options(height=400, width=700, colorbar=True, invert_yaxis=True, cmap='viridis')
    
    entropy2plot = renderer.html(entropy2)

    return render_template('entropy.html', entropy1plot = entropy1plot, entropy2plot = entropy2plot)

# @app.route('/slider', methods = ['GET'])
# def slider():
#     if request.method == 'GET':
#         slider_value = request.args.get('arg1')
#         print('slider_value', slider_value)
#         return slider_value

@app.route('/test_image')
def show_me_image():
    return render_template('show_me_image.html')

@app.route('/large_image')
def show_me_large():
    return render_template('show_me_large.html')

# run
if __name__ == '__main__':
    #app.run(port=5002, debug=True)
    # Testing new app.run()
    #app.run(host="0.0.0.0", port=8000, debug=False)
    app.run()