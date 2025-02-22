import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, QComboBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import numpy as np

class DroneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Controller")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")
        
        self.selected_points = []  # Store selected points

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        self.home_tab = QWidget()
        self.tabs.addTab(self.home_tab, "Home")

        self.init_home_tab()
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
        
        self.go_button = QPushButton("Go")
        self.go_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        
        self.setgrid_button = QPushButton("Set Grid")
        self.setgrid_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.setgrid_button.clicked.connect(self.compute_grid)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #333333; color: #ffffff;")
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
                        if (markers.length < 4) {
                            let marker = new google.maps.Marker({
                                position: event.latLng,
                                map: map
                            });
                            markers.push(marker);
                        }
                    });
                }
                
                function getSelectedPoints() {
                    let points = markers.map(m => ({ lat: m.getPosition().lat(), lng: m.getPosition().lng() }));
                    return JSON.stringify(points);
                }
                
                function resetMarkers() {
                    markers.forEach(marker => marker.setMap(null));
                    markers = [];
                }
            </script>
        </head>
        <body>
            <div id="map" style="width:100%; height:100%;"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html_content)

    def reset_map(self):
        self.map_view.page().runJavaScript("resetMarkers();")

    def compute_grid(self):
        self.map_view.page().runJavaScript("getSelectedPoints();", self.process_selected_points)

    def process_selected_points(self, points):
        import json
        points = json.loads(points)
        if len(points) == 4:
            min_lat = min(p['lat'] for p in points)
            max_lat = max(p['lat'] for p in points)
            min_lon = min(p['lng'] for p in points)
            max_lon = max(p['lng'] for p in points)
            step_dist = 0.001
            grid = self.create_grid(min_lat, max_lat, min_lon, max_lon, step_dist)
            print("Generated Grid:")
            for lat, lon in grid:
                print(lat, lon)
        else:
            print("Please select exactly 4 points on the map.")

    def create_grid(self, min_lat, max_lat, min_lon, max_lon, step_dist):
        lat_steps = int((max_lat - min_lat) / step_dist)
        lon_steps = int((max_lon - min_lon) / step_dist)
        grid = []
        for i in range(lat_steps + 1):
            for j in range(lon_steps + 1):
                grid.append([min_lat + i * step_dist, min_lon + j * step_dist])
        return grid

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())
