import pygame
import time
import os
from swipe import swipe
from global_variables import COLORS, ICONS, ICON_FONT_FILE, FONTS, FPS
from pygame.locals import *
from sunquest import *



from string import maketrans
Uppercase = maketrans("7894561230",
                      'SMTWHF X  ')

clock = pygame.time.Clock()
DEBUG = False
swype = swipe()



class VirtualKeyboard():
	def __init__(self, screen, color, validate=True, parent=None):
		