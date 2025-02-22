import sys
import torch
from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
        QLabel, QPushButton, QLineEdit, QHBoxLayout , QComboBox , QGroupBox , QSpacerItem , QSizePolicy
    )
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import (pyqtSignal, pyqtSlot, QObject, QThread, Qt)
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from PyQt6.QtCore import QUrl
from pymavlink import mavutil
import folium
from PyQt6.QtCore import QTimer
import socket
import multiprocessing
import time 
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=device)
# if device == 'cuda':
#     model.half() 

client = None
# Function to handle communication with the server
class Client:
    def __init__(self):
           
        self.is_connected = False
        self.host='192.168.199.71' 
        self.port=5555
        

    def send(self,data):
        self.client=socket.socket(socket.AF_INET, socket.SOCK_STREAM);self.client.connect((self.host,self.port)) if self.is_connected else print()
        self.client.send(data)

    def connect(self):
        """Try to connect to the server and return a success flag."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print("Connected to server")
            return True  # Return True if connection is successful
        except socket.error as e:
            print(f"Connection failed: {e}. Retrying...")
            time.sleep(5)
            return False  # Return False if connection fails


    def disconnect(self):
        if self.is_connected and self.socket:
            try:
                self.socket.close()  # Close the socket
                self.is_connected = False
                print("Disconnected from server")
            except socket.error as e:
                print(f"Error during disconnection: {e}")
        else:
            print("No active connection to disconnect.")

    

 

def app():


    class MarkerHandler(QObject):
        def __init__(self, web_view):
            super().__init__()
            self.web_view = web_view
            self.markers = []  # Store all markers

        @pyqtSlot(float, float)
        def addMarker(self, lat: float, lon: float):
            """Send the coordinates to JavaScript to update the marker position."""
            print(f"Marker added at latitude: {lat}, longitude: {lon}")
            self.update_marker_on_map(lat, lon)

        def update_marker_on_map(self, lat, lon):
            """Use JavaScript to update the marker on the map."""
            # Execute the JavaScript function to move the marker
            js_code = f"setMarker({lat}, {lon});"
            # Send this code to the web page running in QWebEngineView
            self.web_view.page().runJavaScript(js_code)

            # Store the marker information (lat, lon) in the markers list
            self.markers.append((lat, lon))  # Add the new marker
    class GPSCalibrationTab(QWidget):
        def __init__(self):
            super().__init__()
            

            # Layout
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            # WebEngineView to display the map
            self.map_view = QWebEngineView()
            self.layout.addWidget(self.map_view)

            # WebChannel to communicate with JavaScript
            self.web_channel = QWebChannel()

            # Pass map_view to MarkerHandler
            self.marker_handler = MarkerHandler(self.map_view)
            self.web_channel.registerObject("markerHandler", self.marker_handler)
            self.map_view.page().setWebChannel(self.web_channel)

            # Initialize map with a placeholder HTML file
            self.map_view.setHtml(self.generate_google_map_html())

            # Timer for dynamic updates (if needed)
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_marker)
            self.update_timer.start(1000)  # Update every 1 second
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
                    let markers = [];  // Array to store multiple markers

                    function initMap() {{
                        const defaultLocation = {{ lat: 13.0215, lng: 74.7927 }};  // JavaScript syntax inside the string
                        map = new google.maps.Map(document.getElementById("map"), {{
                            center: defaultLocation,
                            zoom: 7,  // Start with zoom level 15 for initial zoom effect
                            disableDefaultUI: true,  // Enable user interaction for zooming out/in
                            zoomControl: true,  // Enable zoom control
                            scrollwheel: true,  // Enable zooming with mouse wheel
                            streetViewControl: true, // Optional: Enable street view control if desired
                        }});

                        // Listen for map clicks and send coordinates to Python
                        map.addListener("click", (event) => {{
                            const lat = event.latLng.lat();
                            const lon = event.latLng.lng();
                            if (window.markerHandler) {{
                                window.markerHandler.addMarker(lat, lon);  // Send the click coordinates to Python
                            }}
                            setMarker(lat, lon);  // Set a red marker at the clicked location
                        }});

                        // Optional: Add a marker at the default location on map load
                        setMarker(defaultLocation.lat, defaultLocation.lng);
                    }}

                    function setMarker(lat, lon) {{
                        // Create a new marker and add it to the array
                        const location = {{ lat: lat, lng: lon }};
                        const newMarker = new google.maps.Marker({{
                            position: location,
                            map: map,
                            icon: {{
                                url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                            }}
                        }});

                        markers.push(newMarker);  // Store the new marker in the markers array

                        // Optionally, adjust map view to show all markers
                        const bounds = new google.maps.LatLngBounds();
                        markers.forEach(marker => bounds.extend(marker.getPosition()));
                        map.fitBounds(bounds);  // Zoom out to fit all markers on the map
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


        def update_marker(self):
            """Fetch the drone's current GPS coordinates and send to JavaScript to update the map marker."""
            # Fetch coordinates (mocked here for testing purposes)
            lat, lon = 13.0220, 74.7928  # Example coordinates (you can replace these with real data)
        
            # Send the coordinates to JavaScript to update the marker
            js_code = f"setMarker({lat}, {lon});"  # JavaScript code to set the marker at the new location
            self.map_view.page().runJavaScript(js_code)  # Execute the JavaScript on the web page
        


    class camerafeedtab(QWidget):
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
            stream_url = "http://127.0.0.1:5000/video_feed"
            self.video_thread = ObjectDetection(self.video_label,stream_url)
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
        def __init__(self, label, stream_url):
            super().__init__()
            self.label = label
            self.running = True
            self.stream_url = stream_url  # Pass the stream URL as a parameter
            self.cap = cv2.VideoCapture(self.stream_url)  # Use the provided stream URL
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=self.device)
            if self.device == 'cuda':
                self.model.half()
        
            self.frame_count = 0  # To control frame processing rate

            # Check if the stream is opened correctly
            if not self.cap.isOpened():
                print("Error: Could not open video feed.")
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

                # Process every 2nd frame to reduce load (optional)
                if self.frame_count % 2 == 0:
                    # Resize the frame to a smaller resolution before inference (optional)
                    new_width = 640  # Set your desired width
                    new_height = 480  # Set your desired height
                    resized_frame = cv2.resize(frame, (new_width, new_height))

                    # Perform inference on the resized frame
                    results = self.model(resized_frame)

                    # Render the results on the frame (draw bounding boxes)
                    frame_with_boxes = results.render()[0]

                    # Convert frame with boxes to QImage for displaying
                    h, w, ch = frame_with_boxes.shape
                    bytes_per_line = ch * w
                    q_img = QImage(frame_with_boxes.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
                    pixmap = QPixmap(q_img)

                    # Update QLabel with the processed frame
                    self.label.setPixmap(pixmap)

                # Optional: Control the rate at which frames are processed
                cv2.waitKey(1)  # 1 ms delay to let the system process other events

        def stop(self):
            """Stop the thread"""
            self.running = False
            self.cap.release()  # Release the video capture object


    class DroneControlWidget(QWidget):
        def __init__(self, client):
            super().__init__()
            self.drone = None
            self.client = client
    
            # Main layout
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)  # Reduce margins for compactness
    
            # Status Group
            status_group = QGroupBox("Connection Status")
            status_group.setFlat(True)  # Make it look cleaner
            status_layout = QVBoxLayout()
            self.status_label = QLabel("Status: Disconnected")
            status_layout.addWidget(self.status_label)
            status_group.setLayout(status_layout)
            main_layout.addWidget(status_group)
    
            # Server Connect Group
            server_group = QGroupBox("Server Connection")
            server_group.setFlat(True)  # Clean border for server connection section
            server_layout = QVBoxLayout()
            self.connect_server = QPushButton("Connect Server")
            self.connect_server.setFixedSize(150, 40)  # Fix button size for uniformity
    
            # Connect the button's click event to the connect_to_server function
            self.connect_server.clicked.connect(self.connect_to_server)
            server_layout.addWidget(self.connect_server)
            server_group.setLayout(server_layout)
            main_layout.addWidget(server_group)
    
            # Drone Control Group   
            control_group = QGroupBox("Drone Control")
            control_group.setFlat(True)  # Clean border for control section
            control_layout = QVBoxLayout()
            
            # Arm/Disarm Buttons
            arm_disarm_layout = QHBoxLayout()
            self.arm_button = QPushButton("Arm Drone")
            self.disarm_button = QPushButton("Disarm Drone")
            
            # Set uniform button sizes
            self.arm_button.setFixedSize(120, 40)
            self.disarm_button.setFixedSize(120, 40)
    
            self.arm_button.clicked.connect(self.on_arm_clicked)
            self.disarm_button.clicked.connect(self.on_disarm_clicked)
    
            # Add buttons directly to the layout without unnecessary spacer
            arm_disarm_layout.addWidget(self.arm_button)
            arm_disarm_layout.addWidget(self.disarm_button)
    
            # Align buttons to the center
            arm_disarm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
            control_layout.addLayout(arm_disarm_layout)
    
            control_group.setLayout(control_layout)
            main_layout.addWidget(control_group)
    
            # Set the main layout for the widget
            self.setLayout(main_layout)
    
        def on_arm_clicked(self):
            """Handles the arm button click."""
            self.client.send("arm".encode('utf-8'))  # Send arm command
    
        def on_disarm_clicked(self):
            """Handles the disarm button click."""
            self.client.send("disarm".encode("utf-8"))  # Send disarm command
    
        def connect_to_server(self):
            """Try to connect to the server and update the status."""
            if self.client.connect():
                self.update_status("Status: Connected")
            else:
                self.update_status("Status: Failed to Connect")
    
        def update_status(self, status_text):
            """Update the status label with the provided text."""
            self.status_label.setText(status_text)
    


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PyQt6 Application")

            # Initialize DroneControl instance
           
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
            # self.map_monitoring_tab = MapMonitoringTab()
            self.tabs.addTab(GPSCalibrationTab(), "GPS Calibration")
            self.tabs.addTab(camerafeedtab(), "Flask Camera Feed")
            c=Client()

            self.tabs.addTab(DroneControlWidget(c), "Drone Control")
    
            self.apply_dark_theme()

        def apply_dark_theme(self):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                    color: white;
                }
                QTabBar::tab {
                    background: #1e1e1e;
                    color: white;
                }
            """)

        def stop_all_resources(self):
           """Clean up resources like threads and connections."""
           # Stop camera feed thread
           if self.camera_feed_tab.video_thread is not None:
               self.camera_feed_tab.video_thread.stop()
               self.camera_feed_tab.video_thread.wait()
           # Disconnect drone connection
           if self.drone:
               try:
                   self.drone.connection.close()
                   print("Drone connection closed.")
               except Exception as e:
                   print(f"Error closing drone connection: {e}")
        def closeEvent(self, event):
            """Handle application exit to release resources."""
            self.stop_all_resources()
            super().closeEvent(event)

    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.resize(800, 600)
        window.show()
        # drone = DroneControl("/dev/ttyACM0")  # Replace with your connection string
        # drone.arm()
        # drone.set_mode("GUIDED")
        # drone.send_gps_waypoint(37.7749, -122.4194)  # Example coordinates
        # drone.monitor_position()
        sys.exit(app.exec())

    main()


if __name__== '__main__':
    queue=multiprocessing.Queue()
    apps= multiprocessing.Process(target=app)
    clients =multiprocessing.Process(target=client)
    apps.start()
    clients.start()
    apps.join()
    clients.join()
