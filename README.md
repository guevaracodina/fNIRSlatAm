# fNIRSlatAm
Code to create an fNIRS publication network in Latin American countries

Please cite:

Guevara, E., Mesquita, R. C., & Orihuela-Espina, F. (2025). Emerging panorama of functional near-infrared spectroscopy in Latin America. _Neurophotonics_, **13**(S1), S13002. https://doi.org/10.1117/1.NPh.13.S1.S13002

## Installation instructions
Install MiniConda: Download and install MiniConda from the [official site](https://docs.conda.io/en/latest/miniconda.html)

```
# Create & activate a new conda environment
conda create -n map_env python=3.9
conda activate map_env
```

```
# Install core Python libraries
conda install -c conda-forge pandas geopandas matplotlib shapely cartopy
```

```
# Install Excel‐writing support
conda install -c conda-forge xlsxwriter
```

```
# Install country‑lookup package
conda install -c conda-forge pycountry
```

## Running the code
```
python master_script.py
python latam_map.py
```

## Output
<img src="./country_connectivity_map_variable_width_solid.png">
<img src="./country_connectivity_map_other_side.png">
