import math

# Calculate Euclidean distance between two points
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Calculate orientation to face a target position
def calculate_orientation(robot_position, target_position):
    x1, y1 = robot_position
    x2, y2 = target_position
    rad = math.atan2(y2-y1, x2-x1)
    deg = math.degrees(rad)
    if deg < 0:
        deg += 360
    return deg

# Check if a path to a target is clear of obstacles
def is_valid_path(robot_position, target_position, obstacles):
    for obstacle in obstacles:
        if calculate_distance(robot_position, obstacle) + calculate_distance(obstacle, target_position) == calculate_distance(robot_position, target_position):
            return False
    return True

# Find nearest ball with a valid path
def find_nearest_ball(robot_position, balls, obstacles):
    valid_balls = [ball for ball in balls if is_valid_path(robot_position, ball, obstacles)]
    if not valid_balls:
        return None
    distances = [calculate_distance(robot_position, ball) for ball in valid_balls]
    nearest_valid_ball = valid_balls[distances.index(min(distances))]
    return nearest_valid_ball


# Main algorithm
def get_orientation_and_target(robot_position, robot_orientation, grid_size, white_balls, orange_balls, red_crosses):
    balls = white_balls + orange_balls

    if not balls:  # If there are no balls, return None
        return None, None

    nearest_ball = find_nearest_ball(robot_position, balls, red_crosses)

    if nearest_ball is None:
        print("No reachable balls found.")
        return None, None

    new_orientation = calculate_orientation(robot_position, nearest_ball)
    
    # Adjust the orientation to a 360-degree system with respect to the initial robot orientation
    relative_orientation = (new_orientation - robot_orientation) % 360

    return round(relative_orientation), nearest_ball
