import os
import sys
import pygame
import fnmatch
import simplejson
from pprint import pprint
from configobj import ConfigObj
from parseIcons import icon
from validate import Validator
from sqlitedict import SqliteDict
from colors import red, green
from tabulate import tabulate
sys.dont_write_bytecode = True

# THIS SECTION IS TO READ THE CONFIG FILE
CONFIG_FILE = 'config/settings.ini'
CONFIG_SPEC = 'config/_config_validator.ini'
PLUGIN_VALIDATOR = 'config/_plugin_validator.ini'
MATERIAL_COLORS = 'material_colors.json'

RASPBERRYPI = False
# pprint(pygame.di`play.list_modes(), 3)
# Tell the RPi to use the TFT screen and that it's a touchscreen device
if os.name == 'posix':
    RASPBERRYPI = True
    from pitftgpio import PiTFT_GPIO
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    tftscreen = PiTFT_GPIO()


def TFTBtn1Click(channel):
    # test = yield tftscreen.presets
    tftscreen.set_backlight_brightness(tftscreen.presets.next())
    # tftscreen.backlight_off()


def TFTBtn2Click(channel):
    tftscreen.set_backlight_brightness(tftscreen.presets.next())
    # tftscreen.backlight_low()


def TFTBtn3Click(channel):
    pass
    # tftscreen.backlight_med()


def TFTBtn4Click(channel):
    # tftscreen.backlight_high()
    tftscreen.brightness


# This code needs work-------------------------------------
# Set up the four TFT button events
# Set up some custom events
TFTBUTTONCLICK = pygame.USEREVENT + 1
UPDATESCREEN = TFTBUTTONCLICK + 1
TOGGLE_FPS = UPDATESCREEN + 1
NEXTSCREEN = TOGGLE_FPS + 1
NEWSCREEN = NEXTSCREEN + 1
SLEEPEVENT = NEWSCREEN + 1
SWIPE = SLEEPEVENT + 1



click1event = pygame.event.Event(TFTBUTTONCLICK, button=1)
click2event = pygame.event.Event(TFTBUTTONCLICK, button=2)
click3event = pygame.event.Event(TFTBUTTONCLICK, button=3)
click4event = pygame.event.Event(TFTBUTTONCLICK, button=4)


# Set up the callback functions for the buttons
if RASPBERRYPI:
    tftscreen.Button1Interrupt(TFTBtn1Click)
    tftscreen.Button2Interrupt(TFTBtn2Click)
    tftscreen.Button3Interrupt(TFTBtn3Click)
    tftscreen.Button4Interrupt(TFTBtn4Click)

if RASPBERRYPI:
    tftscreen.backlight_high()


config_results = []
validator = Validator()
configspec = ConfigObj(
    CONFIG_SPEC,
    interpolation=False,
    list_values=True,
    _inspec=True)
_CONFIG = ConfigObj(CONFIG_FILE, configspec=configspec)
result = _CONFIG.validate(validator)
print "VALIDATING GLOBAL SETTINGS"
if not result:
    config_results.append([CONFIG_FILE, red('FAILED')])
    # print "-config/settings.ini " + red('FAILED ') + "validation"
    print tabulate(config_results)
    pprint(result)
else:
    print "-config/settings.ini " + green('PASSED ') + "validation"


configspec = ConfigObj(
    PLUGIN_VALIDATOR,
    interpolation=False,
    list_values=True,
    _inspec=True)
config_results = []
# PLUGIN_FILES = []
print "\nVALIDATING PLUGIN SETTINGS"
errors = []
for root, dirnames, filenames in os.walk('./'):
        # print filenames
    for filename in fnmatch.filter(filenames, 'screen.ini'):
        # PLUGIN_FILES.append(os.path.join(root, filename))
        _PLUGIN_CONFIG = ConfigObj(filename, configspec=configspec)
        result = _CONFIG.validate(validator)
        if not result:
            config_results.append([filename, red('FAILED')])
            errors.append(result)
        else:
            config_results.append([filename, green('PASSED')])

print tabulate(config_results)
# pprint(errors)


pygame.font.init()


# CLOCK_DIRTY = False


_COLORS = os.path.join('resources/', MATERIAL_COLORS)
_COLORS_FILE = open(_COLORS)
_JSON_COLORS = simplejson.load(_COLORS_FILE)
# pprint(_JSON_COLORS)
MATERIAL_COLORS = {}
for color in _JSON_COLORS:
    # pprint(COLORS)
    MATERIAL_COLORS[color] = {}
    for shade in _JSON_COLORS[color]:
        tmp = pygame.color.Color(str(_JSON_COLORS[color][shade]))
        # print tmp
        MATERIAL_COLORS[color][shade] = (tmp[0], tmp[1], tmp[2])
MATERIAL_COLORS['CLOUD'] = (236, 240, 241)
MATERIAL_COLORS['ASPHALT'] = (52, 73, 94)
COLORS = MATERIAL_COLORS


DEBUG = _CONFIG['settings']['debug']
FPS = _CONFIG['settings']['fps']
LOADING_TIME = _CONFIG['settings']['loading_time']
SHOW_FPS = True
TOGGLE_FPS_EVENT = pygame.event.Event(TOGGLE_FPS, value=True)

_bg_color = _CONFIG['app_info']['background_color']
_bg_shade = _CONFIG['app_info']['shade']
BACKGROUND_COLOR = COLORS[_bg_color][_bg_shade]


# THIS SECTION IS TO READ THE FONTS
FONTS = {}
for key in _CONFIG['fonts']:
    font = _CONFIG['fonts'][key]
    font_file = font['font']
    font_size = font['size']
    font_shade = font['shade']
    font_color = COLORS[font['color']][font_shade]
    font_location = os.path.join("resources/fonts", font_file)
    FONTS[key] = {
        'font': pygame.font.Font(font_location, font_size),
        'color': font_color,
        'path': font_location,
        'size': font_size}
    # pprint(FONTS)

# pprint(_CONFIG['title_banner'])
DATABASE_SETTINGS = {}
for key in _CONFIG['storage_settings']:
    DATABASE_SETTINGS[key] = _CONFIG['storage_settings'][key]

# Check if the banner needs to be redrawn
# then reset the value so the next load
# times are faster
# if not DEBUG:
    # REBUILD_BANNER = _CONFIG['title_banner']['REBUILD_BANNER']
    # if REBUILD_BANNER:
        # _CONFIG['title_banner']['REBUILD_BANNER'] = False
        # _CONFIG.write()
# else:
REBUILD_BANNER = True
SHADING_QUALITY = _CONFIG['title_banner']['SHADING_QUALITY']
BORDER = _CONFIG['title_banner']['BORDER']
CORNER_RADIUS = _CONFIG['title_banner']['CORNER_RADIUS']
SHADING_ITERATIONS = _CONFIG['title_banner']['SHADING_ITERATIONS']

BANNNER_ICON_SIZE = _CONFIG['title_banner']['BANNNER_ICON_SIZE']

SCREEN_TIMEOUT = _CONFIG['settings']['screen_timeout']

ROWS = {'1': 'A',
        '2': 'B',
        '3': 'C',
        '4': 'D',
        '5': 'E',
        '6': 'F',
        '7': 'G',
        '8': 'H',
        '9': 'I',
        '10': 'J',
        '11': 'K',
        '12': 'L'
        }

# TITLE_RECT = pygame.Rect(3, 30, 314, 60)
# these probably shouldnt be here
TITLE_RECT = pygame.Rect(0, 25, 320, 70)
SWIPE_HINT_RECT = pygame.Rect(0, 210, 320, 30)


# this is where the icon stuff is kept
ICON_FONT_FILE = 'pifile.ttf'
ICON_FONT_JSON = 'config.json'
ICONS = icon(ICON_FONT_JSON, ICON_FONT_FILE)


##################################
# SCREEN BANNER VARIABLES
###################################

LOADING_MESSEGES = []
TREKNOBABBLE = 'treknobabble.tbdb'

_TREKNOBABBLE = os.path.join('resources/', TREKNOBABBLE)
tb_db = SqliteDict(_TREKNOBABBLE)
# for item in dict_db.iteritems():
    # pprint(item)

for key, value in tb_db.iteritems():
    LOADING_MESSEGES.append(value)


# return_event = pygame.event.Event(RETURN_EVENT)

# Dict of events that are accessible to screens
piscreenevents = {
    "button": TFTBUTTONCLICK,
    "update": UPDATESCREEN,
    "nextscreen": NEXTSCREEN,
    "toggle_fps": TOGGLE_FPS_EVENT,
}
