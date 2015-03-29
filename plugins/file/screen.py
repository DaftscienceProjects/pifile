import sys
import pygame
import os
import gui_objects
from pprint import pprint
from time import strftime, localtime
from eztext import Input
from pygame.locals import K_RETURN, KEYDOWN
from multi_font_text import multi_font
from global_variables import COLORS, SWIPE, ICONS, TITLE_RECT, DATABASE_SETTINGS, ROWS, piscreenevents
from displayscreen import PiInfoScreen
from keyboard import VirtualKeyboard
from database import RACK_DB
sys.dont_write_bytecode = True


# For more information on the variables and functions in this file view
# displayscreen.py in the root folder of this project


class myScreen(PiInfoScreen):
    refreshtime = 1
    displaytime = 5
    pluginname = "File Accn"
    plugininfo = "place to file things. "
    accn = ''

    def __init__(self, *args, **kwargs):
        PiInfoScreen.__init__(self, args[0], kwargs)
        self.vkey_surface = pygame.display.get_surface()
        self.vkey = VirtualKeyboard(self.vkey_surface, self.color_name)

        self.screen.fill(COLORS['CLOUD'])
        self.hint_text.update_string("scan to store\nswipe up for keyboard")
        if RACK_DB.last_filed:
            self.accn_box.update_text("Last Filed: " + RACK_DB.last_filed['accn'])
        else:
            self.accn_box.update_text("Unavailable")
        # self.accn_box.text =  "Last Filed: #: " + accn

        self.barcode_input = Input()
        info0_text = "Next Location: "
        info0_size = self.fonts['default_font'][
            'font'].render(info0_text, 1, (0, 0, 0))
        w = info0_size.get_rect().width

        # self.title.update()


        self.info0_rect = pygame.Rect(5, 95, w, 25)
        self.info0_surface = pygame.Surface(self.info0_rect.size)
        self.info0 = gui_objects.text_label(
            surface=self.info0_surface,
            font=self.fonts['default_font']['font'],
            text=info0_text,
            color=self.fonts['default_font']['color'],
            # Rect(left, top, width, height) -> Rect
            rect=self.info0_rect,
            valign='bottom',
            align="left",
            background_color=COLORS['CLOUD'])
        # self.info0.update()
        self.screen_objects['info0'] = {
                'object': self.info0, 
                'surface': self.info0_surface, 
                'rect': self.info0_rect,
                'dirty': True
                }

        # ------------------------------------------
        # These information labels will change when the screen is updated
        # They will need to be updated
        #----------------------------------------
        self.info2_rect = pygame.Rect(0, 95, 100, 25)
        self.info2_rect.left = self.info0_rect.right + 1
        self.info2_surface = pygame.Surface(self.info2_rect.size)
        self.info2 = gui_objects.text_label(
            surface=self.info2_surface,
            font=self.fonts['default_font']['font'],
            text="Unavailable Location",
            color=self.fonts['info_font']['color'],
            rect=self.info2_rect,
            valign='bottom',
            align="left",
            background_color=COLORS['CLOUD'])
        self.screen_objects['info2'] = {
                'object': self.info2, 
                'surface': self.info2_surface, 
                'rect': self.info2_rect,
                'dirty': True
                }



        # location dots!
        self.empty_dot = ICONS.unicode('checkbox-blank-circle-outline')
        self.full_dot = ICONS.unicode('checkbox-blank-circle')
        self.select_dot = ICONS.unicode('plus-circled')

        self.location_indicator_rect = pygame.Rect(0, 200, 320, 35)
        self.location_indicator_surface = pygame.Surface(
            self.location_indicator_rect.size)
        li_items = []
        self.location_indicator = multi_font(
            self.location_indicator_surface,
            li_items,
            COLORS['CLOUD'])
        self.screen_objects['li'] = {
                'object': self.location_indicator, 
                'surface': self.location_indicator_surface, 
                'rect': self.location_indicator_rect,
                'dirty': True
                }

        li_row_font = 'OpenSans-Semibold.ttf'
        self.li_row_font = os.path.join("resources/fonts", li_row_font)
        self.update_indicator()

        for thing in self.screen_objects:
            self.screen_objects[thing]['object'].update()
            self.screen_objects[thing]['object'].dirty = True

    def update_indicator(self):
        # self.location_
        li_items = []
        item = {
            'font_location': self.li_row_font,
            'text': ROWS[str(RACK_DB.next['row'])] + ' ',
            'size': 23,
            'color': self.color
        }

        li_items.append(item)
        # self.info1.text = ''
        size = 18
        while len(li_items) - 1 < RACK_DB.next['column']:
            if (len(li_items)) == RACK_DB.next['column']:
                text = self.select_dot
                color = self.color
            else:
                text = self.full_dot
                color = COLORS[self.color_name]["300"]
            item = {
                'font_location': ICONS.font_location,
                'text': text,
                'size': size,
                'color': color
            }
            li_items.append(item)
        text = self.empty_dot
        color = COLORS['BLUE-GREY']['500']
        while len(li_items) - 1 < DATABASE_SETTINGS['columns']:
            item = {
                'font_location': ICONS.font_location,
                'text': text,
                'size': size,
                'color': color
            }
            li_items.append(item)
        self.location_indicator.items = li_items
        self.location_indicator.dirty = True

    def event_handler(self, event):
        # print event.type
        if event.type == SWIPE and event.value == 'up':
            self.dirty = True
            tmp = self.vkey.run('')
            accn = tmp
            if accn != '':
                # self.dirty = True
                if RACK_DB.last_filed == None:
                    self.store(accn)
                elif accn != RACK_DB.last_filed['accn']:
                    self.store(accn)
                else:
                    print "DUPLICATE ACCN - NOT FILED"
            return True
        if event.type == KEYDOWN and event.key == K_RETURN:
            self.dirty = True
            accn = self.barcode_input.value
            self.barcode_input.value = ''
            if accn != '':
                # self.dirty = True
                if RACK_DB.last_filed == None:
                    self.store(accn)
                elif accn != RACK_DB.last_filed['accn']:
                    self.store(accn)
                else:
                    print "DUPLICATE ACCN - NOT FILED"
            return True
        if self.barcode_input.update(event):
            self.dirty = True
            return True
        else:
            # self.dirty = False
            return False

    def store(self, accn):
        RACK_DB.file_accn(accn)
        self.accn_box.update_text("Last Filed: " + accn)
        self.accn_box.update()
        self.screen_objects['accn_box']['dirty'] = True
        self.update_indicator()

    def update_locations(self):
        pass

    def exit_function(self):
        self.screen.fill(COLORS['CLOUD'])
        # self.title.update()
        self.dirty = True

    def showScreen(self):
        self.update_indicator()
        file_string = gui_objects.format_location(RACK_DB.next)
        if file_string != self.info2.text:
            self.info2.update_text(file_string)
            self.info2.update()
            self.screen_objects['info2']['dirty'] = True

        self.location_indicator.update()
        tmstmp = strftime("%H:%M", localtime(time()))
        if self.clock.text != tmstmp:
                self.clock.update_text(tmstmp)
                self.clock.update()
                self.screen_objects['clock']['dirty'] = True
        self.refresh_objects()
        return self.screen
