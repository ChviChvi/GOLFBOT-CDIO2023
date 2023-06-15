import math
import heapq

def calculate_distance(position1, position2):
    # Calculate Euclidean distance between two positions
    x1, y1 = position1
    x2, y2 = position2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def find_nearest_ball(grid, robot_position, balls, red_crosses):
    print("using second method")
    # Find the nearest ball to the robot's position
    min_distance = float('inf')
    nearest_ball = None

    for ball in balls:
        print("1")
        if ball not in red_crosses:  # Exclude red crosses
            distance = calculate_distance(robot_position, ball)
            print("2")
            if distance < min_distance:
                min_distance = distance
                nearest_ball = ball
                print("3")

    print(nearest_ball)
    return nearest_ball

def reconstruct_path(came_from, start, goal):
    current = tuple(goal)  # Convert goal to tuple
    path = []

    while current != tuple(start):  # Convert start to tuple
        path.append(list(current))  # Convert current back to list for appending to path
        current = came_from[tuple(current)]  # Convert current to tuple for dictionary lookup

    path.append(list(start))  # Convert start back to list for appending to path
    path.reverse()
    return path

def astar(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))  # Push start node with priority 0
    came_from = {}
    cost_so_far = {}
    came_from[tuple(start)] = None
    cost_so_far[tuple(start)] = 0

    while open_set:
        current = heapq.heappop(open_set)[1]  # Pop the node with the lowest priority (cost)
        current_tuple = tuple(current)  # Convert current coordinates to a tuple

        if current == goal:
            return came_from, cost_so_far, True

        for neighbor in get_neighbors(grid, current):
            neighbor_tuple = tuple(neighbor)  # Convert neighbor coordinates to a tuple
            new_cost = cost_so_far[current_tuple] + 1  # Assuming a cost of 1 to move to a neighboring cell

            if neighbor_tuple not in cost_so_far or new_cost < cost_so_far[neighbor_tuple]:
                cost_so_far[neighbor_tuple] = new_cost
                priority = new_cost + calculate_distance(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor_tuple] = current_tuple

    return came_from, cost_so_far, False  # Return False if the goal was not reached

def get_neighbors(grid, position):
    # Get valid neighboring positions in the grid
    x, y = position
    neighbors = []

    if x > 0 and grid[x-1][y] != 1:  # Check left neighbor
        neighbors.append((x-1, y))
    if x < len(grid)-1 and grid[x+1][y] != 1:  # Check right neighbor
        neighbors.append((x+1, y))
    if y > 0 and grid[x][y-1] != 1:  # Check top neighbor
        neighbors.append((x, y-1))
    if y < len(grid[0])-1 and grid[x][y+1] != 1:  # Check bottom neighbor
        neighbors.append((x, y+1))

    return neighbors