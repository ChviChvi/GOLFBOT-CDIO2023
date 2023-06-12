#Vertex class
class Vertex:
    def __init__(self, value, parent, neighbors,x,y):
        self.value = value
        self.parent = parent
        self.neighbors = neighbors
        self.x = x
        self.y = y