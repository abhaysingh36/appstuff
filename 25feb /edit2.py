import sys
import math
import json
import folium
import numpy as np
import cv2
import requests

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, 
    QComboBox, QLabel,QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from pyproj import Proj, Transformer
from shapely.geometry import Polygon, LineString

class VideoThread(QThread):
    update_frame = pyqtSignal(QImage)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.running = True

    def run(self):
        cap = requests.get(self.url, stream=True)
        byte_data = b""

        for chunk in cap.iter_content(chunk_size=1024):
            if not self.running:
                break

            byte_data += chunk
            a = byte_data.find(b'\xff\xd8')  # Start of JPEG
            b = byte_data.find(b'\xff\xd9')  # End of JPEG
            if a != -1 and b != -1:
                jpg = byte_data[a:b+2]
                byte_data = byte_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    self.update_frame.emit(img)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class DroneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Controller")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        # Mode configuration
        self.mode_limits = {
            "Mapping": 4,
            "Delivery": 1,
            "Agriculture": 4,
            "Surveillance": 7
        }

        # Variables for different modes
        self.corners_gps = None
        self.dropoff_point = None
        self.surveillance_points = None
        self.grid_spacing_meters = 10
        self.altitude_meters = 20
        self.waypoints_gps = None
        self.corners_utm = None

        self.video_thread = None
        self.video_url = "http://127.0.0.1:5000/video_feed"

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        # Initialize tabs
        self.home_tab = QWidget()
        self.live_feed_tab = QWidget()
        self.drone_settings_tab = QWidget()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.live_feed_tab, "Live Feed")
        self.tabs.addTab(self.drone_settings_tab, "Drone Settings")

        self.init_home_tab()
        self.init_live_feed_tab()
        self.init_drone_settings_tab()

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_home_tab(self):
        layout = QVBoxLayout()
        
        # Top button layout
        top_button_layout = QHBoxLayout()
        top_button_layout.addStretch()
        
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Mapping", "Delivery", "Agriculture", "Surveillance"])
        self.mode_dropdown.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.mode_dropdown.currentIndexChanged.connect(self.update_map_mode)
        
        self.go_button = QPushButton("Go")
        self.go_button.setStyleSheet("background-color: #1a9e13; color: #ffffff;")
        
        self.setgrid_button = QPushButton("Set Path")
        self.setgrid_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.setgrid_button.clicked.connect(self.compute_path)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #cc3333; color: #ffffff;")
        self.reset_button.clicked.connect(self.reset_map)
        
        top_button_layout.addWidget(self.mode_dropdown)
        top_button_layout.addWidget(self.go_button)
        top_button_layout.addWidget(self.setgrid_button)
        top_button_layout.addWidget(self.reset_button)
        
        self.map_view = QWebEngineView()
        self.load_map()
        
        layout.addLayout(top_button_layout)
        layout.addWidget(self.map_view)
        self.home_tab.setLayout(layout)

    def load_map(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                html, body, #map {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    background-color: #121212;
                }
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCLGirrq1bnCqF6HBOoEJXbDS0_tX_Yjls&callback=initMap" async defer></script>
            <script>
                let map;
                let markers = [];
                let maxMarkers = 4;

                function initMap() {
                    const center = { lat: 13.0215, lng: 74.7927 };
                    map = new google.maps.Map(document.getElementById("map"), {
                        center: center,
                        zoom: 15,
                        styles: [
                            { "elementType": "geometry", "stylers": [{ "color": "#212121" }] },
                            { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#373737" }] },
                            { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#0e0e0e" }] }
                        ]
                    });

                    map.addListener("click", function(event) {
                        if (markers.length < maxMarkers) {
                            let marker = new google.maps.Marker({
                                position: event.latLng,
                                map: map,
                                icon: {
                                    path: google.maps.SymbolPath.CIRCLE,
                                    scale: 5,
                                    fillColor: "#FF0000",
                                    fillOpacity: 1,
                                    strokeWeight: 1
                                }
                            });
                            markers.push(marker);
                        }
                    });
                }

                function getSelectedPoints() {
                    return JSON.stringify(markers.map(m => ({ 
                        lat: m.getPosition().lat(), 
                        lng: m.getPosition().lng() 
                    })));
                }

                function resetMarkers() {
                    markers.forEach(m => m.setMap(null));
                    markers = [];
                }

                function updateMarkerLimit(limit) {
                    maxMarkers = limit;
                    resetMarkers();
                }
            </script>
        </head>
        <body>
            <div id="map" style="width:100%; height:100%;"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html_content)
    def update_map_mode(self):
        selected_mode = self.mode_dropdown.currentText()
        limit = self.mode_limits[selected_mode]
        self.map_view.page().runJavaScript(f"updateMarkerLimit({limit})")

    def order_corners(self, corners):
        centroid_lat = sum(pt[0] for pt in corners) / len(corners)
        centroid_lon = sum(pt[1] for pt in corners) / len(corners)
        
        def angle_from_centroid(pt):
            return math.atan2(pt[0] - centroid_lat, pt[1] - centroid_lon)
        
        sorted_corners = sorted(corners, key=angle_from_centroid, reverse=True)
        top_left = max(sorted_corners, key=lambda pt: (pt[0], -pt[1]))
        while sorted_corners[0] != top_left:
            sorted_corners.append(sorted_corners.pop(0))
        return sorted_corners
    

    def get_utm_zone(self, latitude, longitude):
        return int((longitude + 180) // 6 + 1)

    def convert_to_utm(self):
        """
        Convert the ordered GPS corner points to UTM coordinates.
        """
        lat, lon = self.corners_gps[0]
        utm_zone = self.get_utm_zone(lat, lon)
        self.utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
        self.transformer_gps_to_utm = Transformer.from_proj(Proj('epsg:4326'), self.utm_proj, always_xy=True)
        self.corners_utm = [self.transformer_gps_to_utm.transform(lon, lat) for lat, lon in self.corners_gps]

    def generate_waypoints(self):
        """
        Generate waypoints on a boustrophedon (zigzag) grid within the UTM polygon,
        then convert them back to GPS coordinates.
        """
        if self.corners_utm is None:
            self.convert_to_utm()

        field_polygon = Polygon(self.corners_utm)
        corners_array = np.array(self.corners_utm)
        x_min, y_min = np.min(corners_array, axis=0)
        x_max, y_max = np.max(corners_array, axis=0)
        use_y_axis = (y_max - y_min) > (x_max - x_min)
        # Create grid lines along the longer dimension.
        lines = np.arange(y_min, y_max, self.grid_spacing_meters) if use_y_axis else np.arange(x_min, x_max, self.grid_spacing_meters)
        waypoints_utm = []
        for i, line_pos in enumerate(lines):
            if use_y_axis:
                line = LineString([(x_min, line_pos), (x_max, line_pos)])
            else:
                line = LineString([(line_pos, y_min), (line_pos, y_max)])
            intersection = line.intersection(field_polygon)
            if not intersection.is_empty:
                if intersection.geom_type == 'MultiLineString':
                    coords = sum([list(g.coords) for g in intersection.geoms], [])
                else:
                    coords = list(intersection.coords)
                # Alternate the direction for a zigzag path.
                if i % 2 == 0:
                    waypoints_utm.extend(coords + [(None, None)])
                else:
                    waypoints_utm.extend(coords[::-1] + [(None, None)])
        transformer_utm_to_gps = Transformer.from_proj(self.utm_proj, Proj('epsg:4326'), always_xy=True)
        self.waypoints_gps = []
        for x, y in waypoints_utm:
            if x is None or y is None:
                self.waypoints_gps.append(None)
            else:
                lon, lat = transformer_utm_to_gps.transform(x, y)
                self.waypoints_gps.append((lat, lon))

    def create_map(self, output_file="drone_path.html"):
        """
        Create a Folium map with the field boundary and generated waypoints.
        The map is saved to output_file.
        """
        if self.waypoints_gps is None:
            self.generate_waypoints()
        filtered_waypoints = [wp for wp in self.waypoints_gps if wp is not None]
        if not filtered_waypoints:
            print("No waypoints generated.")
            return
        m = folium.Map(location=filtered_waypoints[0], zoom_start=17, tiles='OpenStreetMap')
        folium.Polygon(
            locations=self.corners_gps,
            color='#ff7800',
            weight=2,
            fill=True,
            fill_color='#ffff00',
            fill_opacity=0.2
        ).add_to(m)
        path_segments = []
        current_segment = []
        for wp in self.waypoints_gps:
            if wp is None:
                if current_segment:
                    path_segments.append(current_segment)
                    current_segment = []
            else:
                current_segment.append(wp)
        if current_segment:
            path_segments.append(current_segment)
        for i, segment in enumerate(path_segments):
            folium.PolyLine(
                locations=segment,
                color='#3388ff' if i % 2 == 0 else '#ff3333',
                weight=3,
                opacity=0.7
            ).add_to(m)
            for j, (lat, lon) in enumerate(segment):
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=3,
                    color='#3388ff',
                    fill=True,
                    fill_color='white',
                    popup=f"Waypoint {i+1}-{j+1}<br>Alt: {self.altitude_meters}m"
                ).add_to(m)
        folium.LayerControl().add_to(m)
        m.save(output_file)
        print("Map saved to", output_file)
        # Reload the updated map in the QWebEngineView.
        with open(output_file, "r", encoding="utf-8") as f:
            html = f.read()
        self.map_view.setHtml(html)

    def reset_map(self):
        """
        Reset the map by clearing the markers on the JavaScript side,
        resetting the stored grid state, and reloading the original map.
        """
        # Clear the markers on the JavaScript side.
        self.map_view.page().runJavaScript("resetMarkers();")
        # Reset internal state.
        self.corners_gps = None
        self.corners_utm = None
        self.waypoints_gps = None
        # Optionally, reload the original map view.
        self.load_map()

    def compute_path(self):
        """
        Retrieve selected points from the JavaScript map, process them,
        generate a grid, and update the map.
        """
        self.map_view.page().runJavaScript("getSelectedPoints();", self.process_points)

    def process_points(self, result):
        try:
            print(f"Raw result from JavaScript: {result}")  # Debugging output
            points = json.loads(result)  # Check if this fails
            print(f"Parsed points: {points}")  # Check if the data is structured correctly
        
            if not isinstance(points, list):
                print("Error: Points is not a list!")
                return

            selected_mode = self.mode_dropdown.currentText()
            print(f"Selected Mode: {selected_mode}")

            required = self.mode_limits.get(selected_mode, None)
            if required is None:
                print("Error: Invalid mode selection")
                return

            if len(points) != required:
                QMessageBox.warning(self, "Invalid Points",
                                f"{selected_mode} requires exactly {required} points!",
                                QMessageBox.StandardButton.Ok)
                return

            if selected_mode in ["Agriculture", "Mapping"]:
                self.corners_gps = [(p['lat'], p['lng']) for p in points]
                self.corners_gps = self.order_corners(self.corners_gps)
                print(f"Ordered GPS Corners: {self.corners_gps}")
                self.generate_waypoints()
                self.create_map()
            elif selected_mode == "Delivery":
                self.dropoff_point = (points[0]['lat'], points[0]['lng'])
                print(f"Dropoff Point: {self.dropoff_point}")
                self.create_delivery_map()
            elif selected_mode == "Surveillance":
                self.surveillance_points = [(p['lat'], p['lng']) for p in points]
                print(f"Surveillance Points: {self.surveillance_points}")
                self.create_surveillance_map()
            else:
                print("Error: Unknown mode selected")

        except Exception as e:
            print("Error in process_points:", e)
            QMessageBox.critical(self, "Error", f"Failed to process points: {str(e)}",
                             QMessageBox.StandardButton.Ok)
    def create_delivery_map(self):
        m = folium.Map(location=self.dropoff_point, zoom_start=17)
        folium.Marker(
            location=self.dropoff_point,
            icon=folium.Icon(color='green', icon='box-open')
        ).add_to(m)
        m.save("delivery.html")
        self.map_view.setHtml(open("delivery.html").read())

    def create_surveillance_map(self):
        m = folium.Map(location=self.surveillance_points[0], zoom_start=17)
        for pt in self.surveillance_points:
            folium.Marker(
                location=pt,
                icon=folium.Icon(color='blue', icon='eye')
            ).add_to(m)
        folium.PolyLine(self.surveillance_points, color='purple').add_to(m)
        m.save("surveillance.html")
        self.map_view.setHtml(open("surveillance.html").read())

    def init_live_feed_tab(self):
        layout = QVBoxLayout()

        self.live_feed_label = QLabel("Live feed will be displayed here.")
        self.live_feed_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        self.live_feed_label.setFixedSize(640, 480)

        self.start_feed_button = QPushButton("Start Feed")
        self.start_feed_button.setStyleSheet("background-color: #1a9e13; color: #ffffff;")
        self.start_feed_button.clicked.connect(self.start_video_feed)

        self.stop_feed_button = QPushButton("Stop Feed")
        self.stop_feed_button.setStyleSheet("background-color: #cc3333; color: #ffffff;")
        self.stop_feed_button.clicked.connect(self.stop_video_feed)

        layout.addWidget(self.live_feed_label)
        layout.addWidget(self.start_feed_button)
        layout.addWidget(self.stop_feed_button)
        self.live_feed_tab.setLayout(layout)

    def init_drone_settings_tab(self):
        layout = QVBoxLayout()
        self.settings_label = QLabel("Drone settings will be displayed here.")
        self.settings_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        layout.addWidget(self.settings_label)
        self.drone_settings_tab.setLayout(layout)

    def start_video_feed(self):
        if self.video_thread is None or not self.video_thread.isRunning():
            self.video_thread = VideoThread(self.video_url)
            self.video_thread.update_frame.connect(self.update_image)
            self.video_thread.start()

    def stop_video_feed(self):
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread = None
            self.live_feed_label.clear()
            self.live_feed_label.setText("Live feed stopped.")

    def update_image(self, img):
        self.live_feed_label.setPixmap(QPixmap.fromImage(img))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())
