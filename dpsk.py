from pyproj import Proj, Transformer
import numpy as np
from shapely.geometry import Polygon, LineString
import folium

# ******************** CONFIGURATION ********************
corners_gps = [
    (13.021767,74.791793),  # Top-left
    (13.021772,74.792076),  # Top-right
    (13.021647,74.792076),  # Bottom-right
    (13.021663,74.791792),  # Bottom-left
]

GRID_SPACING_METERS = 5
ALTITUDE_METERS = 30
# *******************************************************

# --- Previous UTM conversion and grid generation code ---
# (Same as previous implementation until waypoints_gps is generated)

def get_utm_zone(latitude, longitude):
    return int((longitude + 180) // 6 + 1)

# Convert GPS to UTM
lat, lon = corners_gps[0][0], corners_gps[0][1]
utm_zone = get_utm_zone(lat, lon)
utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
transformer_gps_to_utm = Transformer.from_proj(Proj('epsg:4326'), utm_proj, always_xy=True)
corners_utm = [transformer_gps_to_utm.transform(lon, lat) for lat, lon in corners_gps]

# Generate waypoints (same as before)
field_polygon = Polygon(corners_utm)
x_min, y_min = np.min(corners_utm, axis=0)
x_max, y_max = np.max(corners_utm, axis=0)
use_y_axis = (y_max - y_min) > (x_max - x_min)

lines = np.arange(y_min, y_max, GRID_SPACING_METERS) if use_y_axis else np.arange(x_min, x_max, GRID_SPACING_METERS)
waypoints_utm = []

for i, line_pos in enumerate(lines):
    if use_y_axis:
        line = LineString([(x_min, line_pos), (x_max, line_pos)])
    else:
        line = LineString([(line_pos, y_min), (line_pos, y_max)])
    
    intersection = line.intersection(field_polygon)
    if not intersection.is_empty:
        coords = list(intersection.coords) if intersection.geom_type != 'MultiLineString' else sum([list(g.coords) for g in intersection.geoms], [])
        waypoints_utm.extend(coords + [(None, None)] if i % 2 == 0 else coords[::-1] + [(None, None)])

# Convert back to GPS
transformer_utm_to_gps = Transformer.from_proj(utm_proj, Proj('epsg:4326'), always_xy=True)
waypoints_gps = []
for x, y in waypoints_utm:
    if x is None or y is None:
        waypoints_gps.append(None)
    else:
        lon, lat = transformer_utm_to_gps.transform(x, y)
        waypoints_gps.append((lat, lon))

# --- Folium Visualization ---
def create_folium_map(waypoints, corners):
    # Create map centered on first waypoint
    m = folium.Map(location=waypoints[0], zoom_start=17, tiles='OpenStreetMap')

    # Add field boundary
    folium.Polygon(
        locations=corners,
        color='#ff7800',
        weight=2,
        fill=True,
        fill_color='#ffff00',
        fill_opacity=0.2
    ).add_to(m)

    # Create path segments (split by None values)
    path_segments = []
    current_segment = []
    for wp in waypoints:
        if wp is None:
            if current_segment:
                path_segments.append(current_segment)
                current_segment = []
        else:
            current_segment.append(wp)
    if current_segment:
        path_segments.append(current_segment)

    # Add path lines and markers
    for i, segment in enumerate(path_segments):
        # Add polyline
        folium.PolyLine(
            locations=segment,
            color='#3388ff' if i % 2 == 0 else '#ff3333',  # Alternating colors
            weight=3,
            opacity=0.7
        ).add_to(m)

        # Add markers with altitude labels
        for j, (lat, lon) in enumerate(segment):
            folium.CircleMarker(
                location=(lat, lon),
                radius=3,
                color='#3388ff',
                fill=True,
                fill_color='white',
                popup=f"Waypoint {i+1}-{j+1}<br>Alt: {ALTITUDE_METERS}m"
            ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)
    return m

# Filter out None values for mapping
filtered_waypoints = [wp for wp in waypoints_gps if wp is not None]

# Create and display map
m = create_folium_map(filtered_waypoints, corners_gps)
m.save("drone_path.html")
print("Map saved to drone_path.html - open in browser to view!")