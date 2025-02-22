import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, QComboBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class DroneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Controller")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        self.home_tab = QWidget()
        self.live_feed_tab = QWidget()
        self.drone_settings_tab = QWidget()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.live_feed_tab, "Live Feed")
        self.tabs.addTab(self.drone_settings_tab, "Drone Setting")

        self.init_home_tab()

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_home_tab(self):
        layout = QVBoxLayout()
        self.map_view = QWebEngineView()
        self.load_map()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.go_button = QPushButton("Go")
        self.go_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Mapping", "Delivery", "Agriculture", "Surveillance"])
        self.mode_dropdown.setStyleSheet("background-color: #333333; color: #ffffff;")
        
        button_layout.addWidget(self.go_button)
        button_layout.addWidget(self.mode_dropdown)

        layout.addLayout(button_layout)
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
                function initMap() {
                    const location = { lat: 13.0215, lng: 74.7927 };
                    const map = new google.maps.Map(document.getElementById("map"), {
                        center: location,
                        zoom: 7,
                        styles: [
                            { "elementType": "geometry", "stylers": [{ "color": "#212121" }] },
                            { "elementType": "labels.text.stroke", "stylers": [{ "color": "#212121" }] },
                            { "elementType": "labels.text.fill", "stylers": [{ "color": "#757575" }] },
                            { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#373737" }] },
                            { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#0e0e0e" }] }
                        ]
                    });
                    new google.maps.Marker({
                        position: location,
                        map: map
                    });
                }
            </script>
        </head>
        <body>
            <div id="map" style="width:100%; height:100%;"></div>
        </body>
        </html>
        """
        self.map_view.setHtml(html_content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())





# import sys
# import numpy as np
# from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, QComboBox
# from PyQt6.QtWebEngineWidgets import QWebEngineView
# from PyQt6.QtCore import QUrl

# class DroneApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Drone Controller")
#         self.setGeometry(100, 100, 800, 600)
#         self.setStyleSheet("background-color: #121212; color: #ffffff;")
        
#         self.selected_points = []
        
#         layout = QVBoxLayout()
#         self.tabs = QTabWidget()
#         self.tabs.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

#         self.home_tab = QWidget()
#         self.live_feed_tab = QWidget()
#         self.drone_settings_tab = QWidget()

#         self.tabs.addTab(self.home_tab, "Home")
#         self.tabs.addTab(self.live_feed_tab, "Live Feed")
#         self.tabs.addTab(self.drone_settings_tab, "Drone Setting")

#         self.init_home_tab()

#         layout.addWidget(self.tabs)
#         self.setLayout(layout)

#     def init_home_tab(self):
#         layout = QVBoxLayout()
#         self.map_view = QWebEngineView()
#         self.load_map()

#         button_layout = QHBoxLayout()
#         button_layout.addStretch()
#         self.go_button = QPushButton("Go")
#         self.go_button.setStyleSheet("background-color: #333333; color: #ffffff;")
        
#         self.mode_dropdown = QComboBox()
#         self.mode_dropdown.addItems(["Mapping", "Delivery", "Agriculture", "Surveillance"])
#         self.mode_dropdown.setStyleSheet("background-color: #333333; color: #ffffff;")
#         self.mode_dropdown.currentTextChanged.connect(self.on_mode_change)
        
#         self.set_button = QPushButton("Set Grid")
#         self.set_button.setStyleSheet("background-color: #333333; color: #ffffff;")
#         self.set_button.setEnabled(False)
#         self.set_button.clicked.connect(self.create_grid)
        
#         button_layout.addWidget(self.go_button)
#         button_layout.addWidget(self.mode_dropdown)
#         button_layout.addWidget(self.set_button)

#         layout.addLayout(button_layout)
#         layout.addWidget(self.map_view)

#         self.home_tab.setLayout(layout)

#     def load_map(self):
#         html_content = """
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 html, body, #map {
#                     height: 100%;
#                     margin: 0;
#                     padding: 0;
#                     background-color: #121212;
#                 }
#             </style>
#             <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCLGirrq1bnCqF6HBOoEJXbDS0_tX_Yjls&callback=initMap" async defer></script>
#             <script>
#                 let map;
#                 let selectedPoints = [];
#                 function initMap() {
#                     const location = { lat: 13.0215, lng: 74.7927 };
#                     map = new google.maps.Map(document.getElementById("map"), {
#                         center: location,
#                         zoom: 7,
#                         styles: [
#                             { "elementType": "geometry", "stylers": [{ "color": "#212121" }] },
#                             { "elementType": "labels.text.stroke", "stylers": [{ "color": "#212121" }] },
#                             { "elementType": "labels.text.fill", "stylers": [{ "color": "#757575" }] },
#                             { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#373737" }] },
#                             { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#0e0e0e" }] }
#                         ]
#                     });

#                     map.addListener("click", (event) => {
#                         if (selectedPoints.length < 4) {
#                             const lat = event.latLng.lat();
#                             const lon = event.latLng.lng();
#                             selectedPoints.push([lat, lon]);
#                             new google.maps.Marker({
#                                 position: { lat: lat, lng: lon },
#                                 map: map
#                             });
#                             if (selectedPoints.length === 4) {
#                                 window.pyBridge.enableSetButton();
#                             }
#                         }
#                     });
#                 }

#                 function plotGrid(grid) {
#                     grid.forEach(([lat, lon]) => {
#                         new google.maps.Marker({
#                             position: { lat: lat, lng: lon },
#                             map: map,
#                             icon: { url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" }
#                         });
#                     });
#                 }
#             </script>
#         </head>
#         <body>
#             <div id="map" style="width:100%; height:100%;"></div>
#         </body>
#         </html>
#         """
#         self.map_view.setHtml(html_content)

#     def on_mode_change(self, mode):
#         if mode == "Agriculture":
#             self.selected_points = []
#             self.set_button.setEnabled(False)

#     def create_grid(self):
#         if len(self.selected_points) < 4:
#             return
#         min_lat = min(p[0] for p in self.selected_points)
#         max_lat = max(p[0] for p in self.selected_points)
#         min_lon = min(p[1] for p in self.selected_points)
#         max_lon = max(p[1] for p in self.selected_points)
#         step_dist = 0.0001
#         grid = self.compute_grid(min_lat, max_lat, min_lon, max_lon, step_dist)
#         self.plot_grid(grid)

#     def compute_grid(self, min_lat, max_lat, min_lon, max_lon, step_dist):
#         lat_steps = int((max_lat - min_lat) / step_dist)
#         lon_steps = int((max_lon - min_lon) / step_dist)
#         grid = [[min_lat + i * step_dist, min_lon + j * step_dist] for i in range(lat_steps + 1) for j in range(lon_steps + 1)]
#         return grid

#     def plot_grid(self, grid):
#         js_code = f'plotGrid({grid});'
#         self.map_view.page().runJavaScript(js_code)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DroneApp()
#     window.show()
#     sys.exit(app.exec())
