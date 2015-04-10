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

special_keys = [
        'keyboard-return',
        'keyboard-backspace',
        'keyboard-close',
        'eraser',
        'alphabetical']

clock = pygame.time.Clock()
DEBUG = False
swype = swipe()
class VirtualKeyboard():

    ''' Implement a basic full screen virtual keyboard for touchscreens '''

    def __init__(self, screen, color, validate=True):

        # SCREEN SETTINGS
        self.screen = screen
        self.screen.fill(COLORS['CLOUD'])

        self.rect = self.screen.get_rect()
        w,h = self.rect.size

        kw = int((w) / 4)
        kh = int((h) / 5)
        kx = (w - kw * 4) / 2
        ky = 0
        self.key_rect = pygame.Rect(kx, ky, kw, kh)

        self.keyFont = FONTS['key_font']['font']

        self.fa = pygame.font.Font(
            ICONS.font_location, int(
                kh * 0.70))  # keyboard font

        self.textW = w  # + 4  # leave room for escape key
        self.textH = kh
        self.color = COLORS[color]

        self.caps = False
        self.keys = []
        self.addkeys()  # add all the keys
        
        self.input = TextInput(
            self.screen,
            '',
            kx,
            ky,
            kw*4,
            kh)

        self.validate = validate
        self.run(init=True)
        self.screen_copy = self.screen.copy()
        self.special_keys = {
            'keyboard-return': self.keyboard_return,
            'keyboard-backspace': self.keyboard_backspace,
            'keyboard-close': self.keyboard_close,
            'eraser': self.keyboard_backspace,
            'alphabetical': self.togglecaps
        }

    def keyboard_return(self):
        return True

    def keyboard_close(self):
        self.eraser()
        return True

    def keyboard_backspace(self):
        self.input.backspace()
        if len(self.input.text) == 0:
            self.togglecaps(force=True)
        self.paintkeys()
        return False

    def eraser(self):
        while self.input.cursorpos > 0:
            self.input.backspace()
        return False

    def run(self, text='', init=False):
        self.screen.fill(COLORS['CLOUD'])
        self.text = text
        self.caps = False
        self.togglecaps()
        self.paintkeys()

        if init:
            return
        counter = 0
        # main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based...
        while True:
            time.sleep(0.1)  # 10/second is often enough
            events = pygame.event.get()

            if len(self.input.text) == 1 and self.caps:
                self.togglecaps(force=False)

            for e in events:
                if swype.event_handler(e) == 'down':
                    self.input.text = ''
                    return ''
                if (e.type == MOUSEBUTTONDOWN):
                    self.selectatmouse()
                if (e.type == MOUSEBUTTONUP):
                    if self.clickatmouse():
                        # user clicked enter or escape if returns True
                        if self.input.text == '':
                            return self.input.text
                        if self.validate == False:
                            return self.input.text
                        if sunquest_fix(self.input.text) == None:
                            self.paintkeys()
                            temp = self.input.text
                            self.input.text = 'invalid'
                            self.input.cursorvis = False
                            self.input.draw()
                            pygame.display.update()
                            time.sleep(1)
                            self.input.text = temp
                            self.input.draw()
                            pygame.display.update()
                        else:
                            text = sunquest_fix(self.input.text)
                            self.input.text = ''
                            return text

                if (e.type == MOUSEMOTION):
                    if e.buttons[0] == 1:
                        # user click-dragged to a different key?
                        self.selectatmouse()
            counter += 1
            if counter > 10:
                self.input.flashcursor()
                counter = 0
            pygame.display.update()
    def invalid_entry(self):
        pass
        self.clear()


    def unselectall(self, force=False):
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True


    def clickatmouse(self):
        # ''' Check to see if the user is pressing down on a key and draw it selected '''
        # self.screen.blit(self.screenCopy, (0,0))
        self.unselectall()
        for key in self.keys:
            if key.rect.collidepoint(pygame.mouse.get_pos()):
                key.dirty = True
                if key.special:
                    result = self.special_keys[key.special]()
                    return result
                elif self.caps:
                    key = key.caption.translate(Uppercase)
                    if key != ' ':
                        self.input.addcharatcursor(key)
                else:
                    self.input.addcharatcursor(key.caption)
        self.paintkeys()
        return False

    def togglecaps(self, force='toggle'):
        print "toggle caps"
        if force == 'toggle':
            self.caps = not self.caps
        else:
            self.caps = force
        
        for key in self.keys:
            key.dirty = True
        self.paintkeys()
        return False

    def selectatmouse(self):
        self.unselectall()
        pos = pygame.mouse.get_pos()
        if self.input.rect.collidepoint(pos):
            self.input.setcursor(pos)
        else:
            x,y = swype.delta
            if abs(x) < 20 and abs(y) < 20:
                for key in self.keys:
                    if key.rect.collidepoint(pos):
                        key.selected = True
                        key.dirty = True
                        break
        self.paintkeys()

    def addkeys(self):  # Add all the keys for the virtual keyboard

        self.key_rect.left = 1
        self.key_rect.top += self.textH
        for item in range(7, 10):
            key = VKey(str(item), self.key_rect.copy(), self.keyFont, self.color)
            self.keys.append(key)
            self.key_rect.left += self.key_rect.width + 1
        onekey = VKey('keyboard-backspace',self.key_rect.copy(),self.fa, self.color)
        onekey.bskey = True
        self.keys.append(onekey)

        self.key_rect.top = self.key_rect.bottom + 1
        self.key_rect.left = 1

        for item in range(4, 7):
            key = VKey(str(item), self.key_rect.copy(), self.keyFont, self.color)
            self.keys.append(key)
            self.key_rect.left = self.key_rect.right + 1

        onekey = VKey('alphabetical',self.key_rect.copy(),self.fa, self.color)
        self.keys.append(onekey)

        self.key_rect.left = 1
        self.key_rect.top = self.key_rect.bottom + 1

        for item in range(1, 4):
            key = VKey(str(item), self.key_rect.copy(), self.keyFont, self.color)
            self.keys.append(key)
            self.key_rect.left = self.key_rect.right + 1

        onekey = VKey('keyboard-return',self.key_rect.copy(),self.fa, self.color)
        self.keys.append(onekey)

        self.key_rect.left = 1
        self.key_rect.top = self.key_rect.bottom + 1        
        onekey = VKey('keyboard-close',self.key_rect.copy(),self.fa, self.color)        
        self.keys.append(onekey)

        self.key_rect.left = self.key_rect.right + 1
        key = VKey('0', self.key_rect.copy(), self.keyFont, self.color)
        self.keys.append(key)
        self.key_rect.left = self.key_rect.right + 1

        key = VKey('eraser', self.key_rect.copy(), self.fa, self.color)
        self.keys.append(key)

        self.all_keys = pygame.sprite.Group()
        self.all_keys.add(self.all_keys, self.keys)

    def paintkeys(self):
        ''' Draw the keyboard (but only if they're dirty.) '''
        for key in self.keys:
            # pass
            key.update(self.caps)
        self.all_keys.draw(self.screen)

class TextInput():

    ''' Handles the text input box and manages the cursor '''

    def __init__(self, screen, text, x, y, w, h):
        self.screen = screen
        self.text = text
        self.cursorpos = len(text)
        self.x = x
        self.y = y
        self.w = w - 2
        self.h = h - 3
        self.rect = Rect(1, 1, w, h)
        self.surface_rect = Rect(0, 0, w, h)
        self.layer = pygame.Surface((self.w, self.h))
        self.surface = screen.subsurface(self.surface_rect)
        self.max_length = 9

        self.background_color = COLORS['CLOUD']
        self.font_color = COLORS['BLUE-GREY']['700']
        self.cursor_color = self.font_color

        font_file = 'SourceCodePro-Regular.ttf'
        font_location = os.path.join("resources/fonts", font_file)

        rect = self.surface_rect
        fsize = int(self.h)  # font size proportional to screen height
        self.txtFont = pygame.font.Font(
            font_location, int(
                fsize))  # keyboard font

        # attempt to figure out how many chars will fit on a line
        # this does not work with proportional fonts
        tX = self.txtFont.render("XXXXXXXXXX", 1, (255, 255, 0))  # 10 chars
        rtX = tX.get_rect()  # how big is it?

        # chars per line (horizontal)
        self.lineChars = int(self.w / (rtX.width / 10)) - 1
        self.lineH = self.h - 4  # pixels per line (vertical)
        self.lineH = rtX.height  # pixels per line (vertical)

        self.cursorlayer = pygame.Surface(
            (2, self.lineH - 20))  # thin vertical line
        self.cursorlayer.fill(self.cursor_color)  # white vertical line
        self.cursorvis = True

        self.cursorX = len(text) % self.lineChars
        self.cursorY = int(len(text) / self.lineChars)  # line 1

        self.draw()
        

    def draw(self):
        ''' Draw the text input box '''
        self.layer.fill(self.background_color)

        t1 = self.txtFont.render(self.text, 1, self.font_color)  # line 1
        self.layer.blit(t1, (10, -8))

        self.drawcursor()
        self.surface.blit(self.layer, self.rect)

    def flashcursor(self):
        ''' Toggle visibility of the cursor '''
        if self.cursorvis:
            self.cursorvis = False
        else:
            self.cursorvis = True

        if self.cursorvis:
            self.drawcursor()
        self.draw()

    def addcharatcursor(self, letter):
        ''' Add a character whereever the cursor is currently located '''
        if self.cursorpos < len(self.text) and len(self.text) < self.max_length:
            # print 'Inserting in the middle'
            self.text = self.text[:self.cursorpos] + letter + self.text[self.cursorpos:]
            self.cursorpos += 1
            self.draw()
            return
        if len(self.text) < self.max_length:
            self.text += letter
            self.cursorpos += 1
        self.draw()

    def backspace(self):
        ''' Delete a character before the cursor position '''
        if self.cursorpos == 0:
            return
        self.text = self.text[:self.cursorpos - 1] + self.text[self.cursorpos:]
        self.cursorpos -= 1
        self.draw()
        return

    def deccursor(self):
        ''' Move the cursor one space left '''
        if self.cursorpos == 0:
            return
        self.cursorpos -= 1
        self.draw()

    def inccursor(self):
        ''' Move the cursor one space right (but not beyond the end of the text) '''
        if self.cursorpos == len(self.text):
            return
        self.cursorpos += 1
        self.draw()

    def drawcursor(self):
        ''' Draw the cursor '''
        line = int(self.cursorpos / self.lineChars)  # line number
        if line > 1:
            line = 1
        x = 4
        y = 4
        if self.cursorpos > 0:
            linetext = self.text[line * self.lineChars:self.cursorpos]
            rtext = self.txtFont.render(linetext, 1, self.font_color)
            textpos = rtext.get_rect()
            x = x + textpos.width + 6

        if self.cursorvis:
            self.cursorlayer.fill(self.cursor_color)
        else:
            self.cursorlayer.fill(self.background_color)
        self.layer.blit(self.cursorlayer, (x, y))

    def setcursor(self, pos):  # move cursor to char nearest position (x,y)
        line = 0
        x = pos[0] - self.x + line * self.w  # virtual x position
        p = 0
        l = len(self.text)
        while p < l:
            text = self.txtFont.render(
                self.text[
                    :p + 1], 1, (255, 255, 255))  # how many pixels to next char?
            rtext = text.get_rect()
            textX = rtext.x + rtext.width
            if textX >= x:
                break  # we found it
            p += 1
        self.cursorpos = p
        self.draw()

class VKey(pygame.sprite.Sprite):

    ''' A single key for the VirtualKeyboard '''

    def __init__(
            self,
            caption,
            rect,
            font,
            color):
        pygame.sprite.Sprite.__init__(self)
        self.special = None
        self.selected = False
        self.dirty = True

        if caption in special_keys:
            self.special = caption
            if caption == 'alphabetical':
                shifted_text = ICONS.unicode('numeric')
            else:
                shifted_text = ICONS.unicode(caption)
            caption = ICONS.unicode(caption)
        else:
            self.caption = caption
            shifted_text = caption.translate(Uppercase)
        
        self.rect = rect
        if self.special == 'keyboard-return':
            top = rect.top
            rect.height *= 2
            rect.top = top
        self.image = pygame.Surface(self.rect.size)
        
        self.selected_color = color['100']
        self.color = color['500']
        font_color = COLORS['CLOUD']
        self.text = font.render(caption, 1, font_color)
        self.shifted_text = font.render(shifted_text, 1,font_color)

    def update(self, shifted=False, forcedraw=False):
        '''  Draw one key if it needs redrawing '''
        if not forcedraw:
            if not self.dirty:
                return
        if shifted:
            text = self.shifted_text
        else:
            text = self.text
        
        if self.selected:
            color = self.selected_color
        else:
            color = self.color
        
        self.image.fill(color)
        textpos = text.get_rect()
        textpos.centerx = self.rect.width / 2
        textpos.centery = self.rect.height / 2
        self.image.blit(text, textpos)
        self.dirty = False
