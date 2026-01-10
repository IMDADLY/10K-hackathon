import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import copy

# ------------------ PAGE CONFIG ------------------
st.set_page_config(layout="wide")

# ------------------ DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("kollam_top500_updated_risk.csv")
    return df.head(200)

if "nodes_df" not in st.session_state:
    st.session_state.nodes_df = load_data()

nodes_df = st.session_state.nodes_df

colors = {
    "High": "red",
    "Medium": "yellow",
    "Low": "green"
}

# ------------------ UI CLEANUP ------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("Accident Hotzones")

col1, col2 = st.columns([1, 5])

# ------------------ USER LOCATION ------------------
user_location = streamlit_geolocation()

user_lat = None
user_lon = None

if user_location:
    user_lat = user_location.get("latitude")
    user_lon = user_location.get("longitude")

# ------------------ BASE MAP (CACHED) ------------------
@st.cache_data
def create_base_map(df):
    m = folium.Map(location=[8.8932, 76.6141], zoom_start=10)
    for _, node in df.iterrows():
        if node["combined_score"] > 0.5:
            color = "Red"
            risk = "High"
        elif node["combined_score"] > 0.4:
            color = "Yellow"
            risk = "Medium"
        else:
            color = "Green"
            risk = "Low"

        folium.CircleMarker(
            location=[node["y"], node["x"]],
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.5,
            popup=f"{risk} Risk.\n{round(node["combined_score"], 2)}"
        ).add_to(m)

    return m

# ------------------ MAP COMPOSITION ------------------
base_map = create_base_map(nodes_df)
m = copy.deepcopy(base_map)

# Add user location (dynamic, not cached)
if user_lat and user_lon:
    folium.CircleMarker(
        location=[user_lat, user_lon],
        radius=8,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.9,
        popup="Your Current Location"
    ).add_to(m)

# Auto-center once on user
if user_lat and user_lon and "centered" not in st.session_state:
    m.location = [user_lat, user_lon]
    m.zoom_start = 14
    st.session_state["centered"] = True

# ------------------ MAP DISPLAY ------------------
with col2:
    map_data = st_folium(m, height=500, width=900)

# ------------------ CONTROLS ------------------
with col1:

    # Store clicked location
    if map_data and map_data.get("last_clicked"):
        st.session_state["y"] = map_data["last_clicked"]["lat"]
        st.session_state["x"] = map_data["last_clicked"]["lng"]

    st.success("Selected Location:")
    st.write(f"Latitude: {st.session_state.get('y', '—')}")
    st.write(f"Longitude: {st.session_state.get('x', '—')}")

    if user_lat and user_lon:
        st.info("Your Current Location:")
        st.write(f"Latitude: {user_lat}")
        st.write(f"Longitude: {user_lon}")