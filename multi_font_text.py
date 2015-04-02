import pygame
from pprint import pprint
from global_variables import ICONS
import time


class multi_font():

    def __init__(self, surface, rect, items, background_color = (255,255,255, 0)):
        self.items = items
        self.images = []
        self.rect = rect
        self.background_color = background_color
        self.dirty = True
        self.screen = surface
        self.screen.convert_alpha()
        self.surface_rect = self.screen.get_rect()
        self.update()
    def get_screen(self):
        return self.screen

    def update(self):
        if self.dirty:
            self.create_image()
            self.dirty = False
        self._rect.centerx = self.surface_rect.centerx
        self._rect.centery = self.surface_rect.centery
    	self.screen.fill(self.background_color)
        self.screen.blit(self.combine_images, self._rect)

    def create_image(self):
    	self.images = []
        for item in self.items:
            font_location = item['font_location']
            font = pygame.font.Font(font_location, item['size'])
            image = font.render(item['text'], 1, item['color'])
            image.convert_alpha()
            self.images.append(image)

        max_height = 0
        total_width = 0
        for item in self.images:
            item_width, item_height = item.get_size()
            if max_height < item_height:
                max_height = item_height
            total_width += item_width

        self._rect = pygame.Rect(0, 0, total_width, max_height)
        self.combine_images = pygame.Surface((total_width, max_height))
        self.combine_images.fill(self.background_color)
        self.combine_images.convert_alpha()
        # THIS WILL BLIT ALL OF THE IMAGES INTO ONE
        # LARGER IMAGE SIDE BY SIDE
        x = 0
        for image in self.images:
            rect = image.get_rect()
            rect.centery = item_height/2
            rect.left = x
            # self.combine_images.fill((50,50,50))
            self.combine_images.blit(image, rect)
            x += rect.width


if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    screen.fill((255, 255, 255, 0))
    rect = (0, 0, 300, 100)
    subsurface = screen.subsurface(rect)

    items = []
    # font = pygame.font.Font(ICONS.font_location, 20)
    font = ICONS.font_location
    i = 40
    while i < 55:
        item = {
            'font_location': font,
            'text': ICONS.unicode('smile'),
            'size': i,
            'color': (128, 128, 128)
        }
        items.append(item)
        i += 1
    test = multi_font(subsurface, items)
    pygame.display.update()
    time.sleep(2)
