import pygame
from pprintpp import pprint
from global_variables import SWIPE

mouseDownTime = 0
mouseDownPos = (0, 0)
mouseUpPos = (0, 0)

minSwipe = 25

class swipe():
	def __init__(self):
		self.down_pos = None
		self.last_pos = None
		self.up_pos = None
		self.mouse_up = None
		self.mouse_down_time = None
		self.x_delta = 0
		self.y_delta = 0
		self.is_down = False
		self.last_swipe = None

	def set_down(self):
		print "pressed"
		self.down_pos = pygame.mouse.get_pos()
		self.last_pos = pygame.mouse.get_pos()
		self.last_swipe = None
		self.is_down = True

	def release(self):
		print "Released"
		self.up_pos = pygame.mouse.get_pos()
		self.last_pos = None
		self.is_down = False
		self.x_delta = 0
		self.y_delta = 0

	def delta(self):
		new_pos = pygame.mouse.get_pos()
		x_down, y_down = self.last_pos
		x_new, y_new = new_pos
		x = x_new - x_down
		y = y_new - y_down
		self.x_delta = x
		self.y_delta = y
		print y

	def event_handler(self, event):
		if (event.type == pygame.MOUSEBUTTONDOWN):
			self.set_down()
			return False
		if (event.type == pygame.MOUSEBUTTONUP):
			self.release()
			return self.swipe()
		if self.is_down:
			self.delta()
		return False

	def swipe(self):
		x_down, y_down = self.down_pos
		x_up, y_up = self.up_pos
		x = x_up - x_down
		y = y_up - y_down
		swipe = None
		if abs(x) < minSwipe and abs(y) < minSwipe:
		    return 0
		if abs(x) < abs(y):
		    if y > 0:
		        swipe = 'down'
		    if y < 0:
		        swipe = 'up'
		if abs(y) < abs(x):
		    if x > 0:
		        swipe = 'left'
		    if x < 0:
		        swipe = 'right'
		pygame.event.post(pygame.event.Event(SWIPE, value=swipe))
		self.last_swipe = swipe
		return swipe
