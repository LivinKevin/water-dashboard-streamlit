# Water Quality Dashboard

An interactive Streamlit app for exploring water quality data.

**Live app:** https://water-dashboard-bykeving.streamlit.app/ 

## Purpose
Lets users explore water quality measurements through tables, interactive
Plotly charts, and a map. Users can upload their own CSV or use the default dataset.

## Dataset
The default dataset, `biscayneBay_waterquality.csv`, is a February 4, 2022 survey of
Biscayne Bay with 942 readings and 69 columns, including GPS position, temperature,
salinity, pH, dissolved oxygen, turbidity, and water depth.
Source: Professor Gregory Reis

Uploaded CSVs work best with numeric measurement columns, a time or date column,
and latitude/longitude columns (needed for the map and 3D view).

## How to use
- **Data tab:** browse the table, choose columns to display, and see summary statistics.
- **Charts tab:** pick a parameter for the line chart, compare any two parameters
  in the scatter chart, and view the 3D survey path.
- **Maps tab:** see the survey track on a map, colored by a parameter you choose.
- **Insights tab:** summary statistics and correlation for your selections.
- **Sidebar:** upload your own CSV to replace the default data.

## Run locally
1. `pip install -r requirements.txt`
2. `streamlit run water_dashboard.py`

## Development process (AGILE)
Built using user stories tracked as GitHub Issues: https://github.com/LivinKevin/water-dashboard-streamlit/issues 
