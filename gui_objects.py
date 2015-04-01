import pygame
import sys
import os
import parseIcons
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
    # day = strftime('%a', localtime(RACK_DB.rack_date))
    day = item['rackDay']
    file_string = day + '-' + rack + ': ' + row + '' + column
    # if time is sent with the list then we will send that too
    try:
        time = strftime("%H:%M %b %d", localtime(item['time']))
        file_string += " @ " + time
    except:
        pass
    return file_string


class render_textrect():

    # def __init__(self, string, font, rect,
                 # background_color, justification=0, vjustification=0,
                 # margin=0, shrink=False, SysFont=None, FontPath=None,
                 # MaxFont=50, MinFont=5, cutoff=True, screen=None):

    def __init__(self, *args, **kwargs):

        self.string = kwargs['string']

        self.font_info = kwargs['font']
        if 'trim' in self.font_info:
            print "found trim"
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

        if 'margin' in kwargs:
            self.margin = kwargs['margin']
            if not len(self.margin) == 4:
                try:
                    self.margin = (int(self.margin),
                                   int(self.margin),
                                   int(self.margin),
                                   int(self.margin))
                except:
                    self.margin = (0, 0, 0, 0)
        else:
            self.margin = (0, 0, 0, 0)
        if 'cutoff' in kwargs:
            self.cutoff = kwargs['cutoff']
        else:
            self.cutoff = False
        if 'shrink' in kwargs:
            self.shrink = kwargs['shrink']
        else:
            self.shrink = False
        self.dirty = True

        if isinstance(self.margin, tuple):
            if not len(self.margin) == 4:
                try:
                    self.margin = (int(self.margin),
                                   int(self.margin),
                                   int(self.margin),
                                   int(self.margin))
                except:
                    self.margin = (0, 0, 0, 0)
        elif isinstance(self.margin, int):
            self.margin = (self.margin, self.margin, self.margin, self.margin)
        else:
            self.margin = (0, 0, 0, 0)

    def update_string(self, string):
        if self.string != string:
            print "String Changed " + string
            self.string = string
            self.dirty = True
            self.update()

    def get_screen(self):
        self.dirty = False
        return self.screen

    def update(self):
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
                except self.TextRectException:
                    self.fontsize -= 1
                    # print "trying new font" + str(self.fontsize)
            if not fit:
                self.cutoff = True
                # print "shrunk to font: " + str(self.fontsize)
                self.font = pygame.font.Font(self.FontPath, self.fontsize)
                self.screen = self.draw_text_rect()
        self.screen = self.draw_text_rect()

    class TextRectException(Exception):

        def __init__(self, message=None):
            self.message = message

        def __str__(self):
            return self.message

    def draw_text_rect(self):
        print self.string
        padded_surface = pygame.Surface(self.rect.size)
        padded_surface.fill(self.background_color)
        # padded_surface.fill((169,169,169))

        text_rect = padded_surface.get_rect()

        text_rect.width -= self.margin[0] + self.margin[1]
        text_rect.height -= self.margin[2] + self.margin[3]
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
            print self.font.size(line)[1]
            print self.trim
            if h + (self.font.size(line)[1] * self.trim) >= text_rect.height:
                raise self.TextRectException(
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
        if self.v_align == 'top':
            text_rect.top = self.margin[0]
            pass
        elif self.v_align == 'center':
            text_rect.centery = self.rect.height/2
        elif self.v_align == 'bottom':
            text_rect.bottom = self.rect.height - self.margin[3]
            # surface = tempsurface
        else:
            raise self.TextRectException(
                "Invalid vjustification argument: " +
                str(v_align))
        padded_surface.blit(surface, text_rect)
        return padded_surface

if __name__ == "__main__":
    pass
