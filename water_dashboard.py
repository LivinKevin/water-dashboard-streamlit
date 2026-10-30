import streamlit as st
import pandas as pd # data manipulation
import plotly.express as px # data visualization

def load_data(source):
    """Read a CSV and clean it up."""
    df = pd.read_csv(source)
    # remove stray spaces in headers
    df.columns = df.columns.str.strip()
    # drop completely empty columns
    return df.dropna(axis=1, how="all")

def pick_default(cols, keywords):
    """Index of the first column matching a keyword (keywords checked in order), else 0."""
    for k in keywords:
        for i, c in enumerate(cols):
            if k in c.lower():
                return i
    return 0

def find_lat_lon(df):
    """Find latitude/longitude columns by name, or (None, None)."""
    lat = next((c for c in df.columns if c.lower() in ("latitude", "lat")), None)
    lon = next((c for c in df.columns if c.lower() in ("longitude", "lon", "lng", "long")), None)
    return lat, lon

def map_zoom(df, lat, lon):
    """Rough zoom level from how spread out the points are."""
    span = max(df[lat].max() - df[lat].min(), df[lon].max() - df[lon].min())
    return 16 if span < 0.005 else 12 if span < 0.1 else 8 if span < 1 else 4

# to run: streamlit run name_of_file.py
# if it doesn't work, try: python -m streamlit run name_of_file.py

st.title("Water Quality Dashboard")
st.header("Streamlit Data App")
st.subheader("By: Kevin Garcia")

st.divider()

st.markdown("""
### Welcome to my Water Quality Dashboard
This is an interactive dashboard for water quality data analysis. Upload any water quality CSV in
the sidebar, or use the default dataset: a February 2022 survey of Biscayne Bay with 942 readings.

### How to use it
- **Data:** browse the raw table and summary statistics, and choose which columns to show.
- **Charts:** choose a parameter (temperature, salinity, pH, and so on) and
  compare two of them against each other.
- **Maps:** if your file has latitude and longitude columns, see where the readings were taken.

A file works best if it has numeric measurement columns, a time or date column, and latitude/longitude columns for the map.
""")

st.sidebar.header("File Upload")
st.sidebar.info("Upload a CSV file with water quality data")

uploaded_file=st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

source = uploaded_file if uploaded_file is not None else "biscayneBay_waterquality.csv"
try:
    df = load_data(source)
except Exception as e:
    st.error(f"Could not read that file: {e}")
    st.stop()

numeric_cols = df.select_dtypes("number").columns.tolist()
if not numeric_cols:
    st.error("This file has no numeric columns to plot.")
    st.stop()

lat, lon = find_lat_lon(df)
tables, plots, maps, insights = st.tabs(["Data", "Charts", "Maps", "Insights"])

with tables:
    st.dataframe(df)
    st.caption("Raw Data")
    st.dataframe(df.describe())
    st.caption("Descriptive Statistics")
    cols = st.multiselect("Columns to display", df.columns.tolist(),
                         default=df.columns.tolist()[:8])
    st.dataframe(df[cols])

with plots:
    st.subheader("Line Chart")
    x_col = st.selectbox("X axis", df.columns.tolist(),
                         index=pick_default(df.columns.tolist(), ["time", "date"]))
    parameter = st.selectbox("Parameter to plot", numeric_cols,
                             index=pick_default(numeric_cols, ["temperature", "temp"]))
    x_label = f"{x_col} (mm:ss)" if x_col == "Time" else x_col
    fig1 = px.line(df, x=x_col, y=parameter,
                   title=f"{parameter} over {x_col}",
                   labels={x_col: x_label})
    fig1.update_xaxes(nticks=10)                              # fewer, readable ticks
    fig1.update_traces(name=parameter, showlegend=True)       # adds a legend entry
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"How {parameter} changes over {x_col} during the survey.")

    sx = st.selectbox("Scatter X", numeric_cols, index=pick_default(numeric_cols, ["temperature", "temp"]), key="sx")
    sy = st.selectbox("Scatter Y", numeric_cols, index=pick_default(numeric_cols, ["sal"]), key="sy")
    fig2 = px.scatter(df, x=sx, y=sy, title=f"{sx} vs {sy}")
    fig2.update_traces(name=f"{sy} readings", showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Each point is one reading, comparing {sx} (x-axis) with {sy} (y-axis).")

    if lat and lon:
        z_col = st.selectbox("3D height (Z axis)", numeric_cols,
                             index=pick_default(numeric_cols, ["water column"]), key="z3d")
        c3d = st.selectbox("3D color", numeric_cols,
                           index=pick_default(numeric_cols, ["temperature", "temp"]), key="c3d")
        fig3 = px.scatter_3d(df, x=lon, y=lat, z=z_col, color=c3d,
                             title=f"Survey path with {z_col}, colored by {c3d}",
                             height=600)
        if st.checkbox("Reverse Z axis (use for depth)"):
            fig3.update_scenes(zaxis_autorange="reversed")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption(f"The survey path in 3D: {z_col} on the vertical axis, colored by {c3d}.")
    else:
        st.info("No latitude/longitude columns found, so the 3D view is unavailable.")

with maps:
    st.subheader("Maps")
    if lat and lon:
        clean = df.dropna(subset=[lat, lon])
        color = st.selectbox("Color by", numeric_cols,
                             index=pick_default(numeric_cols, ["temperature", "temp"]), key="mapcolor")
        first_map = px.scatter_map(
            clean, lat=lat, lon=lon, color=color,
            center={"lat": clean[lat].mean(), "lon": clean[lon].mean()},
            zoom=map_zoom(clean, lat, lon),
            color_continuous_scale="viridis",
            title=f"Survey track colored by {color}")
        st.plotly_chart(first_map, use_container_width=True)
        st.caption(f"Each dot is a reading along the survey track, colored by {color}.")
    else:
        st.info("No latitude/longitude columns found, so the map is unavailable.")

with insights:
    st.subheader("Insights")

    # Summary of whichever parameter is selected on the Charts tab
    stats = df[parameter]
    st.write(f"**{parameter}** ranged from {stats.min():.2f} to {stats.max():.2f} "
             f"(average {stats.mean():.2f}) across {len(df)} readings.")

    # Relationship between the two scatter-chart parameters
    corr = df[sx].corr(df[sy])
    if pd.notna(corr):
        strength = "strong" if abs(corr) >= 0.7 else "moderate" if abs(corr) >= 0.4 else "weak"
        direction = "positive" if corr > 0 else "negative"
        st.write(f"**{sx}** and **{sy}** have a {strength} {direction} "
                 f"correlation ({corr:.2f}).")
