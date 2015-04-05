import pygame
import sys
import os
import time
# import urllib2
import gui_objects
import eztext
from keyboard import VirtualKeyboard
from configobj import ConfigObj
from validate import Validator
from global_variables import COLORS, FONTS, PLUGIN_VALIDATOR, piscreenevents

from pprintpp import pprint
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class PiInfoScreen():

    # Set default names
    pluginname = "UNDEFINED"
    plugininfo = "You should set pluginname and plugininfo in your plugin subclass"
    # List of screen sizes supported by the script
    supportedsizes = [(320, 240)]

    # Refresh time = how often the data on the screen should be updated
    # (seconds)
    refreshtime = 30

    # How long screen should be displayed before moving on to next screen (seconds)
    # only relevant when screen is autmatically changing screens
    # rather than waiting for key press
    displaytime = 5
    loadingMessage = "Ummm?"

    # This function should not be overriden
    def __init__(self, screensize, scale=True, userevents=None):

        # Set config filepath...
        self.plugindir = os.path.dirname(
            sys.modules[self.__class__.__module__].__file__)
        self.banner_location = os.path.join(self.plugindir, 'resources', 'banner.png')
        self.configfile = os.path.join(self.plugindir, "config", "screen.ini")
        # ...and read the config file
        self.readConfig()
        # Save the requested screen size
        self.screensize = screensize
        self.userevents = userevents
        self.piscreenevents = piscreenevents
        # Check requested screen size is compatible and set supported property
        if screensize not in self.supportedsizes:
            self.supported = False
        else:
            self.supported = True
        self.dirty = True
        pygame.init()
        self.screen = pygame.display.set_mode(self.screensize).copy()
        self.surfacesize = self.supportedsizes[0]

        self.vkey_surface = pygame.display.get_surface()
        self.vkey = VirtualKeyboard(self.vkey_surface, self.color_name)
        self.vkey_screen = self.vkey.screen_copy

        title_rect = pygame.Rect(0, 25, 320, 70)
        title_surface = pygame.Surface(title_rect.size)
        self.title = gui_objects.render_textrect(
            string = self.name,
            font=FONTS['title_font'],
            rect=title_rect,
            background_color=self.color,
            screen=title_surface)

        hint_rect = pygame.Rect(0, 120, 320, 70)
        hint_surface = pygame.Surface(hint_rect.size)
        self.hint_text = gui_objects.render_textrect(
            string='',
            font=FONTS['swipe_font'],
            rect=hint_rect,
            background_color=COLORS['CLOUD'],
            shrink=True,
            screen=hint_surface)
        self.hint_text.text_color = self.color

        clock_rect = pygame.Rect(255, 0, 60, 25)
        clock_surface = pygame.Surface(clock_rect.size)
        self.clock = gui_objects.render_textrect(
            string = '',
            font=FONTS['input_font'],
            rect=clock_rect,
            background_color=COLORS['CLOUD'],
            h_align='right',
            v_align = 'center',
            screen=title_surface)

        accn_rect = pygame.Rect(5, 0, 250, 25)
        accn_surface = pygame.Surface(accn_rect.size)
        self.accn_box = gui_objects.render_textrect(
            string = '',
            font=FONTS['input_font'],
            rect=accn_rect,
            background_color=COLORS['CLOUD'],
            h_align = 'left',
            v_align = 'center',
            screen=accn_surface)

        self.screen_objects = [
            self.accn_box,
            self.clock,
            self.hint_text,
            self.title
            ]

    # Read the plugin's config file and dump contents to a dictionary
    def readConfig(self):
        validator = Validator()
        print self.configfile
        configspec = ConfigObj(PLUGIN_VALIDATOR, interpolation=False, list_values=True,
                       _inspec=True)
        self.pluginConfig = ConfigObj(self.configfile, configspec=configspec)
        result = self.pluginConfig.validate(validator)
        if result != True:
            print 'Config file validation failed!'

        self.setPluginVariables()

    # Can be overriden to allow plugin to change option type
    # Default method is to treat all options as strings
    # If option needs different type (bool, int, float) then this should be
    # done here
    # Alternatively, plugin can just read variables from the pluginConfig
    # dictionary that's created
    # Any other variables (colours, fonts etc.) should be defined here
    def setPluginVariables(self):

        self.name = self.pluginConfig["plugin_info"]["name"]
        self.color_name = self.pluginConfig["plugin_info"]["color"]
        self.shade = self.pluginConfig["plugin_info"]["shade"]
        self.color = COLORS[self.pluginConfig["plugin_info"]["color"]][self.shade]
        self.loadingMessage = self.pluginConfig[
            "plugin_info"]['loading_message']

        try:
            self.title_icon = self.pluginConfig['ui_settings']['title_icon']
        except:
            self.title_icon = 0xf058

        # create a dict with fonts defined in config/settings.ini
        self.fonts = {}
        for key in self.pluginConfig['fonts']:
            font = self.pluginConfig['fonts'][key]

            font_file = font['font']
            font_size = font['size']
            font_shade = font['shade']
            if 'trim' in font:
                font_trim = font['trim']
            else:
                font_trim = .9
            font_color = COLORS[font['color']][font_shade]

            font_location = os.path.join("resources/fonts", font_file)

            self.fonts[key] = {
                'font': pygame.font.Font(font_location, font_size),
                'color': font_color,
                'path': font_location,
                'trim': font_trim,
                'size': font_size}

    # Tells the main script that the plugin is compatible with the requested
    # screen size
    def supported(self):
        return self.supported

    # Returns the refresh time
    def refreshtime(self):
        return self.refreshtime

    # Returns the display time
    def displaytime(self):
        return self.displaytime

    # Returns a short description of the script
    # displayed when user requests list of installed plugins
    def showInfo(self):
        return self.plugininfo

    # Returns name of the plugin
    def screenName(self):
        return self.pluginname

    def loadingMessage():
        return self.loadingMessage

    # Handle button events
    # These should be overriden by screens if required

    def Button1Click(self):
        pass

    def Button2Click(self):
        pass

    def Button3Click(self):
        pass

    def Button4Click(self):
        pass


    def LoadImage(self, fileName, solid=False):
        image = pygame.image.load(fileName)
        image = image.convert()
        if not solid:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Draws a progress bar
    def showProgress(self, position, barsize,bordercolour, fillcolour, bgcolour):
        try:
            if position < 0:
                position = 0
            if position > 1:
                position = 1
        except:
            position = 0
        progress = pygame.Surface(barsize)
        pygame.draw.rect(progress, bgcolour, (0, 0, barsize[0], barsize[1]))
        progresswidth = int(barsize[0] * position)
        pygame.draw.rect(
            progress, fillcolour, (0, 0, progresswidth, barsize[1]))
        pygame.draw.rect(
            progress, bordercolour, (0, 0, barsize[0], barsize[1]), 1)
        return progress

    def exit_function(self):
        pass

    # Main function - returns screen to main script
    # Will be overriden by plugins
    # Defaults to showing name and description of plugin
    def showScreen(self):
        self.screen.fill([0, 0, 0])
        screentext = pygame.font.SysFont("freesans", 20).render(
            "%s: %s." % (self.pluginname, self.plugininfo), 1, (255, 255, 255))
        screenrect = screentext.get_rect()
        screenrect.centerx = self.screen.get_rect().centerx
        screenrect.centery = self.screen.get_rect().centery
        self.screen.blit(screentext, screenrect)

        return self.screen

    def refresh_objects(self):
        if self.dirty:
            print "full refresh"
            self.screen.fill(COLORS['CLOUD'])
            for thing in self.screen_objects:
                _screen = thing.get_screen()
                if _screen:
                    self.screen.blit(_screen, thing.rect)
        else:
            for thing in self.screen_objects:
                if thing.dirty:
                    _screen = thing.get_screen()
                    if _screen:
                        self.screen.blit(thing.get_screen(), thing.rect)
        self.dirty = False


    def event_handler(self, event):
        return False

    def setUpdateTimer(self):
        pass
