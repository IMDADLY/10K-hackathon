This system estimates pedestrian accident risk at road intersections using infrastructure-based indicators derived from OpenStreetMap (OSM).
The model is rule-based and interpretable, designed for environments where historical accident data is unavailable.

Instead of using black-box machine learning, we use a weighted risk scoring model based on known traffic safety principles:
Higher speeds, complex intersections, major roads, and missing pedestrian infrastructure increase pedestrian risk.

Each intersection is assigned a normalized risk score ∈ [0, 1].

For each intersection node i, the following parameters are computed:

1.Intersection complexity: Reprsents the number of roads meeting at the intersection

2.Maximum speed: maximum speed of assigned road segments. If maximum speed is missing, a default value is assigned based on road type. 

3.road type risk: 

primary	1.0
secondary	0.8
tertiary	0.6
residential	0.4
service / others	0.2

4.Pedestrian infrastructure

checks if pedestrian footpath is present or not. Footpath not present = 0, footpath is present = 1.
