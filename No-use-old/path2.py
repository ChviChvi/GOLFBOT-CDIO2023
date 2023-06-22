import math
import heapq

def calculate_distance(position1, position2):
    x1, y1 = position1
    x2, y2 = position2
    return math.hypot(x2 - x1, y2 - y1)

def find_nearest_ball(grid, robot_position, balls, red_crosses):
    distances = {tuple(ball): calculate_distance(robot_position, ball) for ball in balls if ball not in red_crosses}
    nearest_ball = min(distances, key=distances.get, default=None)
    return list(nearest_ball) if nearest_ball else None

def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            print(f"WARNING: No path found from {start} to {goal}")
            return []
    path.append(start)
    path.reverse()
    return [list(p) for p in path]

def astar(grid, start, goal):
    start, goal = tuple(start), tuple(goal)
    open_set = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            break

        for neighbor in get_neighbors(grid, current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + calculate_distance(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    # else:
    #     print(f"WARNING: No path found from {start} to {goal}")
    #     return {}, {}, False

    return came_from


# def get_neighbors(grid, position):
#     x, y = position
#     width, height = len(grid), len(grid[0])
#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
#     neighbors = [(x + dx, y + dy) for dx, dy in directions if 0 <= x + dx < width and 0 <= y + dy < height and grid[x + dx][y + dy] != 1]
#     return neighbors

def get_neighbors(grid, position):
# Get valid neighboring positions in the grid
    x, y = position
    neighbors = []

    # Check horizontal and vertical neighbors
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if (0 <= nx < len(grid)) and (0 <= ny < len(grid[0])) and (grid[nx][ny] != 1):
            neighbors.append((nx, ny))

    #Check diagonal neighbors
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + dx, y + dy
        if (0 <= nx < len(grid)) and (0 <= ny < len(grid[0])) and (grid[nx][ny] != 1):
            neighbors.append((nx, ny))

    return neighbors
