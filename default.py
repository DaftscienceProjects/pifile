import subprocess
try:
    subprocess.call('pip install -r requirements.txt', shell=True)
except:
    print "unable to install requirements"

import os
import pygame
import imp
import psutil
import random
import traceback
from global_variables import *
from database import RACK_DB
from time import time, sleep
from keyboard import VirtualKeyboard
sys.dont_write_bytecode = True
from gui_objects import render_textrect
import types

# modulenames = set(sys.modules)&set(globals())
# allmodules = [name for name in modulenames]
# for thing in allmodules:
#     pprint(thing)
# # import sys


debug = True
screensleep = 60000

# This is where we start
# Initialise pygame

pygame.init()
##############################################################################
# Create a clock and set max FPS (This reduces a lot CPU ussage)

# Screen size (currently fixed)
size = width, height = 320, 240
screen = pygame.display.set_mode(size)

pygame.mouse.set_visible(False if RASPBERRYPI else True)



clock = pygame.time.Clock()
screenindex = 0
stats_rect = pygame.Rect(228, 190, 90, 50)
stats_surface = screen.subsurface(stats_rect)

stats_text = render_textrect(
    string="",
    font=FONTS['fps_font']['font'],
    rect=stats_rect,
    text_color=FONTS['fps_font']['color'],
    background_color=COLORS['CLOUD'],
    justification=0,
    FontPath=FONTS['fps_font']['path'],
    cutoff=True,
    # margin = (5,5),
    MinFont=FONTS['fps_font']['size'] - 4,
    MaxFont=FONTS['fps_font']['size'],
    shrink=False,
    vjustification=0)

cpu_pol = []
_cpu = ''
def show_fps():
    global cpu_pol, _cpu
    _mem = format(psutil.virtual_memory().percent, "3.2f")
    _fps = format(clock.get_fps(), "3.2f")
    if len(cpu_pol) < 20:
        cpu_pol.append(psutil.cpu_percent(interval=None))
    else:
        _cpu = format(sum(cpu_pol) / float(len(cpu_pol)), "3.2f")
        cpu_pol = []
    
    stats_text.string = "FPS: "+_fps + '  \n' 
    stats_text.string += 'CPU: ' + _cpu + ' %\n'
    stats_text.string += 'Mem: ' + _mem + ' %'
    # fps_img = FONTS['fps_font']['font'].render(_fps, 1, FONTS['fps_font']['color'])
    stats_surface.blit(stats_text.update(), (0,0))

quit = False
# b = pygame.time.get_ticks()
d = 0
newscreen = False
newwait = 0
# refresh = 60000
# refreshNow = False
# SWIPE_TO_SCREEN = 0
# CURRENT_SCREEN = -1


def log(message):
    '''Prints message if user has set debug flag to true.'''
    if debug:
        print message

# ##############################################################################
# Plugin handling code adapted from:
# http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
# THANK YOU!
# # ######################################################################


def getPlugins():
    plugins = []
    possibleplugins = os.listdir(PluginFolder)
    a = 1
    for i in possibleplugins:
        location = os.path.join(PluginFolder, i)
        if not os.path.isdir(
                location) or PluginScript not in os.listdir(location):
            continue
        inf = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": inf, "id": a})
        a = a + 1
    return plugins

def loadPlugin(plugin):
    return imp.load_module(MainModule, *plugin["info"])
##############################################################################

##############################################################################
# Initialise plugin screens

def getScreens():
    '''Gets list of available plugin screen objects.'''
    a = []
    for i in getPlugins():
        plugin = loadPlugin(i)
        try:
            # The plugin should have the myScreen function
            # We send the screen size for future proofing (i.e. plugins should
            # be able to cater for various screen resolutions
            #
            # TO DO: Work out whether plugin can return more than one screen!
            loadedscreen = plugin.myScreen(size, userevents=piscreenevents)
            a.append(loadedscreen)
            showLoadedPlugin(loadedscreen)

        except:
            # If it doesn't work, ignore that plugin and move on
            log(traceback.format_exc())
            continue
    return a
##############################################################################


##############################################################################
# Event handling methods
# def setUpdateTimer(pluginloadtime):
    # ''' Sets an update timer
    # Depending on the speed of the processor, the timer
    # can flood the event queue with UPDATE events but
    # if the plugin takes a while to load there may be no time for
    # anything else.
    # This function provides some headroom in the timer
    # '''
    # interval = max(5 * pluginloadtime, pluginScreens[screenindex].refreshtime)

    # pygame.time.set_timer(UPDATESCREEN, 0)
    # pygame.time.set_timer(UPDATESCREEN, interval)

loading_font = pygame.font.Font(FONTS['swipe_font']['path'], 18)


def showWelcomeScreen():
    '''Display a temporary screen to show it's working
    May not display for long because of later code to show plugin loading
    '''
    screen.fill(COLORS['CLOUD'])
    label = loading_font.render(
        "Initialising screens...",
        1,
        COLORS['BLUE-GREY']['600'])
    labelpos = label.get_rect()
    labelpos.centerx = screen.get_rect().centerx
    labelpos.centery = screen.get_rect().centery
    screen.blit(label, labelpos)
    pygame.display.flip()
    # pass
    # sleep(.5)



message_rect = screen.get_rect()
message_text = render_textrect(
    string="loading",
    font=loading_font,
    rect=message_rect,
    text_color=COLORS['CLOUD'],
    background_color=COLORS['CLOUD'],
    justification=1,
    FontPath=FONTS['swipe_font']['path'],
    cutoff=False,
    margin = (5,5),
    MinFont=FONTS['swipe_font']['size'] - 4,
    MaxFont=FONTS['swipe_font']['size'],
    shrink=True,
    vjustification=1)

def showLoadedPlugin(plugin):
    '''Display a temporary screen to show when a module is successfully
    loaded.
    '''
    found = False
    message = ''
    while not found:
        message = random.choice(LOADING_MESSEGES)
        if 'bomb' not in message:
            found = True
    LOADING_MESSEGES.remove(message)

    tmp = message.split(' ', -1)
    first_word = tmp[1]
    if not first_word.endswith('e'):
        first_word += 'ing'
    else:
        first_word = tmp[1][:-1] + 'ing'
    tmp[1] = first_word

    message_text.string = " ".join(tmp)
    message_text.text_color = plugin.color
    screen.blit(message_text.update(), (0,0))
    pygame.display.flip()
    sleep(LOADING_TIME)


def setNextScreen(a, screenindex):
    '''Queues the next screen.'''
    # pygame.time.set_timer(NEWSCREEN, 0)
    # pygame.time.set_timer(UPDATESCREEN, 0)
    pygame.event.post(pygame.event.Event(NEXTSCREEN))

    screenindex += a
    if screenindex < 0:
        screenindex = len(pluginScreens) - 1
    if screenindex > len(pluginScreens) - 1:
        screenindex = 0

    displayLoadingScreen(screenindex)
    return screenindex


def displayLoadingScreen(a):
    pass


def showNewScreen():
    # '''Show the next screen.'''
    # pygame.time.set_timer(NEWSCREEN, 0)
    strttime = time()
    screen = pluginScreens[screenindex].showScreen()
    stptime = time()
    plugdiff = int((stptime - strttime) * 2000)
    # print plugdiff
    # setUpdateTimer(plugdiff)
    pygame.display.flip()

#############################################################################


def longPress(downTime):
    if pygame.time.get_ticks() - longPressTime > downTime:
        return True
    else:
        return False


# Initialise screen object
# if RASPBERRYPI:
#     tftscreen = PiTFT_GPIO()
# Plugin location and names
PluginFolder = "./plugins"
PluginScript = "screen.py"
MainModule = "screen"
pluginScreens = []



# Set our screen size
# Should this detect attached display automatically?


# Set ner (useful for testing, not so much for full screen mode!)
pygame.display.set_caption("Info screen")

# Stop keys repeating
pygame.key.set_repeat()

pluginScreens = getScreens()

mouseDownTime = 0
mouseDownPos = (0, 0)
mouseUpPos = (0, 0)
# Mouse related variables
minSwipe = 30
maxClick = 10
longPressTime = 200


# Function to detect swipes
# -1 is that it was not detected as a swipe or click
# It will return 1 , 2 for horizontal swipe
# If the swipe is vertical will return 3, 4
# If it was a click it will return 0
def getSwipeType():
    x_down, y_down = mouseDownPos
    x_up, y_up = mouseUpPos
    x = x_up - x_down
    y = y_up - y_down
    swipe = 0

    if abs(x) < minSwipe and abs(y) < minSwipe:
        return 0
    if abs(x) < abs(y):
        if y > 0:
            return 3
        if y < 0:
            return 4
    if abs(y) < abs(x):
        if x > 0:
            return 1
        if x < 0:
            return 2
    return 0


def longPress(downTime):
    if pygame.time.get_ticks() - longPressTime > downTime:
        return True
    else:
        return False


# Queue the first screen
displayLoadingScreen(screenindex)

# Run our main loop
while not quit:
    for event in pygame.event.get():
        # print event.type
        # Handle quit message received
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            quit = True
        # RACK_DB.list_all()
        if event.type == pygame.QUIT:
            quit = True
        # mouse button pressed
        if event.type == piscreenevents['toggle_fps'].type:
            SHOW_FPS = not SHOW_FPS
        if (event.type == pygame.MOUSEBUTTONDOWN):
            mouseDownTime = pygame.time.get_ticks()
            mouseDownPos = pygame.mouse.get_pos()
            # pygame.mouse.get_rel()
        if (event.type == pygame.MOUSEBUTTONUP):
            mouseUpPos = pygame.mouse.get_pos()
            swipe = getSwipeType()
            # print "Screen Index Before: " + str(screenindex)
            if swipe == 1:
                pluginScreens[screenindex].exit_function()
                screenindex = setNextScreen(1, screenindex)
                continue
            elif swipe == 2:
                pluginScreens[screenindex].exit_function()
                screenindex = setNextScreen(-1, screenindex)
                # clock = pygame.time.Clock()
                continue
            elif swipe == 3:
                pluginScreens[screenindex].exit_function()
                tmp_event = pygame.event.Event(SWIPE_DOWN, value=1)
                pluginScreens[screenindex].event_handler(tmp_event)
                continue
                # quit = True
                # continue
            elif swipe == 4:
                # vkey = VirtualKeyboard(screen)
                # tmp = vkey.run('')
                pluginScreens[screenindex].exit_function()
                tmp_event = pygame.event.Event(SWIPE_UP, value=1)
                pluginScreens[screenindex].event_handler(tmp_event)
                continue
            # print "Screen Index After: " + str(screenindex)
        if (event.type == TFTBUTTONCLICK):
            if (event.button == 1):
                pluginScreens[a].Button1Click()
            if (event.button == 2):
                pluginScreens[a].Button2Click()
            if (event.button == 3):
                pluginScreens[a].Button3Click()
            if (event.button == 4):
                pluginScreens[a].Button4Click()
        if (event.type == NEWSCREEN):
            showNewScreen()
        pluginScreens[screenindex].event_handler(event)

    screen = pluginScreens[screenindex].showScreen()

    if SHOW_FPS:
        show_fps()
    clock.tick(FPS)
    # clock.tick()
    pygame.display.flip()

# If we're here we've exited the display loop...
log("Exiting...")
pygame.quit()
sys.exit(0)
