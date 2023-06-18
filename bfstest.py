from Robot_Movement2 import bfs, create_grid
size=[1000,1000]
grid = create_grid(size)


values = bfs(grid,(1,1),(50,50))
print(values)