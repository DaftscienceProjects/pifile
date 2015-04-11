import os
import pygame
import imp
import psutil
import random
import traceback
from swipe import swipe
from global_variables import *
from database import RACK_DB
from time import time, sleep
from keyboard import VirtualKeyboard
sys.dont_write_bytecode = True
from gui_objects import render_textrect
import types

debug = True
screensleep = 60000

pygame.init()
##############################################################################
# Create a clock and set max FPS (This reduces a lot CPU ussage)

# Screen size (currently fixed)
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
screen_rect = screen.get_rect()
pygame.mouse.set_visible(False if RASPBERRYPI else True)

clock = pygame.time.Clock()
screenindex = 0
stats_rect = pygame.Rect(228, 190, 90, 50)
stats_surface = pygame.Surface(stats_rect.size)

stats_surface2 = screen.subsurface(stats_rect)
stats_text = render_textrect(
    string="",
    font=FONTS['fps_font'],
    rect=stats_rect,
    h_align = 'left',
    background_color=COLORS['CLOUD'],
    screen = stats_surface)


cpu_pol = []
_cpu = ''
def show_fps():
    global cpu_pol, _cpu
    _mem = format(psutil.virtual_memory().percent, "3.2f")
    _fps = format(clock.get_fps(), "3.2f")
    if len(cpu_pol) < 10:
        cpu_pol.append(psutil.cpu_percent(interval=None))
    else:
        _cpu = format(sum(cpu_pol) / float(len(cpu_pol)), "3.2f")
        cpu_pol = []
    string =  'FPS:   ' +_fps + '\n' 
    string += 'CPU %: ' + _cpu + '\n'
    string += 'Mem %: ' + _mem

    stats_text.update_string(string)
    screen.blit(stats_text.get_screen(), stats_rect)

quit = False
d = 0
newscreen = False
newwait = 0


def log(message):
    '''Prints message if user has set debug flag to true.'''
    if debug:
        print message



def getPlugins():
    plugins = []
    keyboards = []
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
    plugins = []
    keyboards = []
    for plugin in getPlugins():
        plugin = loadPlugin(plugin)
        loadedscreen = plugin.myScreen(size, userevents=piscreenevents)
        plugins.append(loadedscreen)
        showLoadedPlugin(loadedscreen)

    for plugin in plugins:
        keyboards.append(plugin.vkey)
    return plugins, keyboards


loading_font = pygame.font.Font(FONTS['swipe_font']['path'], 18)

# def showWelcomeScreen():
    # '''Display a temporary screen to show it's working
    # May not display for long because of later code to show plugin loading
    # '''
    # pass
    # screen.fill(COLORS['CLOUD'])
    # label = loading_font.render(
        # "Initialising screens...",
        # 1,
        # COLORS['BLUE-GREY']['600'])
    # labelpos = label.get_rect()
    # labelpos.centerx = screen.get_rect().centerx
    # labelpos.centery = screen.get_rect().centery
    # screen.blit(label, labelpos)
    # pygame.display.flip()
    # sleep(2)

message_rect = screen.get_rect()
message_text = render_textrect(
    string="loading",
    font=FONTS['swipe_font'],
    rect=message_rect,
    background_color=COLORS['CLOUD'],
    justification=1,
    margin = (5,5),
    screen = screen)

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

    message_text.update_string(" ".join(tmp)) 
    message_text.text_color = plugin.color
    screen.blit(message_text.get_screen(), (0,0))
    pygame.display.flip()
    # sleep(LOADING_TIME)
    screen.fill(COLORS['CLOUD'])

def get_next_index(direction, screenindex):
    new_index = direction + screenindex
    if new_index < 0:
        new_index = len(pluginScreens) - 1
    if new_index > len(pluginScreens) - 1:
        new_index = 0
    return new_index

def showNewScreen():
    # '''Show the next screen.'''
    # pygame.time.set_timer(NEWSCREEN, 0)
    strttime = time()
    screen = pluginScreens[screenindex].showScreen()
    stptime = time()
    plugdiff = int((stptime - strttime) * 2000)
    pygame.display.flip()

#############################################################################



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

pluginScreens, keyboards = getScreens()



mouseDownTime = 0
mouseDownPos = (0, 0)
mouseUpPos = (0, 0)
# Mouse related variables
minSwipe = 30
maxClick = 10
longPressTime = 200


# Run our main loop
swype = swipe()

def mouse_down(event, index):
    screenindex = index
    swype.event_handler(event)
    other_screen = 0
    delta_y = 0
    delta_x = 0

    left = get_next_index(1, screenindex)
    right = get_next_index(-1, screenindex)

    left_screen = pluginScreens[left].screen
    right_screen = pluginScreens[right].screen
    current_screen = pluginScreens[screenindex].screen
    keyboard_screen = pluginScreens[screenindex].vkey_screen

    # while swype.is_down:
    while pygame.mouse.get_pressed()[0]:
        for event in pygame.event.get():
            swype.event_handler(event)
        if not swype.is_down: continue
        print "Finishing swipe motion"

        delta_x, delta_y = swype.delta
        # delta_y = swype.y_delta
        if abs(delta_x) > abs(delta_y):
            if delta_x > 0:
                screen.blit(left_screen, (-320+delta_x,0))
            else:
                screen.blit(right_screen, (320+delta_x,0))
            screen.blit(current_screen, (delta_x, 0))
        elif abs(delta_x) < abs(delta_y):
            if delta_y < 0:
                screen.blit(current_screen, (0, delta_y))
                screen.blit(keyboard_screen, (0, 240+delta_y))
        update_display()

    if swype.last_swipe:
        print swype.last_swipe
        # accel = 1.6
        if swype.last_swipe == 'left':
            while delta_x < 319:
                # print delta_x
                screen.blit(left_screen, (-320+delta_x,0))
                screen.blit(current_screen, (delta_x, 0))
                delta_x *= ANIMATION_SPEED
                update_display()
            screenindex = left
        if swype.last_swipe == 'right':
            while delta_x > - 319:
                # print delta_x
                screen.blit(right_screen, (320+delta_x,0))
                screen.blit(current_screen, (delta_x, 0))
                delta_x *= ANIMATION_SPEED
                update_display()
            screenindex = right
        if swype.last_swipe == 'up':
            while delta_y > - 239:
                screen.blit(current_screen, (0, delta_y))
                screen.blit(keyboard_screen, (0, 240+delta_y))
                delta_y *= ANIMATION_SPEED
                update_display()
            evnt = pygame.event.Event(SWIPE, value='up')
            pluginScreens[screenindex].event_handler(evnt)
    pygame.event.post(pygame.event.Event(NEWSCREEN, value=screenindex))
    return True if screenindex != index else False 

def update_display(fps=None):
    global SHOW_FPS
    if SHOW_FPS:
        show_fps()
    if fps:
        clock.tick(fps)
    else:
        clock.tick(FPS)
    pygame.display.flip()

while not quit:
    show_keyboard = False
    new_screen = False
    for event in pygame.event.get():
        if event.type == SWIPE and event.value == 'up':
            continue
        if pluginScreens[screenindex].event_handler(event):
            continue
        if event.type == pygame.QUIT:
            quit = True
        if event.type == piscreenevents['toggle_fps'].type:
            SHOW_FPS = not SHOW_FPS
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if event.button == 1:
                if mouse_down(event, screenindex):
                    new_screen = True
        if event.type == NEWSCREEN:
            screenindex = event.value
    if new_screen:
        new_screen = False
        continue
    screen.blit(pluginScreens[screenindex].showScreen(), (0,0))
    update_display()
pygame.quit()
sys.exit(0)
