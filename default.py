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

loading_font = pygame.font.Font(FONTS['swipe_font']['path'], 18)

def showWelcomeScreen():
    '''Display a temporary screen to show it's working
    May not display for long because of later code to show plugin loading
    '''
    pass
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
    sleep(LOADING_TIME)
    screen.fill(COLORS['CLOUD'])


def setNextScreen(event, screenindex):
    if event == 'left':
        a = 1
    elif event =='right':
        a = -1
    else:
        return screenindex
    '''Queues the next screen.'''
    pygame.event.post(pygame.event.Event(NEXTSCREEN))
    pluginScreens[screenindex].exit_function()

    screenindex += a
    if screenindex < 0:
        screenindex = len(pluginScreens) - 1
    if screenindex > len(pluginScreens) - 1:
        screenindex = 0

    return screenindex

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

pluginScreens = getScreens()

mouseDownTime = 0
mouseDownPos = (0, 0)
mouseUpPos = (0, 0)
# Mouse related variables
minSwipe = 30
maxClick = 10
longPressTime = 200


# Run our main loop
swype = swipe()

def mouse_down(event):
    print "mouse_down"
    screen_rect = screen.get_rect()
    global screenindex
    swype.event_handler(event)
    other_screen = 0
    while swype.is_down:
        for event in pygame.event.get():
            swype.event_handler(event)
        if not swype.is_down:
            continue

        delta_x = swype.x_delta
        delta_y = swype.y_delta
        print delta_x
        if abs(delta_x) > abs(delta_y):
            delta = delta_x
            last_delta = delta
            if delta > 0:
                other_screen = screenindex + 1
            if delta < 0:
                other_screen = screenindex - 1
            if other_screen < 0:
                other_screen = len(pluginScreens) - 1
            if other_screen > len(pluginScreens) - 1:
                other_screen = 0
            pluginScreens[screenindex].dirty = True
            screen_rect.left = delta
            screen.blit(pluginScreens[other_screen].screen, (0,0))
            tmp_screen = pluginScreens[screenindex].screen.copy()

            # tmp_screen.set_alpha(255-abs(delta_x)) 
            screen.blit(tmp_screen, screen_rect)
        else:
            screen.blit(pluginScreens[screenindex].screen, (0,0))
        update_display()
    print "Mouse Up?"
    if swype.last_swipe:
        print swype.last_swipe
        accel = 1.3
        if swype.last_swipe == 'left':
            while screen_rect.left < screen_rect.width:
                screen.blit(pluginScreens[other_screen].screen, (0,0))
                tmp_screen = pluginScreens[screenindex].screen.copy()
                tmp_screen.set_alpha(400-abs(screen_rect.left)) 
                screen.blit(tmp_screen, screen_rect)
                screen_rect.left *= accel
                # accel += 5
                update_display()
            screenindex = setNextScreen(swype.last_swipe, screenindex)
        if swype.last_swipe == 'right':
            while screen_rect.left > -screen_rect.width:
                screen.blit(pluginScreens[other_screen].screen, (0,0))
                tmp_screen = pluginScreens[screenindex].screen.copy()
                tmp_screen.set_alpha(400-abs(screen_rect.left)) 
                screen.blit(tmp_screen, screen_rect)
                screen_rect.left *= accel
                update_display()

            screenindex = setNextScreen(swype.last_swipe, screenindex)

        screen.blit(pluginScreens[screenindex].showScreen(), (0,0))
        update_display()
        mouseUpPos = pygame.mouse.get_pos()

def update_display():
    show_fps()
    # if SHOW_FPS:
        # show_fps()
    clock.tick(FPS)
    pygame.display.flip()

# pygame.event.set_blocked([1,4])
# pygame.event.set_blocked([1])
while not quit:
    for event in pygame.event.get():
        event_used = pluginScreens[screenindex].event_handler(event)
        if not event_used:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                quit = True
            if event.type == pygame.QUIT:
                quit = True
            if event.type == piscreenevents['toggle_fps'].type:
                SHOW_FPS = not SHOW_FPS
            if (event.type == pygame.MOUSEBUTTONDOWN):
                mouse_down(event)
            # if event.type == SWIPE:
                    # screenindex = setNextScreen(event, screenindex)

    screen.blit(pluginScreens[screenindex].showScreen(), (0,0))

    update_display()

pygame.quit()
sys.exit(0)
