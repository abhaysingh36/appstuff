import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, 
    QComboBox, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import numpy as np
from PyQt6.QtCore import QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import requests

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

        
        self.selected_points = []  # Store selected points


        self.video_thread = None
        self.video_url = "http://127.0.0.1:5000/video_feed"

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
                    for (let i = 0; i < markers.length; i++) {
                        markers[i].setMap(null);
                    }
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
            step_dist = 0.000009
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
        self.min_lat=min_lat
        self.max_lat=max_lat
        self.min_lon=min_lon
        self.max_lon=max_lon
        for i in range(lat_steps + 1):
        # Determine the current latitude for this row
            current_lat = min_lat + i * step_dist
        
        # For even rows, move left-to-right (min_lon to max_lon)
        if i % 2 == 0:
            for j in range(lon_steps + 1):
                current_lon = min_lon + j * step_dist
                grid.append([current_lat, current_lon])
        # For odd rows, move right-to-left (max_lon to min_lon)
        else:
            for j in range(lon_steps, -1, -1):
                current_lon = min_lon + j * step_dist
                grid.append([current_lat, current_lon])
    
        return grid

    def reset_map(self):
        self.map_view.page().runJavaScript("resetMarkers();")

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
        layout.addWidget(QLabel("Drone Settings Tab"))
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


    def init_drone_settings_tab(self):
        layout = QVBoxLayout()
        self.settings_label = QLabel("Drone settings will be displayed here.")
        self.settings_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        layout.addWidget(self.settings_label)
        self.drone_settings_tab.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())
