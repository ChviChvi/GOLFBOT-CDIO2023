

def danger_zone(grid, robot_position, ball_list, danger_distance=25):
    # Grid dimensions
    X, Y = grid

    # Robot position
    x, y = robot_position

    # Checking if robot is in the danger zone
    in_danger = x < danger_distance or y < danger_distance or X-x <= danger_distance or Y-y <= danger_distance

    # Filter the ball list to remove any that are within the danger zone
    new_ball_list = []
    for ball in ball_list:
        ball_x, ball_y = ball
        if (ball_x >= danger_distance and ball_y >= danger_distance and
            X-ball_x > danger_distance and Y-ball_y > danger_distance):
            new_ball_list.append(ball)

    return in_danger, new_ball_list


def Moving_back():

    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }

    key_state["backward"] = True

    return key_state
