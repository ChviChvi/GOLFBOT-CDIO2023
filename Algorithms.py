from coordinate import Coordinate
from vertex import Vertex
from collections import deque


#Check if a ball is in the corner
#Returns true if the ball is in a corner
def ball_in_corner(ballcoordinates,max):
    # Check if the ball is placed in the 20 closest coordinates to the border.
    ball_in_corner = False
    if ((max.x - ballcoordinates.x) < 20 or ballcoordinates.x < 20) and ((max.y - ballcoordinates_y) < 20 or ballcoordinates_y < 20):
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


#BFS modified to use vertexclass
def bfs(graph, start ):
    visited = set()  # Set to keep track of visited nodes
    queue = deque([start])  # Initialize the queue with the start node
    start.parent = start

    while queue:
        node = queue.popleft()  # Get the next node from the front of the queue
        if node.value not in visited:
            visited.add(node.value)  # Mark the node as visited

            # Add the unvisited neighboring nodes to the queue
            neighbors = graph[node.y][node.x].neighbors
            for neighbor in neighbors:
                if neighbor.value not in visited:
                    queue.append(neighbor)
                    neighbor.parent = node
                

#Returns the path from ball to robot in coordinates
#Doesnt take edges or corners into account yet
#Prints the path 
def pathtoball( maxx, maxy , robot_coordinates,ball_coordinates, cross_coordinates):

    
    grid = []   # Create an empty list to store rows

    value=1
    for i in range(maxy):
        row = []  # Create a new list for each row
        for j in range(maxx):
            vertex = Vertex(value = value,parent = 0, neighbors = [], x = j, y = i )
            row.append(vertex)  # Populate the row with values
            value += 1
        grid.append(row)   # Add the row to the grid

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            neighbors = []

            if i > 0:
                neighbors.append(grid[i - 1][j])
            if i < len(grid) - 1:
                neighbors.append(grid[i + 1][j])
            if j > 0:
                neighbors.append(grid[i][j - 1])
            if j < len(grid[i]) - 1:
                neighbors.append(grid[i][j + 1])

            grid[i][j].neighbors = neighbors


    robot_vertex = grid[robot_coordinates.y][robot_coordinates.x]
    bfs( grid,robot_vertex)


    i = ball_coordinates.y-1
    j = ball_coordinates.x-1 
   
    t = 0
    while t<5 and grid[i][j].parent.value != robot_vertex.value:
        
        print("x: ", grid[i][j].parent.x, ", y: ", grid[i][j].parent.y)
        h=i
        k=j
        i = grid[h][k].parent.y
        j = grid[h][k].parent.x

       
#Testing
robotC=Coordinate(2,2)
ballC= Coordinate(7,5)
pathtoball(10,10,robotC,ballC)











