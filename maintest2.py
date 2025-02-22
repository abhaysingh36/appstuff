import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget, QHBoxLayout, 
    QComboBox, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
import cv2
import requests
import json

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
        
        self.selected_points = []
        self.video_thread = None
        self.video_url = "http://127.0.0.1:5000/video_feed"

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

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
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
            <script>
                let map;
                let markers = [];
                function initMap() {
                    const center = { lat: 13.0215, lng: 74.7927 };
                    map = new google.maps.Map(document.getElementById("map"), {
                        center: center,
                        zoom: 15
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
                    return JSON.stringify(markers.map(m => ({ lat: m.getPosition().lat(), lng: m.getPosition().lng() })));
                }
            </script>
        </head>
        <body><div id="map" style="width:100%; height:100%;"></div></body>
        </html>
        """
        self.map_view.setHtml(html_content)

    def compute_grid(self):
        self.map_view.page().runJavaScript("getSelectedPoints();", self.process_selected_points)

    def process_selected_points(self, points):
        points = json.loads(points)
        if len(points) == 4:
            grid = self.create_grid(points)
            print("Generated Grid:", grid)
        else:
            print("Please select exactly 4 points on the map.")
    def reset_map(self):
        print("Resetting map...")
        self.load_map()  # Reload the map to reset markers


    def create_grid(self, points):
        lat_vals = [p['lat'] for p in points]
        lon_vals = [p['lng'] for p in points]
        min_lat, max_lat = min(lat_vals), max(lat_vals)
        min_lon, max_lon = min(lon_vals), max(lon_vals)
        step_dist = 0.000009
        grid = []
        lat_steps = int((max_lat - min_lat) / step_dist)
        lon_steps = int((max_lon - min_lon) / step_dist)
        for i in range(lat_steps + 1):
            current_lat = min_lat + i * step_dist
            for j in range(lon_steps + 1):
                current_lon = min_lon + j * step_dist
                grid.append((current_lat, current_lon))
        return grid

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneApp()
    window.show()
    sys.exit(app.exec())
