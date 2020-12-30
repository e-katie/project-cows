import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from matplotlib import animation

import random

width = 1280
height = 720

class Scene:

	def __init__(self, ground_pos, canvas):
		self.canvas = canvas
		self.objects = []
		
		ground = mpatches.Rectangle(
			xy = (0, 0), 
			width = width,
			height = ground_pos,
			color = (0, 0.2, 0)
		)
		self.objects.append(ground)
		
		sky = mpatches.Rectangle(
			xy = (0, ground_pos), 
			width = width,
			height = height,
			color = (0.2, 0, 0.3)
		)
		self.objects.append(sky)

	def draw(self):
		for patch in self.objects:
			self.canvas.add_patch(patch)

class FlyingSaucer:

	def __init__(self, x, y, canvas):

		self.canvas = canvas
		
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.beamOn = False

		self.fs_width      = 180
		self.fs_height     = 80
		self.window_width  = 0.55
		self.window_height = 0.55
		self.base_height   = 0.4
		self.num_lights    = 10
		self.light_inc     = 15
		self.brightnesses  = []
		self.beamWidth     = 140

		for i in range(self.num_lights):
			self.brightnesses.append((i * self.light_inc * 2) % 255)

	def hover(self):
		self.x += random.uniform(-2,2)
		self.y += random.uniform(-2,2) 

	def update(self):
		self.x += self.vx
		self.y += self.vy

	def setVelocityX(self, vx):
		self.vx = vx

	def setVelocityY(self, vy):
		self.vy = vy

	def turnOnBeam(self):
		self.beamOn = True

	def turnOffBeam(self):
		self.beamOn = False

	def draw(self):

		patches = []
	
		if self.beamOn:
			patches.append(self.beam())
		
		# draw the window
		window = mpatches.Wedge(
			center = (self.x, self.y), 
			r	   = self.fs_height * self.window_height, 
			theta1 = 0, 
			theta2 = 180, 
			color  = (175/255,238/255,238/255)
		)
		patches.append(window)

		path = mpath.Path
		path_data = [
			(path.MOVETO,    [self.x - 0.5*self.fs_width,self.y]),
			(path.CURVE4,    [self.x - 0.25*self.fs_width,self.y - self.fs_height * self.base_height]),
			(path.CURVE4,    [self.x + 0.25*self.fs_width,self.y - self.fs_height * self.base_height]),
			(path.CURVE4,    [self.x + 0.5*self.fs_width,self.y]),
			(path.CLOSEPOLY, [self.x - 0.5*self.fs_width,self.y])
		]
		codes, verts = zip(*path_data)
		path = mpath.Path(verts, codes)
		bodyBottom = mpatches.PathPatch(path, color=(50/255,50/255,50/255))
		patches.append(bodyBottom)

		path = mpath.Path
		path_data = [
			(path.MOVETO,    [self.x - 0.5*self.fs_width,self.y]),
			(path.CURVE4,    [self.x - 0.25*self.fs_width,self.y + self.fs_height * self.base_height]),
			(path.CURVE4,    [self.x + 0.25*self.fs_width,self.y + self.fs_height * self.base_height]),
			(path.CURVE4,    [self.x + 0.5*self.fs_width,self.y]),
			(path.CLOSEPOLY, [self.x - 0.5*self.fs_width,self.y])
		]
		codes, verts = zip(*path_data)
		path = mpath.Path(verts, codes)
		bodyTop = mpatches.PathPatch(path, color=(150/255,150/255,150/255))
		patches.append(bodyTop)

		# draw the lights
		dist_between = self.fs_width/(self.num_lights - 1)

		for i in range(self.num_lights):
			x = self.x - self.fs_width/2 + i * dist_between
			light = mpatches.Circle(
				xy = (x, self.y),
				radius = 3,
				color = (
					self.brightnesses[i]/255, 
					self.brightnesses[i]/255, 
					0
				)
			)
			self.brightnesses[i] += self.light_inc
			if self.brightnesses[i] > 255:
				self.brightnesses[i] = 180

			patches.append(light)

		for patch in patches:
			self.canvas.add_patch(patch)

	def beam(self):
		path = mpath.Path
		path_data = [
			(path.MOVETO,    [self.x - 25,self.y + self.fs_height * self.base_height * 0.5]),
			(path.LINETO,    [self.x + 25,self.y + self.fs_height * self.base_height * 0.5]),
			(path.LINETO,    [self.x + self.beamWidth/2,100]),
			(path.LINETO,    [self.x - self.beamWidth/2,100]),
			(path.CLOSEPOLY, [self.x - 25,self.y + self.fs_height * self.base_height * 0.5]),
		]
		codes, verts = zip(*path_data)
		path = mpath.Path(verts, codes)
		patch = mpatches.PathPatch(path, color=(1,1,100/255,100/255), lw=0)
		return patch

	def getBeamBoundaries(self):
		boundaries = []
		boundaries.append(self.x - self.beamWidth/2)
		boundaries.append(self.x + self.beamWidth/2)
		return boundaries

class Cow:

	def __init__(self, x, y, canvas):

		self.canvas = canvas

		self.x = x
		self.y = y
		self.direction = random.randint(2,4)
		self.flyingSaucerRef = None
		self.flagForDeletion = False
		self.isFrozen = False

		self.step = 0

		if random.uniform(0., 1.) > 0.5:
			self.direction *= -1

	def draw(self):
		patches = []
		# body
		body = mpatches.Rectangle(
			xy = (self.x, self.y + 5), 
			width = 10,
			height = 5,
			color = (1, 250/255, 240/255)
		)
		patches.append(body)
		# legs
		leg1 = None
		leg2 = None
		if self.step > 2:
			leg1 = mpatches.Rectangle(
				xy = (self.x, self.y), 
				width = 2,
				height = 5,
				color = (1, 250/255, 240/255)
			)
			leg2 = mpatches.Rectangle(
				xy = (self.x + 8, self.y), 
				width = 2,
				height = 5,
				color = (1, 250/255, 240/255)
			)
		else:
			leg1 = mpatches.Rectangle(
				xy = (self.x + 2, self.y), 
				width = 2,
				height = 5,
				color = (1, 250/255, 240/255)
			)
			leg2 = mpatches.Rectangle(
				xy = (self.x + 6, self.y), 
				width = 2,
				height = 5,
				color = (1, 250/255, 240/255)
			)
		patches.append(leg1)
		patches.append(leg2)
		# head
		head = None
		if self.direction > 0:
			head = mpatches.Rectangle(
				xy = (self.x + 10, self.y + 8), 
				width = 4,
				height = 4,
				color = (1, 250/255, 240/255)
			)
		else:
			head = mpatches.Rectangle(
				xy = (self.x - 4, self.y + 8), 
				width = 4,
				height = 4,
				color = (1, 250/255, 240/255)
			)
		patches.append(head)
		# markings
		mark1 = mpatches.Rectangle(
			xy = (self.x + 5, self.y + 6), 
			width = 3,
			height = 3,
			color = (0, 0, 0)
		)
		mark2 = mpatches.Rectangle(
			xy = (self.x + 2, self.y + 7), 
			width = 1,
			height = 1,
			color = (0, 0, 0)
		)
		patches.append(mark1)
		patches.append(mark2)
		for patch in patches:
			self.canvas.add_patch(patch)
		
	def walk(self):
		self.x += self.direction
		self.step = (self.step + 1) % 6

class CowManager:

	def __init__(self, cowsNum, canvas):
		self.canvas = canvas
		self.cows = []
		self.cowsNum = cowsNum

		# initial cows
		for i in range(cowsNum):
			self.cows.append(Cow(random.randint(0, width), 100, self.canvas))

	def update(self):
		# add new cows if necessary
		if len(self.cows) < self.cowsNum:
			self.cows.append(Cow(width + 99, 100, self.canvas))
		
		for cow in self.cows:
			if not cow.isFrozen:
				if cow.y > 100:
					# falling
					cow.y -= 8
				else:
					cow.y = 100
					# regular walking
					cow.walk()

					if cow.x > width + 100:
						cow.x = -100

					elif cow.x < -100:
						cow.x = width + 100
			else:
				# reset for next frame
				cow.isFrozen = False
		
		# remove old cows
		i = len(self.cows) - 1
		while i >= 0:
			if self.cows[i].flagForDeletion:
				self.cows.pop(i)
			i -= 1

	def draw(self):
		for cow in self.cows:
			cow.draw()

	def checkForCows(self, x1, x2):
		# returns all cows between the two points
		cows = []
		for cow in self.cows:
			if cow.x >= x1 and cow.x <= x2:
				cows.append(cow)
		return cows
	
	def levitateCows(self, boundaries, x_anchor, y_cutoff):
		cows = self.checkForCows(boundaries[0], boundaries[1])
		# hover up
		for cow in cows:
			cow.x = x_anchor
			cow.y += 4
			cow.isFrozen = True
			
			if cow.y > y_cutoff:
				cow.flagForDeletion = True


fig, ax = plt.subplots()

scene = Scene(
	ground_pos = 100, 
	canvas     = ax
)
fs = FlyingSaucer(
	x      = 200, 
	y      = 600,
	canvas = ax
)
cowManager = CowManager(
	cowsNum = 10,
	canvas  = ax
)

def press(event):
	if event.key == 'left':
		fs.turnOffBeam()
		fs.setVelocityX(-5)
		fs.setVelocityY(0)
	if event.key == 'right':
		fs.turnOffBeam()
		fs.setVelocityX(5)
		fs.setVelocityY(0)
	if event.key == 'up':
		fs.turnOffBeam()
		fs.setVelocityX(0)
		fs.setVelocityY(5)
	if event.key == 'down':
		fs.turnOffBeam()
		fs.setVelocityX(0)
		fs.setVelocityY(-5)
	if event.key == ' ' and fs.beamOn:
		fs.setVelocityX(0)
		fs.setVelocityY(0)
		fs.turnOffBeam()
	elif event.key == ' ' and not fs.beamOn:
		fs.setVelocityX(0)
		fs.setVelocityY(0)
		fs.turnOnBeam()

fig.canvas.mpl_connect('key_press_event', press)

def draw(nextFrame):

	ax.clear()
	ax.set_xlim(0, width)
	ax.set_ylim(0, height)

	scene.draw()
	
	cowManager.update()
	cowManager.draw()
	
	fs.update()
	fs.hover()
	fs.draw()
	
	if fs.beamOn:
		bounds = fs.getBeamBoundaries()
		cowManager.levitateCows(bounds, fs.x, fs.y)

	ax.axis('off')

ani = animation.FuncAnimation(
	fig, draw, frames=1000, interval=1
)
plt.tight_layout()
plt.show()
