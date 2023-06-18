def bfs(grid, start, end):
    queue = [((start[0], start[1]), [])]
    seen = set()

    while queue:
        ((x, y), path) = queue.pop(0)
        node = (x, y)
        if node not in seen:
            seen.add(node)
            path = path + [node]
            if node == end:

                print(f"START {start}")
                print(f"END {end}")
                print(f"PATH {path}")

                return path
            for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                next_x, next_y = x + direction[0], y + direction[1]
                queue.append(((next_x, next_y), path))

    return None


def create_grid(size, obstacles):
    grid = [[0 for _ in range(size[0])] for _ in range(size[1])]
    for obstacle in obstacles:
        grid[obstacle[1]][obstacle[0]] = 1
    return grid


def find_path(grid_size, robot_position, white_balls, orange_balls, red_crosses):
    grid = create_grid(grid_size, red_crosses)
    balls = white_balls + orange_balls
    shortest_path = None
    print("robot position: ", robot_position)

    def calculate_distance(pos1, pos2):
        (x1, y1) = pos1
        (x2, y2) = pos2
        return abs(x1 - x2) + abs(y1 - y2)

    def find_closest_ball(robot_pos, balls):
        closest_ball = None
        min_distance = float('inf')
        for ball in balls:
            distance = calculate_distance(robot_pos, ball)
            if distance < min_distance:
                min_distance = distance
                closest_ball = ball
        return closest_ball

    while balls:
        closest_ball = find_closest_ball(robot_position, balls)
        if closest_ball is None:
            break

        print("Finding path to ball: ", closest_ball)
        start = (robot_position[0],  robot_position[1])
        goal = (closest_ball[0],  closest_ball[1])
        # start = (robot_position[0], grid_size[1] - robot_position[1])
        # goal = (closest_ball[0], grid_size[1] - closest_ball[1])
        path = bfs(grid, start, goal)
        if path is not None:
            shortest_path = path
            break

        print("No path to ball: ", closest_ball)
        balls.remove(closest_ball)

    return shortest_path

