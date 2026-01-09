import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

nodes_df = pd.read_csv("kollam_intersection_risk.csv")

st.set_page_config(layout="wide")
st.title("Accident Prone Areas")

# Default map center (Kollam example)
center_lat, center_lon = 8.8932, 76.6141

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13
)

colors = {"High": "Red", "Medium": "Yellow", "Low": "Green"}

for index, node in nodes_df.head(100).iterrows():
    folium.CircleMarker(
        location=[node["y"], node["x"]],
        radius=2,
        color=colors[node["risk_level"]],
        fill=True,
        fill_color=colors[node["risk_level"]],
        fill_opacity=0.5,
        popup=node["risk_level"] + " Risk"
    ).add_to(m)

# Render map and capture interactions
map_data = st_folium(
    m,
    height=500,
    width=900
)

# Extract clicked coordinates
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    st.success(f"Selected Location:")
    st.write(f"Latitude: {lat}")
    st.write(f"Longitude: {lon}")
