# A collision detector for a collection of circles in a rectangular area.
#
# Rough sketch of collision detection:
# Divide the area into a grid of smaller squares, and use this to bin the circles. 
# Then sort the circles from largest to smallest, and iterate through the list, 
# searching for collisions. For a given circle, if all collisions with larger circles
# have already been found, it is easy to compute which grid cells can contain new collisions.
# Dynamically recompute the grid cell size when the circles become much smaller.

import math

class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

class Grid:
    def __init__(self, width, height, gridSquareWidth):
        self.width = width
        self.height = height
        self.gridSquareWidth = gridSquareWidth
        self.numGridCols = math.ceil(width / gridSquareWidth)
        self.numGridRows = math.ceil(height / gridSquareWidth)
        self.grid = [[[] for _ in range(self.numGridCols)] for _ in range(self.numGridRows)]

    def get(self, row, col):
        return self.grid[row][col]

    def set(self, row, col, value):
        self.grid[row][col] = value

    def push(self, row, col, value):
        self.grid[row][col].append(value)

    def positionToGridCell(self, x, y):
        col = max(0, min(self.numGridCols-1, math.floor(x / self.gridSquareWidth)))
        row = max(0, min(self.numGridRows-1, math.floor(y / self.gridSquareWidth)))
        return [row, col]

# Bin the circles into grid cells
def initializeGrid(circles, width, height, gridSquareWidth):
    grid = Grid(width, height, gridSquareWidth)

    for circle in circles:
        [gridRow, gridCol] = grid.positionToGridCell(circle.x, circle.y)
        grid.push(gridRow, gridCol, circle)

    return grid

# Find the collisions
def collidingPairs(circles, width, height):
    if len(circles) == 0:
        return []

    colliding = []
    circlesSortedByRadius = circles.copy()
    circlesSortedByRadius.sort(reverse=True, key=lambda c: c.radius)
    maxRadius = circlesSortedByRadius[0].radius
    halfMaxRadius = maxRadius / 2

    gridSquareWidth = 2*maxRadius
    grid = initializeGrid(circlesSortedByRadius, width, height, gridSquareWidth)

    doneCircles = set()

    for circleIndex in range(len(circlesSortedByRadius)):
        circle = circlesSortedByRadius[circleIndex]

        while circle.radius < halfMaxRadius:
            maxRadius = circle.radius
            halfMaxRadius = maxRadius / 2
            gridSquareWidth = maxRadius
            grid = initializeGrid(circlesSortedByRadius[circleIndex:], width, height, gridSquareWidth)

        [minGridRow, minGridCol] = grid.positionToGridCell(
            circle.x - 2*circle.radius,
            circle.y - 2*circle.radius
        )

        [maxGridRow, maxGridCol] = grid.positionToGridCell(
            circle.x + 2*circle.radius,
            circle.y + 2*circle.radius
        )

        for r in range(minGridRow, maxGridRow + 1):
            for c in range(minGridCol, maxGridCol + 1):
                for otherCircle in grid.get(r, c):
                    if (otherCircle == circle or otherCircle in doneCircles): continue
                    dx = circle.x - otherCircle.x
                    dy = circle.y - otherCircle.y
                    distanceSq = dx * dx + dy * dy
                    radiusSum = circle.radius + otherCircle.radius
                    if distanceSq < radiusSum * radiusSum:
                        colliding.append([circle, otherCircle])
        doneCircles.add(circle)
    return colliding
