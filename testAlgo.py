import heapq
import math

# current numbers are temporary and is for a 100x150 field with a dangerzone of 10
min_dist_dangerzone = 10
max_dist_dangerzone_x = 90
max_dist_dangerzone_y = 140

def distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_shortest_path(coordinates):
    start = coordinates[0]
    remaining = coordinates[1:]
    heap = [(0, start, remaining, [start])]
    heapq.heapify(heap)
    shortest_path = None

    while heap:
        cost, current, remaining, path = heapq.heappop(heap)
        if not remaining:
            if shortest_path is None or cost < shortest_path[0]:
                shortest_path = (cost, path)
        else:
            for next_coord in remaining:
                new_cost = cost + distance(current, next_coord)
                new_path = path + [next_coord]
                new_remaining = remaining[:]
                new_remaining.remove(next_coord)
                heapq.heappush(heap, (new_cost, next_coord, new_remaining, new_path))

    return shortest_path

#temp use. orange ball is always first coord
coordinates = [(10, 10), (2, 20), (40, 4), (3, 3)]
shortest_path = get_shortest_path(coordinates)

print("List of Coordinates:")
for coord in coordinates:
    print(coord)

print("\nShortest Path:")
for coord in shortest_path[1]:
    if coord[0] < min_dist_dangerzone or coord[1] < min_dist_dangerzone or coord[0] > max_dist_dangerzone_x or coord[1] > max_dist_dangerzone_y:
        print("zoned")
        print(coord)
    else:
        print(coord)
