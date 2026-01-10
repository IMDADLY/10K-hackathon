import pandas as pd
import numpy as np
import osmnx as ox
import random
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# -----------------------------
# Load CSV and create synthetic traffic
# -----------------------------
df = pd.read_csv("kollam_top500_high_risk.csv")
df['traffic'] = [random.randint(0, 10) for _ in range(len(df))]

# -----------------------------
# Map highway type and approximate speed
# -----------------------------
def avg_speed_from_highway(highway):
    mapping = {
        'primary': 60,
        'secondary': 50,
        'tertiary': 40,
        'residential': 30,
        'service': 20
    }
    return mapping.get(highway, 40)

# Create OSM graph
G = ox.graph_from_place("Kollam, Kerala, India", network_type="drive")
nodes, edges = ox.graph_to_gdfs(G)
edges = edges.reset_index()  # Fixes KeyError by adding 'u', 'v', 'key'

# Map node OSMID to most common highway type
highway_map = {}
for node_id in df['osmid']:
    connected_edges = edges[(edges['u'] == node_id) | (edges['v'] == node_id)]
    if not connected_edges.empty:
        hw_series = connected_edges['highway']
        # Handle multi-value highway lists
        hw_series = hw_series.apply(lambda x: x[0] if isinstance(x, list) else x)
        highway_map[node_id] = hw_series.mode()[0]  # most common
    else:
        highway_map[node_id] = 'residential'

df['highway'] = df['osmid'].map(highway_map)
df['speed_kph'] = df['highway'].apply(avg_speed_from_highway)
df['speed_norm'] = df['speed_kph'] / df['speed_kph'].max()  # normalize 0-1

# -----------------------------
# Load dataset for logistic regression
# -----------------------------
data = pd.read_csv("data-1.csv")

# Ensure indices align with df if necessary
# For simplicity, assume first len(df) rows correspond
X = data.iloc[:len(df), 1:3]  # features
y = (data.iloc[:len(df), 0] < 16).astype(int)  # target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Create and train logistic regression model
model = LogisticRegression(max_iter=8000)
model.fit(X_scaled, y)

print("Weights :", model.coef_[0])
print("Intercept (β0):", model.intercept_[0])

w = model.coef_[0]

# -----------------------------
# Function to find closest row index
# -----------------------------
def find_closest_index(x_value, y_value, df):
    # columns 1 and 2 are traffic and speed_norm
    distances = (df.iloc[:, 1] - x_value)**2 + (df.iloc[:, 2] - y_value)**2
    return distances.idxmin()

# Example: closest row for a given traffic/speed
example_row_idx = 0  # first row
traffic_val = df.loc[example_row_idx, 'traffic']
speed_val = df.loc[example_row_idx, 'speed_norm']

closest_idx = find_closest_index(traffic_val, speed_val, df)

# Fix "2 minus" problem by aligning df index to X_scaled index
# Map df index to position in X_scaled
closest_pos = df.index.get_loc(closest_idx)  # gives 0-based position
c = X_scaled[closest_pos]

# -----------------------------
# Probability calculation using logistic regression
# -----------------------------
P = 1 / (1 + np.exp(-(model.intercept_[0] + np.dot(w, c))))

if P > 0.7:
    print(f"High Accident Risk for example row {example_row_idx}")
else:
    print(f"Low Accident Risk for example row {example_row_idx}")

# -----------------------------
# Compute combined score for all rows
# -----------------------------
# Predict probabilities for the aligned subset
probabilities = model.predict_proba(X_scaled)[:, 1]  # probability of class 1

w_risk = 0.5
w_active = 0.5

df['combined_score'] = w_risk * df['risk_score'] + w_active * probabilities
# Create a new DataFrame with just the risk and coordinates
output_df = df[['x', 'y', 'combined_score']].copy()

# Save to CSV
output_df.to_csv("kollam_top500_updated_risk.csv", index=False)

print("New CSV with combined risk and coordinates saved as 'kollam_top500_updated_risk.csv'.")

print("Top 500 intersections with synthetic traffic/speed combined risk calculated.")
