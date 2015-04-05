import pygame
import sys
import os
import parseIcons
from time import time, sleep
from PIL import Image, ImageFilter
from time import strftime, localtime
from PIL import ImageDraw, ImageFont
from global_variables import COLORS, ROWS, ICON_FONT_FILE, ICONS, SHADING_ITERATIONS
from global_variables import ICON_FONT_JSON, REBUILD_BANNER, CORNER_RADIUS
from global_variables import SHADING_QUALITY, BACKGROUND_COLOR, BORDER, BANNNER_ICON_SIZE

from pprint import pprint

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def format_location(item):
    row = ROWS[str(item['row'])]
    rack = str(item['rack'])
    column = str(item['column'])
    day = item['rackDay']
    file_string = day + '-' + rack + ': ' + row + '' + column
    try:
        time = strftime("%H:%M %b %d", localtime(item['time']))
        file_string += " @ " + time
    except:
        pass
    return file_string

class TextRectException(Exception):

        def __init__(self, message=None):
            self.message = message

        def __str__(self):
            return self.message

class render_textrect():
    def __init__(self, *args, **kwargs):

        self.string = kwargs['string']

        self.font_info = kwargs['font']
        if 'trim' in self.font_info:
            # print "found trim"
            self.trim = self.font_info['trim']
        else:
            self.trim = 1
        self.font = self.font_info['font']
        self.FontPath = self.font_info['path']
        self.text_color = self.font_info['color']
        self.MaxFont = self.font_info['size']
        self.MinFont = self.font_info['size'] - 5

        self.screen = kwargs['screen']
        self.rect = kwargs['rect']
        self.background_color = kwargs['background_color']

        if 'SysFont' in kwargs:
            self.SysFont = kwargs['SysFont']
        else:
            self.SysFont = None

        if 'h_align' in kwargs:
            self.h_align = kwargs['h_align']
        else:
            self.h_align = 'center'

        if 'v_align' in kwargs:
            self.v_align = kwargs['v_align']
        else:
            self.v_align = 'center'

        sides = ('top', 'bottom', 'left', 'right')
        self.margin = {}
        if 'margin' in kwargs:
            _m = kwargs['margin']
            for side in sides:
                if side in _m:
                    self.margin[side] = _m[side]
        for side in sides: self.margin[side] = 0

        if 'cutoff' in kwargs:
            self.cutoff = kwargs['cutoff']
        else:
            self.cutoff = False
        if 'shrink' in kwargs:
            self.shrink = kwargs['shrink']
        else:
            self.shrink = False
        self.dirty = True
        self._update()

    def change_font(self, font, color=None):
        self.font_info = font
        self.font = self.font_info['font']
        self.FontPath = self.font_info['path']
        self.text_color = self.font_info['color']
        self.MaxFont = self.font_info['size']
        self.MinFont = self.font_info['size'] - 5
        if color:
            self.text_color = color

    def update_string(self, string):
        if self.string != string:
            # print "String Changed " + string
            self.string = string
            self.dirty = True
            self._update()

    def get_screen(self):
        self.dirty = False
        return self.screen

    def _update(self):
        # print "Updatating Thing " + self.string
        self.fontsize = self.MaxFont
        if not self.shrink:
            # print "not shrunk"
            self.screen = self.draw_text_rect()
        else:
            fit = False
            while self.fontsize >= self.MinFont:
                if self.FontPath is None:
                    self.font = pygame.font.SysFont(
                        self.SysFont,
                        self.fontsize)
                else:
                    # print "found font"
                    self.font = pygame.font.Font(
                        self.FontPath,
                        self.fontsize)
                try:
                    surface = self.draw_text_rect()
                    fit = True
                    break
                except TextRectException:
                    self.fontsize -= 1
                    # print "trying new font" + str(self.fontsize)
            if not fit:
                self.cutoff = True
                # print "shrunk to font: " + str(self.fontsize)
                self.font = pygame.font.Font(self.FontPath, self.fontsize)
                self.screen = self.draw_text_rect()
        self.screen = self.draw_text_rect()

    def draw_text_rect(self):
        # print self.string
        padded_surface = pygame.Surface(self.rect.size)
        padded_surface.fill(self.background_color)
        # padded_surface.fill((169,169,169))

        text_rect = padded_surface.get_rect()

        # text_rect.width -= self.margin[0] + self.margin[1]
        # text_rect.height -= self.margin[2] + self.margin[3]
        surface = pygame.Surface(text_rect.size)
        surface.fill(self.background_color)
        # surface.fill((200,200,200))

        final_lines = []
        lines = self.string.splitlines()
        for line in lines:
            if self.font.size(line)[0] > text_rect.width:
                words = line.split(' ')
                # if any of our words are too long to fit, return.
                for word in words:
                    if self.font.size(word)[0] >= text_rect.width:
                        raise TextRectException(
                            "The word " +
                            word +
                            " is too long to fit in the rect passed.")
                accumulated_line = ""
                for word in words:
                    test_line = accumulated_line + word + " "
                    # Build the line while the words fit.
                    if self.font.size(test_line)[0] < text_rect.width:
                        accumulated_line = test_line
                    else:
                        final_lines.append(accumulated_line)
                        accumulated_line = word + " "
                final_lines.append(accumulated_line)
            else:
                final_lines.append(line)

        # Let's try to write the text out on the surface.

        # surface = pygame.Surface(self.rect.size)
        # surface.fill(self.background_color)
        h = 0
        _trimming_rect= None
        for line in final_lines:
            new_height = h + (self.font.size(line)[1] * self.trim)
            if new_height >= self.rect.height:
                raise TextRectException(
                    "Once word-wrapped, the text string was too tall to fit in the rect.")
            if line != '':
                # RENDER THE TEXT
                tempsurface = self.font.render(line, 1, self.text_color)
                # GET THE SIZE OF TEXT
                _trimming_rect = tempsurface.get_rect()
                # CUT THE PADDING OFF THE BOTTOM OF THE TEXT
                _trimming_rect.top = h
                _trimming_rect.height = int(_trimming_rect.height * self.trim)

                if self.h_align == 'left':
                    _trimming_rect.left = 0
                    surface.blit(tempsurface, _trimming_rect)
                elif self.h_align == 'center':
                    _trimming_rect.centerx = text_rect.centerx
                    surface.blit(tempsurface, _trimming_rect)
                elif self.h_align == 'right':
                    _trimming_rect.left = text_rect.width - _trimming_rect.width
                    surface.blit(tempsurface, _trimming_rect)
                else:
                    raise TextRectException(
                        "Invalid justification argument: " + str(self.h_align))
            h += _trimming_rect.height
        text_rect.height = h
        if self.h_align =='left':
            text_rect.left = self.margin['left']
        elif self.h_align == 'center':
            text_rect.centerx = self.rect.width/2
            text_rect.centerx += self.margin['left']
            text_rect.centerx -= self.margin['right']
        elif self.h_align == 'right':
            text_rect.left = self.rect.width - text_rect.width
            text_rect.width -= self.margin['right']
        if self.v_align == 'top':
            text_rect.top = self.margin['top']
            pass
        elif self.v_align == 'center':
            text_rect.centery = self.rect.height/2 
            text_rect.centery += self.margin['top']
            text_rect.centery -= self.margin['bottom']
        elif self.v_align == 'bottom':
            text_rect.bottom = self.rect.height - self.margin['bottom']
        else:
            raise TextRectException(
                "Invalid vjustification argument: " +
                str(v_align))
        padded_surface.blit(surface, text_rect)
        return padded_surface

class textrect_image(render_textrect):
    def __init__(self, *args, **kwargs):
        render_textrect.__init__(self, *args, **kwargs)
        img = kwargs['img']
        img_rect = img.get_rect()
        img_rect.centerx = self.rect.centerx

        self.img = pygame.Surface(self.rect.size)
        self.img.fill(self.background_color)
        self.img.blit(img, img_rect)
        self.show_img = False
        self._update()

    def toggle_screen(self):
        self.dirty = True
        self.show_img = not self.show_img
        # print "Toggled screens"

    def get_screen(self):
        self.dirty = False
        if self.show_img:
            # print "returning image"
            return self.img
        else:
            return self.screen

    def update_string(self, string):
        if self.show_img:
            self.dirty = True
            self.show_img = False
        if self.string != string:
            self.string = string
            self.dirty = True
            self._update()




if __name__ == "__main__":
    pass
