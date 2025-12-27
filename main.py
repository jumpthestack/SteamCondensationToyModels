# A simulation of steam condensing into droplets on a flat surface.
#
# Real time animation is done with tkinter + pillow
# Exporting to video is done with moviepy
#
# Collision detection is outsourced to a custom module that partitions the plane
# into smaller squares to reduce the number of pairwise checks to perform. Besides
# this, very little optimization has been done.

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from moviepy import ImageSequenceClip
from graph import Graph, Edge
from collision import collidingPairs, Circle
from droplet import Droplet
import numpy as np
import random

# Set this switch to either show animation in real time or export to a video file
# False -> just show the animation
# True -> just export to video file
recording = False

# Canvas dimensions for displaying animation
canvasWidth = 800
canvasHeight = 400

# Set up moviepy frames for exporting to video file
frames = []
frameIndex = 0
durationMovieSeconds = 10
fps = 30
numFrames = durationMovieSeconds * fps
numMovies = 15
movieIndex = 0

# A factor for scaling up the canvas for better resolution in the output video
if recording:
    resolutionFactor = 2
else:
    resolutionFactor = 1

# Set up PIL image for drawing
img = Image.new('RGB', (canvasWidth*resolutionFactor, canvasHeight*resolutionFactor), '#303030')
draw = ImageDraw.Draw(img)

# Set up a tkinter window and canvas
root = tk.Tk()
root.title('Steam Condensation Simulation')
root.geometry(str(canvasWidth) + 'x' + str(canvasHeight))
canvas = tk.Canvas(root, width=canvasWidth, height=canvasHeight, bg='#303030')
canvas.pack()

# Draw a circle on the PIL image
def drawCircle(x, y, radius):
    x0 = x - radius
    y0 = y - radius
    x1 = x + radius
    y1 = y + radius
    draw.ellipse((x0*resolutionFactor, y0*resolutionFactor, x1*resolutionFactor, y1*resolutionFactor), fill='lightblue', outline='blue', width=1)

# Clear the PIL image
def resetImage():
    global img, draw
    img = Image.new('RGB', (canvasWidth*resolutionFactor, canvasHeight*resolutionFactor), '#303030')
    draw = ImageDraw.Draw(img)

# Show the PIL image on the tkinter canvas
def applyImageToCanvas():
    global img, canvas
    tkImg = ImageTk.PhotoImage(img.resize((canvasWidth, canvasHeight), Image.Resampling.LANCZOS))
    canvas.create_image(0, 0, anchor=tk.NW, image=tkImg)
    canvas.image = tkImg  # Keep a reference to avoid garbage collection

# A class for representing water droplets on a flat surface
class Droplet:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def volume(self):
      # Hemisphere volume formula
      return (1/2) * (4/3) * 3.14159 * self.radius ** 3

    def draw(self):
        drawCircle(self.x, self.y, self.radius)

    def centerOfMassWith(self, otherDroplet):
      totalVolume = self.volume() + otherDroplet.volume()
      x = (self.x * self.volume() + otherDroplet.x * otherDroplet.volume()) / totalVolume
      y = (self.y * self.volume() + otherDroplet.y * otherDroplet.volume()) / totalVolume
      return { 'x': x, 'y': y }

    # How two droplets coalesce
    def mergeWith(self, otherDroplet):
      totalVolume = self.volume() + otherDroplet.volume()
      newRadius = Droplet.volumeToRadius(totalVolume)
      newCenter = self.centerOfMassWith(otherDroplet)
      return Droplet(newCenter['x'], newCenter['y'], newRadius)

    @staticmethod
    def volumeToRadius(volume):
      # Inverse of hemisphere volume formula
      return (3 * volume / (2 * 3.14159)) ** (1/3)

    # How two or more droplets coalesce
    @staticmethod
    def mergeDroplets(dropletList):
      mergedDroplet = dropletList[0]
      for i in range(1, len(dropletList)):
        mergedDroplet = mergedDroplet.mergeWith(dropletList[i])
      return mergedDroplet

# The current set of droplets on the surface
droplets = set()

def addDroplet(x, y, radius):
    droplet = Droplet(x, y, radius)
    droplets.add(droplet)

def render():
    resetImage()
    for droplet in droplets:
        droplet.draw()
    if not recording:
        applyImageToCanvas()

def pairsInSet(set):
    arr = list(set)
    pairs = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            pairs.append((arr[i], arr[j]))
    return pairs

def step():
    # Declare the global variables
    global droplets

    # Add new droplets
    numNewDroplets = 400
    for i in range(numNewDroplets):
        x = random.random() * canvasWidth
        y = random.random() * canvasHeight
        addDroplet(x, y, 1)

    # Grow existing droplets
    for droplet in droplets:
        volume = droplet.volume()
        surfaceAreaGuidestick = droplet.radius ** 2  # This is proportional to surface area
        newVolume = volume + 0.1 * surfaceAreaGuidestick  # Growth in volume depends on surface area
        droplet.radius = Droplet.volumeToRadius(newVolume)

    # Check each pair of droplets to see if they should merge
    dropletArray = list(droplets)
    dropletCollidingPairs = collidingPairs(dropletArray, canvasWidth, canvasHeight)

    # Find all connected components of droplets to merge
    graph = Graph(0, [])
    for (d1, d2) in dropletCollidingPairs:
        graph = graph.addEdge(Edge(d1, d2))
    dropletsToMerge = graph.getNonSingletonConnectedComponents()

    # Merge droplets
    for dropletList in dropletsToMerge:
        newDroplet = Droplet.mergeDroplets(dropletList)
        droplets.add(newDroplet)
        for d in dropletList:
            droplets.discard(d)

def loop():
    global droplets, frames, frameIndex, img, movieIndex

    if recording:
        frames.append(np.array(img.resize((canvasWidth, canvasHeight), Image.Resampling.LANCZOS)))
        frameIndex += 1

        if (frameIndex >= numFrames):
            # Save the frames as a video using moviepy
            clip = ImageSequenceClip(frames, fps=fps)
            clip.write_videofile('steam_condensation_simulation_' + str(movieIndex) + '.mp4', codec="libx264")
            
            # Reset the frames and go to the next movie
            frameIndex = 0
            frames = []
            movieIndex += 1
            
            # Exit if all movies are completed
            if movieIndex >= numMovies:
                root.destroy()
                return  
            

    step()
    render()

    root.after(5, loop)

loop()

root.mainloop()