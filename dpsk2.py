import folium
import json
import numpy as np
from pyproj import Proj, Transformer
from shapely.geometry import Polygon, LineString
from flask import Flask, request, jsonify

app = Flask(__name__)
app.debug = True

# Create base map
m = folium.Map(location=[34.0522, -118.2437], zoom_start=17)

# Feature groups for layers
marker_group = folium.FeatureGroup(name="Markers")
path_group = folium.FeatureGroup(name="Flight Path")
m.add_child(marker_group)
m.add_child(path_group)

# JavaScript template with proper map reference
click_js = f"""
<script>
console.log('Script initialization...');
let markers = [];
let map = {m.get_name()};

function updateStatus() {{
    const status = document.getElementById('status');
    status.innerHTML = `Markers: ${{markers.length}}/4`;
    
    if(markers.length === 4) {{
        status.innerHTML += '<br><button onclick="generatePath()" style="margin-top:10px; padding:8px;">Generate Path</button>';
    }}
}}

function generatePath() {{
    console.log('Generating path...');
    const coords = markers.map(m => m.getLatLng());
    
    fetch('/process-points', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            points: coords.map(p => [p.lat, p.lng])
        }})
    }})
    .then(response => {{
        console.log('Response status:', response.status);
        if(response.ok) location.reload();
    }})
    .catch(error => console.error('Error:', error));
}}

map.on('click', function(e) {{
    console.log('Click event:', e.latlng);
    
    if(markers.length < 4) {{
        const marker = L.marker(e.latlng, {{
            draggable: true,
            autoPan: true
        }}).addTo(map);
        
        marker.on('dragend', function(e) {{
            console.log('Marker moved:', e.target.getLatLng());
        }});
        
        markers.push(marker);
        updateStatus();
    }}
}});

console.log('Click handler registered');
</script>

<div id="status" style="position: fixed; top: 10px; left: 10px; 
      background: white; padding: 10px; z-index: 1000; border: 1px solid #ccc;">
    <strong>Click 4 points</strong>
</div>
"""

m.get_root().html.add_child(folium.Element(click_js))

@app.route('/')
def home():
    """Main endpoint serving the map"""
    print("Serving map page")
    return m._repr_html_()

@app.route('/process-points', methods=['POST'])
def process_points():
    """Endpoint for processing coordinates"""
    print("\n=== Processing Request ===")
    try:
        data = request.json
        print("Received data:", data)
        
        if not data or 'points' not in data:
            return jsonify(error="Invalid data format"), 400
            
        points = np.array(data['points'])
        print("Raw points:", points)
        
        if len(points) != 4:
            return jsonify(error="Exactly 4 points required"), 400
        
        # Sort points clockwise
        centroid = np.mean(points, axis=0)
        angles = np.arctan2(points[:,1] - centroid[1], points[:,0] - centroid[0])
        sorted_indices = np.argsort(-angles)
        sorted_points = points[sorted_indices]
        print("Sorted points:", sorted_points)
        
        # Save coordinates
        with open('coordinates.json', 'w') as f:
            json.dump(sorted_points.tolist(), f)
            
        # UTM conversion
        utm_zone = int((sorted_points[0][1] + 180)) // 6 + 1
        utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
        transformer = Transformer.from_proj(Proj('epsg:4326'), utm_proj, always_xy=True)
        utm_corners = [transformer.transform(lon, lat) for lat, lon in sorted_points]
        print("UTM coordinates:", utm_corners)
        
        # Generate path
        poly = Polygon(utm_corners)
        x_min, y_min = np.min(utm_corners, axis=0)
        x_max, y_max = np.max(utm_corners, axis=0)
        
        waypoints = []
        use_y_axis = (y_max - y_min) > (x_max - x_min)
        spacing = 5  # meters
        
        lines = np.arange(y_min, y_max, spacing) if use_y_axis else np.arange(x_min, x_max, spacing)
        print(f"Generating {len(lines)} lines")
        
        for i, pos in enumerate(lines):
            if use_y_axis:
                line = LineString([(x_min, pos), (x_max, pos)])
            else:
                line = LineString([(pos, y_min), (pos, y_max)])
            
            intersection = line.intersection(poly)
            if not intersection.is_empty:
                coords = list(intersection.coords)
                waypoints.extend(coords[::-1] if i%2 else coords)
        
        # Convert back to GPS
        transformer_back = Transformer.from_proj(utm_proj, Proj('epsg:4326'), always_xy=True)
        gps_waypoints = [transformer_back.transform(x, y) for x, y in waypoints]
        print("Converted waypoints:", len(gps_waypoints))
        
        # Save and add to map
        with open('waypoints.json', 'w') as f:
            json.dump(gps_waypoints, f)
            
        path_group.add_child(folium.PolyLine(
            locations=[(lon, lat) for lat, lon in gps_waypoints],
            color='red',
            weight=3
        ))
        
        return jsonify(success=True)
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(port=5000)