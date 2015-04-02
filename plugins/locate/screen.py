import sys
import os
import pygame
import gui_objects
from time import strftime, localtime, time
from eztext import Input
from pygame.locals import K_RETURN, KEYDOWN
from global_variables import COLORS, ICONS, SCREEN_TIMEOUT, FONTS
from displayscreen import PiInfoScreen
from keyboard import VirtualKeyboard
from database import RACK_DB
sys.dont_write_bytecode = True


# For more information on the variables and functions in this file view
# displayscreen.py in the root folder of this project


class myScreen(PiInfoScreen):
    # PiInfoScreen.__init__()
    refreshtime = 1
    displaytime = 5
    pluginname = "File Accn"
    plugininfo = "place to file things. "
    accn = ''

    def __init__(self, *args, **kwargs):
        PiInfoScreen.__init__(self, args[0], kwargs)

        self.vkey_surface = pygame.display.get_surface()
        self.vkey = VirtualKeyboard(self.vkey_surface, self.color_name)

        self.timer = False
        self.timeout = 0
        self.timeout_delay =  5  # in seconds
        self.new_result = False
        self.dirty = True

        self.default_message = "scan to locate\nswipe up for keyboard"

        self.barcode_input = Input()
        RACK_DB.next_location()

        not_found =pygame.image.load(os.path.join(self.plugindir, 'resources', 'magoo.png'))

        self.screen_objects.remove(self.hint_text)
        del(self.hint_text)

        self.icon_font = pygame.font.Font(
            ICONS.font_location,
            50)  # keyboard font
        # This is the box where location results go
        result_rect = pygame.Rect(0, 95, 320, 115)
        result_surface = pygame.Surface(result_rect.size)
        self.result_text = gui_objects.textrect_image(
            string="",
            img = not_found,
            font=FONTS['swipe_font'],
            rect=result_rect,
            background_color=COLORS['CLOUD'],
            shrink=True,
            screen=result_surface)
        self.result_text.text_color = self.color
        self.result_text.margin['top'] = 3
        self.screen_objects.append(self.result_text)


        # # BOTTOM INFO BAR
        info1_rect = pygame.Rect(5, 205, 310, 20)
        info1_surface = pygame.Surface(info1_rect.size)
        self.info1 = gui_objects.render_textrect(
            string = '',
            font=self.fonts['info_font'],
            rect=info1_rect,
            background_color=COLORS['CLOUD'],
            screen=info1_surface)
        self.screen_objects.append(self.info1)

        for thing in self.screen_objects:
            thing.update()
        self.dirty = True

    def event_handler(self, event):
        evt_used = False
        accn = ''
        if event.type == SWIPE and event.value == 'up':
            self.dirty = True
            accn = self.vkey.run('')
            evt_used = True
        elif event.type == KEYDOWN and event.key == K_RETURN:
            accn = self.barcode_input.value
            self.barcode_input.value = ''
            evt_used = True
        else:
            evt_used = self.barcode_input.update(event)
        
        if accn != '':
            if len(accn) > 14:
                return False
            self.accn_box.update_string("Accn#: " + str(accn))
            self.timeout = time() + self.timeout_delay
            result = RACK_DB.find_accn(accn)
            if not result:
                # self.info0.update_string("Accn#: " + str(accn))
                self.result_text.toggle_screen()
                self.info1.update_string("Ohh Magoo, you've done it again!")
                self.info1.dirty = True
            else:
                # self.info0.update_string("Accn #: " + accn)
                if len(result) <= 4:
                    if len(result) == 1:
                        self.info1.update_string(str(
                            len(result)) + ' location found')
                    else:
                        self.info1.update_string(str(
                            len(result)) + ' locations found')
                    reversed_list = reversed(result)
                else:
                    self.info1.update_string("Showing last 6 locations")
                    reversed_list = reversed(result[-4:])
                formated = []
                for item in reversed_list:
                    formated.append(gui_objects.format_location(item))
                self.result_text.change_font(FONTS['mono'], self.color)
                self.result_text.update_string("\n".join(formated))
        return evt_used

    def exit_function(self):
        self.screen.fill(COLORS['CLOUD'])
        self.dirty = True

    def showScreen(self):
        tmstmp = strftime("%H:%M", localtime(time()))
        self.clock.update_string(tmstmp)
        if self.timeout < time():
            self.result_text.change_font(FONTS['swipe_font'], self.color)
            self.result_text.update_string('')
            self.accn_box.update_string('')
            self.info1.update_string('')
            self.result_text.update_string(self.default_message)
        self.refresh_objects()
        return self.screen
