# Mystic Bit

### Team

* Connor Tann
* Justin Boylan-Toomey
* Patrick Davies
* Lawrie
* Alessandro
* Dan Austin
* Jeremy Fortun

### Vision

Predict permeability ahead of the bit, using offset well log data.

Also predict uncertainty range

Show simulation of drilling, with predictions updating

### Repo layout

- notebooks: Jupyter notebooks
- mysticbit: module to store key python functions
- data: data (obvs)
- webapp/petex-hackathon: plotted/interactive charts

### Conda environment

To create the python environment (windows), use:
```bash
conda create -n mysticbit python=3 anaconda
conda activate mysticbit
python -m ipykernel install --name mysticbit
```


