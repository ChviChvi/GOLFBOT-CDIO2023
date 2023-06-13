import heapq
import math

def heuristic(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def astar(grid, start, goal):
    start = tuple(start)
    goal = tuple(goal)
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for next in get_neighbors(grid, current):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(frontier, (priority, next))
                came_from[next] = current

    return came_from, cost_so_far

def get_neighbors(grid, current):
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    result = []
    for dir in dirs:
        nx, ny = current[0] + dir[0], current[1] + dir[1]
        if nx >= 0 and ny >= 0 and nx < len(grid) and ny < len(grid[0]) and grid[nx][ny] != 1:
            result.append((nx, ny))
    return result

def reconstruct_path(came_from, start, goal):
    start = tuple(start)
    goal = tuple(goal)
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def find_nearest_ball(grid, robot_pos, balls):
    robot_pos = tuple(robot_pos)
    min_dist = math.inf
    nearest_ball = None
    for ball in balls:
        ball = tuple(ball)
        dist = heuristic(robot_pos, ball)
        if dist < min_dist:
            min_dist = dist
            nearest_ball = ball
    return nearest_ball
