def danger_zone(grid, robot_position, ball_list, danger_percent=18):
    # Grid dimensions
    X, Y = grid

    # Calculate danger distance based on percentage
    danger_distance_x = X * (danger_percent / 100)
    danger_distance_y = Y * (danger_percent / 100)

    # Robot position
    x, y = robot_position

    # Ignore if the robot is outside of the grid
    if x < 0 or x >= X or y < 0 or y >= Y:
        return False, [], "Outside of grid"

    # Define danger zone flags
    danger_left = x < danger_distance_x
    danger_right = X-x <= danger_distance_x
    danger_up = y < danger_distance_y
    danger_down = Y-y <= danger_distance_y

    # Checking if robot is in the danger zone
    in_danger = danger_left or danger_right or danger_up or danger_down

    # Determine the danger zone
    if danger_up and danger_right:
        zone = "North East"
    elif danger_up and danger_left:
        zone = "North West"
    elif danger_down and danger_right:
        zone = "South East"
    elif danger_down and danger_left:
        zone = "South West"
    elif danger_up:
        zone = "North"
    elif danger_down:
        zone = "South"
    elif danger_right:
        zone = "East"
    elif danger_left:
        zone = "West"
    else:
        zone = "Safe"

    # Filter the ball list to remove any that are within the danger zone or outside the grid
    new_ball_list = []
    for ball in ball_list:
        if not isinstance(ball, (list, tuple)) or len(ball) != 2:
            continue
        ball_x, ball_y = ball
        if (ball_x >= 0 and ball_y >= 0 and
            ball_x < X and ball_y < Y and
            ball_x >= danger_distance_x and ball_y >= danger_distance_y and
            X-ball_x > danger_distance_x and Y-ball_y > danger_distance_y):
            new_ball_list.append(ball)

    return in_danger, new_ball_list, zone




def Turning1(zone, orientation):

    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }

    #print("BACKING - BEEP BEEP BACKING - BEEP BEEP")
    if zone is "West": # move West
        if 357 < orientation or orientation < 3:
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 180 < orientation < 357:
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 3 < orientation < 180:
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "East": # move East
        if 177 < orientation < 183:
            key_state["backward"] = True
            key_state["turn_left"] = False
            key_state["turn_right"] = False
        elif 0 < orientation < 177:
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 183 < orientation < 360:
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "South": # move South
        if 267 < orientation < 273:
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 90 < orientation < 267:
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 273 < orientation or orientation < 90: # Corrected
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "North": # move North
        if 87 < orientation < 93:
            key_state["backward"] = True
            key_state["turn_left"] = False
            key_state["turn_right"] = False
        elif orientation < 87 or orientation > 270: # Corrected
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 93 < orientation < 270: # Corrected
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "North West": # move Northwest
        if 315 < orientation < 360 or 0 <= orientation < 45:           
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 180 < orientation < 315:           
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 45 < orientation < 180:
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "South East": # move Southeast
        if 135 < orientation < 225:            
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 0 < orientation < 135:
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 225 < orientation < 360:
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "North East": # move Northeast
        if 45 < orientation < 135:            
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 0 <= orientation < 45:           
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 135 < orientation < 360:           
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    elif zone is "South West": # move Southwest
        if 225 < orientation < 315:
            key_state["turn_left"] = False
            key_state["turn_right"] = False
            key_state["backward"] = True
        elif 90 < orientation < 225:
            key_state["turn_left"] = False
            key_state["turn_right"] = True
        elif 315 < orientation or orientation < 90: # Corrected
            key_state["turn_left"] = True
            key_state["turn_right"] = False
    
    return key_state

def Turning(zone, orientation):
    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }
    
    # Move West
    if zone is "West":
        if 177 < orientation < 183:
            key_state["forward"] = True
        elif 357 < orientation or orientation < 3:
            key_state["backward"] = True
        elif 180 < orientation < 357:
            key_state["turn_right"] = True
        elif 3 < orientation < 180:
            key_state["turn_left"] = True
    
    # Move East
    elif zone is "East":
        if 357 < orientation or orientation < 3:
            key_state["forward"] = True
        elif 177 < orientation < 183:
            key_state["backward"] = True
        elif 0 < orientation < 177:
            key_state["turn_right"] = True
        elif 183 < orientation < 360:
            key_state["turn_left"] = True

    # Move South
    elif zone is "South":
        if 87 < orientation < 93:
            key_state["forward"] = True
        elif 267 < orientation < 273:
            key_state["backward"] = True
        elif 90 < orientation < 267:
            key_state["turn_right"] = True
        elif 273 < orientation or orientation < 90: # Corrected
            key_state["turn_left"] = True

    # Move North
    elif zone is "North":
        if 267 < orientation < 273:
            key_state["forward"] = True
        elif 87 < orientation < 93:
            key_state["backward"] = True
        elif orientation < 87 or orientation > 270: # Corrected
            key_state["turn_right"] = True
        elif 93 < orientation < 270: # Corrected
            key_state["turn_left"] = True
            
    # Move Northwest
    elif zone is "North West":
        if 225 < orientation < 315:
            key_state["forward"] = True
        elif 315 < orientation < 360 or 0 <= orientation < 45:           
            key_state["backward"] = True
        elif 180 < orientation < 315:           
            key_state["turn_right"] = True
        elif 45 < orientation < 180:
            key_state["turn_left"] = True
            
    # Move Southeast
    elif zone is "South East":
        if 45 < orientation < 135:
            key_state["forward"] = True
        elif 135 < orientation < 225:            
            key_state["backward"] = True
        elif 0 < orientation < 135:
            key_state["turn_right"] = True
        elif 225 < orientation < 360:
            key_state["turn_left"] = True
            
    # Move Northeast
    elif zone is "North East":
        if 315 < orientation or 0 <= orientation < 45:
            key_state["forward"] = True
        elif 45 < orientation < 135:            
            key_state["backward"] = True
        elif 0 <= orientation < 45:           
            key_state["turn_right"] = True
        elif 135 < orientation < 360:           
            key_state["turn_left"] = True
            
    # Move Southwest
    elif zone is "South West":
        if 135 < orientation < 225:
            key_state["forward"] = True
        elif 225 < orientation < 315:
            key_state["backward"] = True
        elif 90 < orientation < 225:
            key_state["turn_right"] = True
        elif 315 < orientation or orientation < 90: # Corrected
            key_state["turn_left"] = True
    
    return key_state


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
