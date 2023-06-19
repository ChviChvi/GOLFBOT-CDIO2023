def find_goal(grid, robot_position, goal_position, red_crosses):
    shortest_path = None
    goal= goal_position
    print("robot position: ", robot_position)
    print("goal position: ", goal_position)

    def calculate_distance(pos1, pos2):
        (x1, y1) = pos1
        (x2, y2) = pos2
        return abs(x1 - x2) + abs(y1 - y2)


    print("Finding path to goal: ", goal)
    start = (robot_position[0],  robot_position[1])
    goal = (goal[0],  goal[1])
        # start = (robot_position[0], grid_size[1] - robot_position[1])
        # goal = (closest_ball[0], grid_size[1] - closest_ball[1])
    path = bfs(grid, start, goal)
    if path is not None:
        shortest_path = path
        return shortest_path

    print("No path to goal: ", goal)

    return shortest_path

