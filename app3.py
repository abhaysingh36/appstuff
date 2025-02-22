import sys
import torch
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QHBoxLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import (
    pyqtSignal, pyqtSlot, QObject, QThread, Qt
)
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from PyQt6.QtCore import QUrl
from pymavlink import mavutil
import folium
from PyQt6.QtCore import QTimer
import socket
import multiprocessing


def client():
    # Function to handle communication with the server
    def start_client(host='192.168.199.71', port=5555):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        while True:
            # Get input from the user (the message to send to the server)
            message = input("Client: ")

            if message.lower() == 'exit':
                print("Closing connection...")
                client.close()
                break

            # Send the message to the server
            client.send(message.encode('utf-8'))

            # Receive the server's response
            response = client.recv(1024).decode('utf-8')
            print(f"Server: {response}")

    start_client()


def app():
    class MarkerHandler(QObject):
        @pyqtSlot(float, float)
        def addMarker(self, lat: float, lon: float):
            print(f"Marker added at latitude: {lat}, longitude: {lon}")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=device)
    if device == 'cuda':
        model.half()

    class GPSCalibrationTab(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()

            self.map_view = QWebEngineView()
            self.web_channel = QWebChannel()
            self.marker_handler = MarkerHandler()
            self.web_channel.registerObject("markerHandler", self.marker_handler)
            self.map_view.page().setWebChannel(self.web_channel)

            self.map_view.setHtml(self.generate_google_map_html())
            layout.addWidget(self.map_view)

            coord_layout = QHBoxLayout()
            coord_layout.addWidget(QLabel("Enter GPS Coordinates:"))
            self.coordinate_input = QLineEdit()
            coord_layout.addWidget(self.coordinate_input)

            self.set_marker_button = QPushButton("Set Marker")
            self.set_marker_button.clicked.connect(self.set_marker)
            coord_layout.addWidget(self.set_marker_button)

            layout.addLayout(coord_layout)

            self.status_label = QLabel("Status: Ready")
            layout.addWidget(self.status_label)

            self.setLayout(layout)

        def generate_google_map_html(self):
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    html, body, #map {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
                </style>
                <script 
                    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCLGirrq1bnCqF6HBOoEJXbDS0_tX_Yjls&callback=initMap" 
                    async defer>
                </script>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script>
                    let map;
                    let marker;

                    function initMap() {{
                        const defaultLocation = {{ lat: 51.505, lng: -0.09 }};
                        map = new google.maps.Map(document.getElementById("map"), {{
                            center: defaultLocation,
                            zoom: 13,
                        }});

                        map.addListener("click", (event) => {{
                            if (window.markerHandler) {{
                                window.markerHandler.addMarker(event.latLng.lat(), event.latLng.lng());
                            }}
                        }});
                    }}

                    function setMarker(lat, lon) {{
                        console.log('Setting marker at:', lat, lon);

                        if (marker) {{
                            marker.setMap(null);
                        }}

                        const location = {{ lat: lat, lng: lon }};
                        marker = new google.maps.Marker({{
                            position: location,
                            map: map,
                            icon: {{
                                url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                            }}
                        }});

                        map.panTo(location);
                        map.setZoom(15);
                    }}

                    window.onload = function() {{
                        new QWebChannel(qt.webChannelTransport, function(channel) {{
                            window.markerHandler = channel.objects.markerHandler;
                        }});
                    }};
                </script>
            </head>
            <body>
                <div id="map"></div>
            </body>
            </html>
            """

        def set_marker(self):
            coordinates = self.coordinate_input.text()
            try:
                lat, lon = map(float, coordinates.split(","))
                self.map_view.page().runJavaScript(f"setMarker({lat}, {lon});")
                self.status_label.setText(f"Status: Marker set at {lat}, {lon}")
            except ValueError:
                self.status_label.setText("Status: Invalid coordinates! Use 'latitude,longitude' format.")

    class MapMonitoringTab(QWidget):
        def __init__(self, drone):
            super().__init__()
            self.drone = drone

            # Layout
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            # WebEngineView to display the map
            self.map_view = QWebEngineView()
            self.layout.addWidget(self.map_view)

            # Initialize map
            self.init_map()

            # Timer for dynamic updates
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_map)
            self.update_timer.start(1000)  # Update every 1 second

        def init_map(self):
            """Initialize the map with a default location."""
            # Default location (latitude, longitude)
            self.current_location = (0.0, 0.0)
            self.map = folium.Map(location=self.current_location, zoom_start=15)

            # Save the map to an HTML file
            self.map_file = "map.html"
            self.save_map()

            # Load the map into the view
            self.map_view.setUrl(QUrl.fromLocalFile(self.map_file))

        def save_map(self):
            """Save the map to an HTML file."""
            folium.Marker(self.current_location, popup="Drone Location").add_to(self.map)
            self.map.save(self.map_file)

        def update_map(self):
            """Update the map with the drone's current GPS position."""
            try:
                if self.drone:
                    # Fetch current GPS coordinates from the drone
                    lat, lon = self.drone.get_gps_coordinates()
                    self.current_location = (lat, lon)

                    # Update the map
                    self.map = folium.Map(location=self.current_location, zoom_start=15)
                    folium.Marker(self.current_location, popup="Drone Location").add_to(self.map)

                    # Save and reload the map
                    self.save_map()
                    self.map_view.setUrl(QUrl.fromLocalFile(self.map_file))
            except Exception as e:
                print(f"Error updating map: {e}")

    class CameraFeedTab(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()

            layout.addWidget(QLabel("Flask Camera Feed with YOLOv5", alignment=Qt.AlignmentFlag.AlignCenter))

            # QLabel to show video frames
            self.video_label = QLabel(self)
            layout.addWidget(self.video_label)

            # Create buttons to start and stop the feed
            self.start_feed_button = QPushButton("Start Feed")
            self.stop_feed_button = QPushButton("Stop Feed")
            self.stop_feed_button.setEnabled(False)

            button_layout = QHBoxLayout()
            button_layout.addWidget(self.start_feed_button)
            button_layout.addWidget(self.stop_feed_button)

            layout.addLayout(button_layout)

            self.setLayout(layout)

            # Initialize webcam feed thread
            self.video_thread = None

            # Connect buttons to methods
            self.start_feed_button.clicked.connect(self.start_feed)
            self.stop_feed_button.clicked.connect(self.stop_feed)

        def start_feed(self):
            """Start the video feed with object detection"""
            self.video_thread = ObjectDetection(self.video_label)
            self.video_thread.start()

            self.start_feed_button.setEnabled(False)
            self.stop_feed_button.setEnabled(True)

        def stop_feed(self):
            """Stop the video feed"""
            if self.video_thread is not None:
                self.video_thread.stop()
                self.video_thread.wait()  # Wait for thread to finish

            self.start_feed_button.setEnabled(True)
            self.stop_feed_button.setEnabled(False)


    class ObjectDetection(QThread):
        def __init__(self, label):
            super().__init__()
            self.label = label
            self.running = True
            self.cap = cv2.VideoCapture("http://127.0.0.1:5000/video_feed")  # Flask feed URL

            # Check if the webcam feed is opened correctly
            if not self.cap.isOpened():
                print("Error: Could not open webcam feed.")
                self.running = False

            self.frame_count = 0  # To control frame processing rate

        def run(self):
            while self.running:
                ret, frame = self.cap.read()

                # If the frame is not grabbed, break the loop
                if not ret:
                    print("Error: Failed to capture image.")
                    break

                self.frame_count += 1

                # Process every 5th frame for object detection
                if self.frame_count % 5 == 0:
                    results = model(frame)

                    # Draw the detected objects on the frame
                    frame = results.render()[0]

                # Convert frame to QImage and display it
                self.display_frame(frame)

        def stop(self):
            self.running = False

        def display_frame(self, frame):
            """Display the frame on the QLabel"""
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            bytes_per_line = channel * width
            q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    class DroneControl:
        def __init__(self):
            self.connection = None
            self.connect()

        def connect(self):
            # Connect to the drone using pymavlink
            try:
                self.connection = mavutil.mavlink_connection('/dev/ttyACM0')
                print("Connected to drone.")
            except Exception as e:
                print(f"Error connecting to drone: {e}")

        def get_gps_coordinates(self):
            if self.connection:
                try:
                    msg = self.connection.recv_match(type='GPS_RAW_INT', blocking=True)
                    lat = msg.lat / 1e7  # Convert to degrees
                    lon = msg.lon / 1e7  # Convert to degrees
                    return lat, lon
                except Exception as e:
                    print(f"Error retrieving GPS data: {e}")
                    return 0.0, 0.0
            return 0.0, 0.0

    class DroneControlWidget(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Drone Control")
            self.setGeometry(100, 100, 800, 600)

            self.tab_widget = QTabWidget()

            self.drone = DroneControl()

            self.gps_tab = GPSCalibrationTab()
            self.map_tab = MapMonitoringTab(self.drone)
            self.camera_tab = CameraFeedTab()

            self.tab_widget.addTab(self.gps_tab, "GPS Calibration")
            self.tab_widget.addTab(self.map_tab, "Map Monitoring")
            self.tab_widget.addTab(self.camera_tab, "Camera Feed")

            self.setCentralWidget(self.tab_widget)

    app = QApplication(sys.argv)
    window = DroneControlWidget()
    window.show()

    sys.exit(app.exec())
