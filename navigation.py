import heapq
import numpy as np
from geopy.distance import distance

# Define start and target GPS coordinates
start_lat, start_lon = 10.0, 20.0
target_lat, target_lon = 12.0, 22.0

# Create rectangular boundary
min_lat = min(start_lat, target_lat)
max_lat = max(start_lat, target_lat)
min_lon = min(start_lon, target_lon)
max_lon = max(start_lon, target_lon)

# Define grid resolution (in degrees, e.g., ~11m for 0.0001)
resolution = 0.0005  # Adjust from 0.0001 to 0.0005 (larger steps)


# Generate grid
lat_steps = int((max_lat - min_lat) / resolution) + 1
lon_steps = int((max_lon - min_lon) / resolution) + 1

def latlon_to_index(lat, lon):
    return int((lat - min_lat) / resolution), int((lon - min_lon) / resolution)

def index_to_latlon(i, j):
    return min_lat + i * resolution, min_lon + j * resolution

# Priority Queue for A*
class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

from geopy.distance import distance

from geopy.distance import distance
import math

# def heuristic(a, b):
#     # Check if a and b are tuples
#     if not isinstance(a, tuple) or not isinstance(b, tuple):
#         print(f"❌ ERROR: `a` or `b` is not a tuple → a: {a}, b: {b}")
#         return float("inf")

#     # Check if tuples have exactly 2 elements
#     if len(a) != 2 or len(b) != 2:
#         print(f"❌ ERROR: Tuple length incorrect → a: {a}, b: {b}")
#         return float("inf")

#     # Check if values are numeric and finite
#     if any(not isinstance(coord, (int, float)) or not math.isfinite(coord) for coord in a + b):
#         print(f"❌ ERROR: Non-numeric or infinite values → a: {a}, b: {b}")
#         return float("inf")

#     # Check for valid latitude/longitude range
#     if not (-90 <= a[0] <= 90 and -180 <= a[1] <= 180):
#         print(f"❌ ERROR: Invalid latitude/longitude in `a` → {a}")
#         return float("inf")

#     if not (-90 <= b[0] <= 90 and -180 <= b[1] <= 180):
#         print(f"❌ ERROR: Invalid latitude/longitude in `b` → {b}")
#         return float("inf")

#     return distance(a, b).m  # Geodesic distance in meters

# def heuristic(a, b):
#     return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance in lat/lon
from geopy.distance import geodesic

def heuristic(a, b):
    return geodesic(a, b).meters  # Direct geodesic distance


# def a_star_search(start, goal, obstacles):
#     start_index = latlon_to_index(*start)
#     goal_index = latlon_to_index(*goal)

#     frontier = PriorityQueue()
#     frontier.put(start_index, 0)
#     came_from = {}
#     cost_so_far = {}

#     came_from[start_index] = None
#     cost_so_far[start_index] = 0

#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

#     while not frontier.empty():
#         current = frontier.get()

#         if current == goal_index:
#             break

#         for d in directions:
#             neighbor = (current[0] + d[0], current[1] + d[1])
#             if not (0 <= neighbor[0] < lat_steps and 0 <= neighbor[1] < lon_steps):
#                 continue

#             neighbor_latlon = index_to_latlon(*neighbor)
#             if neighbor_latlon in obstacles:
#                 continue

#             # print(f"🔍 Debug: current={current}, index_to_latlon(*current)={index_to_latlon(*current)}, neighbor_latlon={neighbor_latlon}")

#             new_cost = cost_so_far[current] + heuristic(index_to_latlon(*current), neighbor_latlon)

#             if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
#                 cost_so_far[neighbor] = new_cost
#                 priority = new_cost + heuristic(neighbor_latlon, goal)
#                 frontier.put(neighbor, priority)
#                 came_from[neighbor] = current

#     # Reconstruct path
#     current = goal_index
#     path = []
#     while current is not None:
#         path.append(index_to_latlon(*current))
#         current = came_from.get(current)
#     path.reverse()
#     return path


# def a_star_search(start, goal, obstacles):
#     start_index = latlon_to_index(*start)
#     goal_index = latlon_to_index(*goal)

#     frontier = PriorityQueue()
#     frontier.put(start_index, 0)
#     came_from = {}
#     cost_so_far = {}

#     came_from[start_index] = None
#     cost_so_far[start_index] = 0

#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

#     threshold = 0.00015  # Slightly larger than resolution

#     while not frontier.empty():
#         current = frontier.get()
#         current_latlon = index_to_latlon(*current)

#         if heuristic(current_latlon, goal) < threshold:
#             print("✅ Goal reached!")
#             break

#         for d in directions:
#             neighbor = (current[0] + d[0], current[1] + d[1])
#             if not (0 <= neighbor[0] < lat_steps and 0 <= neighbor[1] < lon_steps):
#                 continue

#             neighbor_latlon = index_to_latlon(*neighbor)

#             # Improved obstacle checking with a threshold
#             if any(heuristic(neighbor_latlon, obs) < threshold for obs in obstacles):
#                 continue

#             new_cost = cost_so_far[current] + heuristic(current_latlon, neighbor_latlon)

#             if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
#                 cost_so_far[neighbor] = new_cost
#                 priority = new_cost + heuristic(neighbor_latlon, goal)
#                 frontier.put(neighbor, priority)
#                 came_from[neighbor] = current

#     # Reconstruct path
#     current = goal_index
#     path = []
#     while current is not None:
#         path.append(index_to_latlon(*current))
#         current = came_from.get(current)

#     path.reverse()
#     return path

def a_star_search(start, goal, obstacles):
    start_index = latlon_to_index(*start)
    goal_index = latlon_to_index(*goal)

    print(f"🟢 Start Index: {start_index}, Goal Index: {goal_index}")
    
    frontier = PriorityQueue()
    frontier.put(start_index, 0)
    came_from = {}
    cost_so_far = {}

    came_from[start_index] = None
    cost_so_far[start_index] = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    threshold = 0.00015  # Slightly larger than resolution

    while not frontier.empty():
        current = frontier.get()
        current_latlon = index_to_latlon(*current)

        print(f"🔹 Expanding node: {current}, {current_latlon}")

        if current == goal_index:

            print("✅ Goal reached!")
            break

        for d in directions:
            neighbor = (current[0] + d[0], current[1] + d[1])
            if not (0 <= neighbor[0] < lat_steps and 0 <= neighbor[1] < lon_steps):
                print(f"⏭️ Skipping out-of-bounds: {neighbor}")
                continue

            neighbor_latlon = index_to_latlon(*neighbor)

            # Check for obstacles
            if any(heuristic(neighbor_latlon, obs) < threshold for obs in obstacles):
                print(f"🚧 Skipping obstacle at {neighbor_latlon}")
                continue

            new_cost = cost_so_far[current] + heuristic(current_latlon, neighbor_latlon)

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor_latlon, goal)
                frontier.put(neighbor, priority)
                came_from[neighbor] = current

    # Reconstruct path
    current = goal_index
    path = []
    while current is not None:
        path.append(index_to_latlon(*current))
        current = came_from.get(current)

    if not path:
        print("❌ No path found!")
    else:
        print("✅ Path found!")

    path.reverse()
    return path


# Example obstacle (lat, lon)
obstacles = {(10.5, 20.5), (11.0, 21.0)}



path = a_star_search((start_lat, start_lon), (target_lat, target_lon), obstacles)

print("Path:")
for p in path:
    print(p)
