# Mystic Bit

Project from OGA Hackathon London 2018.

Team: Connor Tann, Justin Boylan-Toomey, Patrick Davies, Lawrie Cowley, Alessandro Cristofori, Dan Austin, Jeremy Fortun

### Vision

Real-time, near-bit prediction 1-40m ahead of the drill-bit, using offset well log data

Also predict the uncertainty range.

Delivering value through:
* Improved drilling safety
* Faster decision making 
* Improved well targeting
* Leveraging existing field observations

### Results

A set of 30 Gradient Boosting Decision Tree Regressors were successfully trained on the well data,
enabling prediction ahead of the bit. Lagged OH features were created, and a quartile loss function
was used to capture uncertainty. 30+ separate models trained!

A mysticbit Python module was created to deploy the ML framework

Web app created with Flask, Plotly and Dash.


### Repo layout

- notebooks: Jupyter notebooks
- mysticbit: core python module containing ML models
- data: anonymized well log data data
- webapp/petex-hackathon: plotted/interactive charts

### Conda environment

To create the python environment (windows), use:
```bash
conda create -n mysticbit python=3 anaconda
conda activate mysticbit
python -m ipykernel install --name mysticbit
```


