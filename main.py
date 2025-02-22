import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, 
    QComboBox, QLabel, QSpacerItem, QSizePolicy
)
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

        # Tabs
        self.home_tab = QWidget()
        self.live_feed_tab = QWidget()
        self.drone_settings_tab = QWidget()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.live_feed_tab, "Live Feed")
        self.tabs.addTab(self.drone_settings_tab, "Drone Settings")

        self.init_home_tab()
        # self.init_live_feed_tab()
        # self.init_drone_settings_tab()

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
        self.go_button.setStyleSheet("background-color: #1a9e13; color: #ffffff;")
        
        self.setgrid_button = QPushButton("Set Grid")
        self.setgrid_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.setgrid_button.clicked.connect(self.compute_grid)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #cc3333; color: #ffffff;")
        self.reset_button.clicked.connect(self.reset_map)
        
        top_button_layout.addWidget(self.mode_dropdown)
        top_button_layout.addWidget(self.go_button)
        top_button_layout.addWidget(self.setgrid_button)
        top_button_layout.addWidget(self.reset_button)
        
        self.map_view = QWebEngineView()
        self.load_map()
        
        # Bottom button layout
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addStretch()
        
        self.locate_button = QPushButton("Locate Me")
        self.locate_button.setStyleSheet("background-color: #1e90ff; color: #ffffff;")
        self.locate_button.clicked.connect(self.locate_me)
        
        bottom_button_layout.addWidget(self.locate_button)
        bottom_button_layout.addStretch()
        
        layout.addLayout(top_button_layout)
        layout.addWidget(self.map_view)
        layout.addLayout(bottom_button_layout)
        
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
                .locate-btn {
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    background-color: #1e90ff;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    cursor: pointer;
                    z-index: 1000;
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
                }

                function locateMe() {
                    const myLocation = { lat: 13.024632392685684, lng: 74.79277732009889 };
                    map.setCenter(myLocation);
                    map.setZoom(17);
                }
            </script>
        </head>
        <body>
            <div id="map" style="width:100%; height:100%;"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html_content)

    def locate_me(self):
        self.map_view.page().runJavaScript("locateMe();")



    def compute_grid(self):
        """Get selected points from the map and generate a grid."""
        self.map_view.page().runJavaScript("getSelectedPoints();", self.process_selected_points)

    def process_selected_points(self, points):
        """Process selected points to create a grid."""
        points = json.loads(points)
        if len(points) == 4:
            min_lat = min(p['lat'] for p in points)
            max_lat = max(p['lat'] for p in points)
            min_lon = min(p['lng'] for p in points)
            max_lon = max(p['lng'] for p in points)

            step_dist = 0.001  # Adjust grid density
            grid = self.create_grid(min_lat, max_lat, min_lon, max_lon, step_dist)
            print("Generated Grid Points:")
            for lat, lon in grid:
                print(lat, lon)
        else:
            print("Please select exactly 4 points on the map.")

    def create_grid(self, min_lat, max_lat, min_lon, max_lon, step_dist):
        """Generate a grid within the selected area."""
        lat_steps = int((max_lat - min_lat) / step_dist)
        lon_steps = int((max_lon - min_lon) / step_dist)

        grid = []
        for i in range(lat_steps + 1):
            for j in range(lon_steps + 1):
                grid.append([min_lat + i * step_dist, min_lon + j * step_dist])

        return grid

    def reset_map(self):
        self.map_view.page().runJavaScript("resetMarkers();")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())
