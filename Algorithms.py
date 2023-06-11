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

    while queue:
        node = queue.popleft()  # Get the next node from the front of the queue
        if node.value not in visited:
            #grid[][].parent = node.value  # Process the node (in this example, we simply print it)
            visited.add(node.value)  # Mark the node as visited

            # Add the unvisited neighboring nodes to the queue
            neighbors = graph[node.y][node.x].neighbors
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    neighbor.parent = node


#Check to see to go horizontal or vertical first.
#Returns true if 
def move_horizontal( maxx, maxy , robot_coordinates):

    
    grid = []  # Create an empty list to store rows

    value=1
    for i in range(maxy):
        row = []  # Create a new list for each row
        for j in range(maxx):
            vertex = Vertex(value = value,parent = 0, neighbors = [], x = j, y = i )
            row.append(vertex)  # Populate the row with values
            value += 1
        grid.append(row)  # Add the row to the grid

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
   
    print(grid[1][2].parent.x)
    print(grid[1][2].parent.y)
    print(grid[1][2].x)
    print(grid[1][2].y)
    



robotC=Coordinate(2,3)

move_horizontal(4,8,robotC)











