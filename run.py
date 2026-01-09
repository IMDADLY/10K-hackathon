import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------
# 1. Set place and filenames
# -----------------------------
place = "Kollam, Kerala, India"  # city-level
graph_file = "kollam_city.graphml"

# -----------------------------
# 2. Load or download OSM graph
# -----------------------------
if os.path.exists(graph_file):
    print("Loading saved OSM graph...")
    G = ox.load_graphml(graph_file)
else:
    print("Downloading Kollam city road network from OSM...")
    G = ox.graph_from_place(place, network_type='drive')
    ox.save_graphml(G, graph_file)
    print("Graph saved for future use.")

# -----------------------------
# 3. Convert to GeoDataFrames
# -----------------------------
nodes, edges = ox.graph_to_gdfs(G)
print(f"Total nodes: {len(nodes)}, edges: {len(edges)}")

# -----------------------------
# 4. Compute intersection degree
# -----------------------------
nodes['degree'] = [G.degree(n) for n in G.nodes()]
intersections = nodes[nodes['degree'] > 2].copy()  # only real intersections
print(f"Total intersections: {len(intersections)}")

# -----------------------------
# 5. Extract features from edges
# -----------------------------
intersections['maxspeed'] = 0
intersections['road_type_score'] = 0
intersections['footway_present'] = 0
intersections['crossing_present'] = 0

for i, (node_id, node) in enumerate(intersections.iterrows(), 1):
    if i % 50 == 0:
        print(f"Processing intersection {i}/{len(intersections)}...")
    
    connected_edges = list(G.edges(node_id, data=True))
    
    maxspeeds, road_types, footway, crossing = [], [], [], []
    
    for u, v, data in connected_edges:
        # Maxspeed
        speed = data.get('maxspeed')
        if isinstance(speed, list):
            speed = speed[0]
        if speed is not None:
            try:
                maxspeeds.append(int(speed))
            except:
                pass
        
        # Road type
        highway = data.get('highway')
        if isinstance(highway, list):
            highway = highway[0]
        road_types.append(highway)
        
        # Footway / Crossing presence
        footway.append(1 if 'footway' in data.get('footway', '') else 0)
        crossing.append(1 if 'crossing' in data.get('crossing', '') else 0)
    
    intersections.at[node_id, 'maxspeed'] = np.mean(maxspeeds) if maxspeeds else 40
    road_score_map = {'primary':5, 'secondary':4, 'tertiary':3, 'residential':2, 'service':1}
    road_scores = [road_score_map.get(r, 2) for r in road_types]
    intersections.at[node_id, 'road_type_score'] = np.mean(road_scores)
    intersections.at[node_id, 'footway_present'] = max(footway) if footway else 0
    intersections.at[node_id, 'crossing_present'] = max(crossing) if crossing else 0

# -----------------------------
# 6. Compute Relative Risk Score
# -----------------------------
intersections['risk_score'] = (
    intersections['degree'] * 0.3 +
    intersections['road_type_score'] * 0.3 +
    intersections['maxspeed']/50*0.3 -
    intersections['footway_present']*0.05 -
    intersections['crossing_present']*0.05
)
# Normalize 0-1
intersections['risk_score'] = (intersections['risk_score'] - intersections['risk_score'].min()) / \
                              (intersections['risk_score'].max() - intersections['risk_score'].min())

# -----------------------------
# 7. Fix: Make node IDs a column
# -----------------------------
intersections = intersections.reset_index()  # now 'osmid' exists

# -----------------------------
# 8. Classify Risk Levels
# -----------------------------
bins = [0, 0.33, 0.66, 1.0]
labels = ['Low', 'Medium', 'High']
intersections['risk_level'] = pd.cut(intersections['risk_score'], bins=bins, labels=labels, include_lowest=True)

# -----------------------------
# 9. Plot Risk Map
# -----------------------------
risk_colors = {'Low':'green', 'Medium':'orange', 'High':'red'}
fig, ax = plt.subplots(figsize=(12,12))
edges.plot(ax=ax, linewidth=0.5, edgecolor='gray')

for level, color in risk_colors.items():
    intersections[intersections['risk_level']==level].plot(ax=ax, markersize=20, color=color, label=level)

plt.title("Pedestrian Accident Risk by Intersection – Kollam City")
plt.legend(title='Risk Level')
plt.axis('off')
plt.show()
plt.savefig("kollam_risk_map.png", dpi=300)
print("Risk map saved as kollam_risk_map.png")

# -----------------------------
# 10. Export CSV and GeoJSON
# -----------------------------
intersections[['osmid','x','y','risk_score','risk_level']].to_csv("kollam_intersection_risk.csv", index=False)
intersections.to_file("kollam_intersection_risk.geojson", driver="GeoJSON")
print("CSV and GeoJSON exported.")

# -----------------------------
# 11. Top 50 High-Risk Intersections
# -----------------------------
top50 = intersections.sort_values(by='risk_score', ascending=False).head(50)
top50[['osmid','x','y','risk_score','risk_level']].to_csv("kollam_top50_high_risk.csv", index=False)
print("Top 50 high-risk intersections saved to kollam_top50_high_risk.csv")

# Save the risk CSV
intersections.to_csv("Kollam_intersection_risk.csv", index=False)
print("CSV saved: Kollam_intersection_risk.csv")

