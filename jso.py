# import numpy as np
# import geopandas as gpd
# import osmnx as ox
# import matplotlib.pyplot as plt

# def generate_map_patch(start_coords, end_coords, grid_size=(20, 20)):
#     """
#     Generate a small map patch using OpenStreetMap based on two GPS coordinates.

#     :param start_coords: (lat, lon) of the starting point
#     :param end_coords: (lat, lon) of the destination point
#     :param grid_size: (rows, cols) for the output grid resolution
#     :return: Map patch as a grid and visualization
#     """

#     # Determine the bounding box from start and end coordinates
#     min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
#     min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

#     # Get the map data from OpenStreetMap
#     bbox = (min_lat, max_lat, min_lon, max_lon)
#     G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type="walk")



#     # Convert to a GeoDataFrame for grid-based analysis
#     nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

#     # Create an empty grid
#     grid = np.zeros(grid_size, dtype=int)

#     # Map latitude/longitude to grid indices
#     lat_range = np.linspace(min_lat, max_lat, grid_size[0])
#     lon_range = np.linspace(min_lon, max_lon, grid_size[1])

#     def latlon_to_grid(lat, lon):
#         """Convert latitude/longitude to grid index."""
#         row = np.argmin(np.abs(lat_range - lat))
#         col = np.argmin(np.abs(lon_range - lon))
#         return row, col

#     # Mark road edges as free space (0) and non-road areas as obstacles (1)
#     for _, edge in edges.iterrows():
#         u = nodes.loc[edge['u']]
#         v = nodes.loc[edge['v']]
#         row_u, col_u = latlon_to_grid(u['y'], u['x'])
#         row_v, col_v = latlon_to_grid(v['y'], v['x'])
#         grid[row_u, col_u] = 0  # Free space (road)
#         grid[row_v, col_v] = 0  # Free space (road)



#     # Mark start and end locations
#     start_row, start_col = latlon_to_grid(*start_coords)
#     end_row, end_col = latlon_to_grid(*end_coords)
#     grid[start_row, start_col] = 8  # Start point
#     grid[end_row, end_col] = 9  # End point

#     # Visualization
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(grid, cmap="gray", origin="upper")
#     ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
#     ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
#     ax.set_title("Generated Map Patch")
#     ax.legend()
#     plt.show()

#     return grid

# # Example Usage
# start_latlon = (37.7749, -122.4194)  # Example: San Francisco
# end_latlon = (37.7755, -122.4180)   # Slightly nearby target

# grid_map = generate_map_patch(start_latlon, end_latlon)
# def generate_map_patch(start_coords, end_coords, grid_size=(20, 20)):
#     """
#     Generate a small map patch using OpenStreetMap based on two GPS coordinates.
#     """

#     # Determine the bounding box from start and end coordinates
#     min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
#     min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

#     # Get the map data from OpenStreetMap using the updated bounding box format
#     bbox = (min_lat, max_lat, min_lon, max_lon)
#     G = ox.graph_from_bbox(bbox, network_type="walk")  # Corrected call

#     # Convert to a GeoDataFrame for grid-based analysis
#     nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

#     # Debug: print the column names to check for 'u' and 'v'
#     print("Edge columns:", edges.columns)
#     print("Node columns:", nodes.columns)

#     # Create an empty grid
#     grid = np.zeros(grid_size, dtype=int)

#     # Map latitude/longitude to grid indices
#     lat_range = np.linspace(min_lat, max_lat, grid_size[0])
#     lon_range = np.linspace(min_lon, max_lon, grid_size[1])

#     def latlon_to_grid(lat, lon):
#         """Convert latitude/longitude to grid index."""
#         row = np.argmin(np.abs(lat_range - lat))
#         col = np.argmin(np.abs(lon_range - lon))
#         return row, col

#     # Mark road edges as free space (0) and non-road areas as obstacles (1)
#     for _, edge in edges.iterrows():
#         print(edge)  # Debug: inspect the current edge row
#         u = nodes.loc[edge['u']]  # Adjust if needed based on column names
#         v = nodes.loc[edge['v']]
#         row_u, col_u = latlon_to_grid(u['y'], u['x'])
#         row_v, col_v = latlon_to_grid(v['y'], v['x'])
#         grid[row_u, col_u] = 0  # Free space (road)
#         grid[row_v, col_v] = 0  # Free space (road)

#     # Mark start and end locations
#     start_row, start_col = latlon_to_grid(*start_coords)
#     end_row, end_col = latlon_to_grid(*end_coords)
#     grid[start_row, start_col] = 8  # Start point
#     grid[end_row, end_col] = 9  # End point

#     # Visualization
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(grid, cmap="gray", origin="upper")
#     ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
#     ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
#     ax.set_title("Generated Map Patch")
#     ax.legend()
#     plt.show()

#     return grid
# print()

# import numpy as np
# import osmnx as ox
# import matplotlib.pyplot as plt

# def generate_map_patch(start_coords, end_coords, grid_size=(20, 20)):
#     """
#     Generate a small map patch using OpenStreetMap based on two GPS coordinates.
#     """

#     # Determine the bounding box from start and end coordinates
#     min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
#     min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

#     # Get the map data from OpenStreetMap using the updated bounding box format
#     bbox = (min_lat, max_lat, min_lon, max_lon)
#     G = ox.graph_from_bbox(*bbox, network_type="walk")  # Corrected call

#     # Convert to a GeoDataFrame for grid-based analysis
#     nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

#     # Debug: print the column names to check for 'u' and 'v'
#     print("Edge columns:", edges.columns)
#     print("Node columns:", nodes.columns)

#     # Create an empty grid
#     grid = np.zeros(grid_size, dtype=int)

#     # Map latitude/longitude to grid indices
#     lat_range = np.linspace(min_lat, max_lat, grid_size[0])
#     lon_range = np.linspace(min_lon, max_lon, grid_size[1])

#     def latlon_to_grid(lat, lon):
#         """Convert latitude/longitude to grid index."""
#         row = np.argmin(np.abs(lat_range - lat))
#         col = np.argmin(np.abs(lon_range - lon))
#         return row, col

#     # Mark road edges as free space (0) and non-road areas as obstacles (1)
#     for _, edge in edges.iterrows():
#         # Debug: print edge details
#         print("Processing edge:", edge)

#         # Debug: print the u and v nodes of the current edge
#         try:
#             u = nodes.loc[edge['u']]  # Check if 'u' exists
#             v = nodes.loc[edge['v']]  # Check if 'v' exists
#         except KeyError as e:
#             print("KeyError: Check the column names for 'u' and 'v'. Error:", e)
#             continue

#         print("Start node:", u)
#         print("End node:", v)

#         row_u, col_u = latlon_to_grid(u['y'], u['x'])
#         row_v, col_v = latlon_to_grid(v['y'], v['x'])
#         grid[row_u, col_u] = 0  # Free space (road)
#         grid[row_v, col_v] = 0  # Free space (road)

#     # Mark start and end locations
#     start_row, start_col = latlon_to_grid(*start_coords)
#     end_row, end_col = latlon_to_grid(*end_coords)
#     grid[start_row, start_col] = 8  # Start point
#     grid[end_row, end_col] = 9  # End point

#     # Visualization
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(grid, cmap="gray", origin="upper")
#     ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
#     ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
#     ax.set_title("Generated Map Patch")
#     ax.legend()
#     plt.show()

#     return grid

# # Example usage
# start_latlon = (37.7749, -122.4194)  # Example start coordinates (San Francisco)
# end_latlon = (37.8044, -122.2711)  # Example end coordinates (Oakland)
# grid_map = generate_map_patch(start_latlon, end_latlon)




# import numpy as np
# import matplotlib.pyplot as plt

# def latlon_to_grid(lat, lon, lat_range, lon_range, grid_size):
#     """
#     Convert latitude and longitude to grid indices.
#     """
#     row = np.argmin(np.abs(lat_range - lat))  # Find the nearest latitude in the grid
#     col = np.argmin(np.abs(lon_range - lon))  # Find the nearest longitude in the grid
#     return row, col

# def generate_map_patch(start_coords, end_coords, grid_size=(20, 20)):
#     """
#     Generate a small map patch for drone navigation using lat/lon coordinates.
#     """
#     min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
#     min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

#     # Define latitude and longitude ranges based on the bounding box
#     lat_range = np.linspace(min_lat, max_lat, grid_size[0])
#     lon_range = np.linspace(min_lon, max_lon, grid_size[1])

#     # Initialize the grid (0 represents free space, 1 represents obstacles, etc.)
#     grid = np.zeros(grid_size, dtype=int)

#     # Convert start and end coordinates to grid indices
#     start_row, start_col = latlon_to_grid(start_coords[0], start_coords[1], lat_range, lon_range, grid_size)
#     end_row, end_col = latlon_to_grid(end_coords[0], end_coords[1], lat_range, lon_range, grid_size)

#     # Mark start and end locations on the grid
#     grid[start_row, start_col] = 8  # Start point (e.g., '8' for start)
#     grid[end_row, end_col] = 9  # End point (e.g., '9' for end)

#     # Visualization of the grid
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(grid, cmap="gray", origin="upper")
#     ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
#     ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
#     ax.set_title("Generated Map Patch for Drone Navigation")
#     ax.legend()
#     plt.show()

#     return grid

# # Example usage with coordinates (latitude, longitude)
# start_latlon = (37.7749, -122.4194)  # Example: San Francisco (Start)
# end_latlon = (37.8044, -122.2711)  # Example: Oakland (End)
# grid_map = generate_map_patch(start_latlon, end_latlon)
# import numpy as np
# import matplotlib.pyplot as plt
# from queue import PriorityQueue

# def latlon_to_grid(lat, lon, lat_range, lon_range, grid_size):
#     """
#     Convert latitude and longitude to grid indices.
#     """
#     row = np.argmin(np.abs(lat_range - lat))  # Find the nearest latitude in the grid
#     col = np.argmin(np.abs(lon_range - lon))  # Find the nearest longitude in the grid
#     return row, col

# def a_star(grid, start, end):
#     """
#     A* Pathfinding algorithm to find the shortest path.
#     """
#     # Directions for 4 possible moves (Up, Down, Left, Right)
#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
#     def heuristic(a, b):
#         # Manhattan distance heuristic
#         return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
#     # Initialize open and closed lists
#     open_list = PriorityQueue()
#     open_list.put((0, start))  # (priority, position)
#     came_from = {}  # To reconstruct path
#     g_score = {start: 0}  # Cost from start
#     f_score = {start: heuristic(start, end)}  # Estimated cost to end
    
#     while not open_list.empty():
#         _, current = open_list.get()

#         if current == end:
#             # Reconstruct the path
#             path = []
#             while current in came_from:
#                 path.append(current)
#                 current = came_from[current]
#             path.append(start)
#             path.reverse()
#             return path
        
#         # Check neighbors
#         for direction in directions:
#             neighbor = (current[0] + direction[0], current[1] + direction[1])
#             if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
#                 tentative_g_score = g_score[current] + 1
#                 if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
#                     came_from[neighbor] = current
#                     g_score[neighbor] = tentative_g_score
#                     f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
#                     open_list.put((f_score[neighbor], neighbor))
    
#     return None  # Return None if no path is found

# def generate_map_patch(start_coords, end_coords, grid_size=(20, 20)):
#     """
#     Generate a small map patch for drone navigation using lat/lon coordinates.
#     """
#     min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
#     min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

#     # Define latitude and longitude ranges based on the bounding box
#     lat_range = np.linspace(min_lat, max_lat, grid_size[0])
#     lon_range = np.linspace(min_lon, max_lon, grid_size[1])

#     # Initialize the grid (0 represents free space, 1 represents obstacles, etc.)
#     grid = np.zeros(grid_size, dtype=int)

#     # Convert start and end coordinates to grid indices
#     start_row, start_col = latlon_to_grid(start_coords[0], start_coords[1], lat_range, lon_range, grid_size)
#     end_row, end_col = latlon_to_grid(end_coords[0], end_coords[1], lat_range, lon_range, grid_size)

#     # Mark start and end locations on the grid
#     grid[start_row, start_col] = 8  # Start point (e.g., '8' for start)
#     grid[end_row, end_col] = 9  # End point (e.g., '9' for end)

#     # Find the shortest path using A*
#     start = (start_row, start_col)
#     end = (end_row, end_col)
#     path = a_star(grid, start, end)

#     # Visualize the grid and the path
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.imshow(grid, cmap="gray", origin="upper")
#     ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
#     ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
    
#     # Plot the path
#     if path:
#         path_x, path_y = zip(*path)
#         ax.plot(path_y, path_x, color="green", linewidth=2, label="Path")
    
#     ax.set_title("Generated Map Patch for Drone Navigation")
#     ax.legend()
#     plt.show()

#     return grid, path

# # Example usage with coordinates (latitude, longitude)
# start_latlon = (37.7749, -122.4194)  # Example: San Francisco (Start)
# end_latlon = (37.8044, -122.2711)  # Example: Oakland (End)
# grid_map, path = generate_map_patch(start_latlon, end_latlon)
# print("Waypoints of the shortest path:", path)


import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue

def latlon_to_grid(lat, lon, lat_range, lon_range, grid_size):
    """
    Convert latitude and longitude to grid indices.
    """
    row = np.argmin(np.abs(lat_range - lat))  # Find the nearest latitude in the grid
    col = np.argmin(np.abs(lon_range - lon))  # Find the nearest longitude in the grid
    return row, col

def a_star(grid, start, end):
    """
    A* Pathfinding algorithm to find the shortest path, avoiding obstacles.
    """
    # Directions for 4 possible moves (Up, Down, Left, Right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def heuristic(a, b):
        # Manhattan distance heuristic (suitable for grid-based pathfinding)
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    # Initialize open and closed lists
    open_list = PriorityQueue()
    open_list.put((0, start))  # (priority, position)
    came_from = {}  # To reconstruct path
    g_score = {start: 0}  # Cost from start
    f_score = {start: heuristic(start, end)}  # Estimated cost to end
    
    while not open_list.empty():
        _, current = open_list.get()

        if current == end:
            # Reconstruct the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        
        # Check neighbors
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if grid[neighbor[0], neighbor[1]] == 1:  # Check if the cell is an obstacle
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    open_list.put((f_score[neighbor], neighbor))
    
    return None  # Return None if no path is found

def generate_map_patch(start_coords, end_coords, grid_size=(20, 20), obstacle_percentage=0.2):
    """
    Generate a small map patch for drone navigation using lat/lon coordinates.
    """
    min_lat, max_lat = min(start_coords[0], end_coords[0]), max(start_coords[0], end_coords[0])
    min_lon, max_lon = min(start_coords[1], end_coords[1]), max(start_coords[1], end_coords[1])

    # Define latitude and longitude ranges based on the bounding box
    lat_range = np.linspace(min_lat, max_lat, grid_size[0])
    lon_range = np.linspace(min_lon, max_lon, grid_size[1])

    # Initialize the grid (0 represents free space, 1 represents obstacles)
    grid = np.zeros(grid_size, dtype=int)

    # Add random obstacles to the grid
    num_obstacles = int(obstacle_percentage * grid_size[0] * grid_size[1])
    for _ in range(num_obstacles):
        row = np.random.randint(0, grid_size[0])
        col = np.random.randint(0, grid_size[1])
        grid[row, col] = 1  # Mark as obstacle

    # Convert start and end coordinates to grid indices
    start_row, start_col = latlon_to_grid(start_coords[0], start_coords[1], lat_range, lon_range, grid_size)
    end_row, end_col = latlon_to_grid(end_coords[0], end_coords[1], lat_range, lon_range, grid_size)

    # Mark start and end locations on the grid
    grid[start_row, start_col] = 8  # Start point (e.g., '8' for start)
    grid[end_row, end_col] = 9  # End point (e.g., '9' for end)

    # Find the shortest path using A*
    start = (start_row, start_col)
    end = (end_row, end_col)
    path = a_star(grid, start, end)

    # Visualize the grid and the path
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap="gray", origin="upper")
    ax.scatter(start_col, start_row, color="red", marker="o", label="Start")
    ax.scatter(end_col, end_row, color="blue", marker="o", label="End")
    
    # Plot the path
    if path:
        path_x, path_y = zip(*path)
        ax.plot(path_y, path_x, color="green", linewidth=2, label="Path")
    
    ax.set_title("Generated Map Patch for Drone Navigation")
    ax.legend()
    plt.show()

    return grid, path

# Example usage with coordinates (latitude, longitude)
start_latlon = (37.7749, -122.4194)  # Example: San Francisco (Start)
end_latlon = (37.8044, -122.2711)  # Example: Oakland (End)
grid_map, path = generate_map_patch(start_latlon, end_latlon)
print("Waypoints of the shortest path:", path)
