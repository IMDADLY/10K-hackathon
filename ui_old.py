import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("kollam_top500_high_risk.csv")
    return df.head(500)


if "nodes_df" not in st.session_state:
    st.session_state.nodes_df = load_data()
nodes_df = st.session_state.nodes_df
colors = {"High": "Red", "Medium": "Yellow", "Low": "Green"}

st.set_page_config(layout="wide")
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("Accident Hotzones")

col1, col2 = st.columns([1, 5])
user_location = streamlit_geolocation()
st.session_state["lat"] = user_location["latitude"]
st.session_state["lon"] = user_location["longitude"]

@st.cache_data
def create_map(df):
    m = folium.Map(location=[8.8932, 76.6141], zoom_start=10)

    for _, node in nodes_df.iterrows():
        folium.CircleMarker(
            location=[node["y"], node["x"]],
            radius=4,
            color=colors[node["risk_level"]],
            fill=True,
            fill_color=colors[node["risk_level"]],
            fill_opacity=0.5,
            popup=node["risk_level"] + " Risk"
        ).add_to(m)
    
    return m

if "map" not in st.session_state:
        st.session_state.map = create_map(nodes_df)
with col2:
    map_data = st_folium(st.session_state.map, height=500, width=900)

with col1:
    option = st.selectbox(
    "Select Location",
    ["Kollam"]
    )

    rain = st.slider("Rain factor", 0.0, 1.0)
    #no_of_int = st.number_input("No. of intersections", 10, 100, key="n")

    st.success(f"Selected Location:")
    st.write(f"Latitude: {st.session_state.get("y", "")}")
    st.write(f"Longitude: {st.session_state.get("x", "")}")
    if map_data and map_data.get("last_clicked"):
        st.session_state["y"] = map_data["last_clicked"]["lat"]
        st.session_state["x"] = map_data["last_clicked"]["lng"]