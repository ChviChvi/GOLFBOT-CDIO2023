from coordinate import Coordinate


#Check if a ball is in the corner
#Returns true if the ball is in a corner
def ball_in_corner(ballcoordinates,max):
    # Check if the ball is placed in the 20 closest coordinates to the border.
    ball_in_corner = False
    if ((max.x - ballcoordinates.x) < 20 or ballcoordinates.x < 20) and
            ((max.y - ballcoordinates_y) < 20 or ballcoordinates_y < 20)):
        ball_in_corner = True
    else:
        ball_in_corner = False

    return ball_in_corner


#Check if a ball is in the cross
#Returns true if the ball is in the cross
def ball_in_cross(ball_coordinates, cross_coordinates):
    incross = False
    inx = False
    for Coordinate in cross_coordinates:
        if ball_coordinates.x == Coordinate.x:
            inx = True
    if inx:
        for Coordinate in cross_coordinates:
            if ball_coordinate.y == Coordinate.y:
                incross = True
    
    return incross


#Check to see to go horizontal or vertical first.
#Returns true if 
'''
def move_horizontal(ball_coordinates, cross_coordinates, robot_coordinates):
    move_horizontal = False
    xoverlap = False
    yoverlap = False
    for Coordinate in cross_coordinates:
        if robot_coordinates.x == Coordinate.x:
            xoverlap = True
        if robot_coordinates.y == Coordinate.y:
            yoverlap = True
    if 
'''

    











