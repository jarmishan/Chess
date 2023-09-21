import  json

import pygame as _pygame

_pygame.init()

class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = _pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace("png", "json")
        with open(self.meta_data) as file:
            self.data = json.load(file)
        file.close()

    def get_sprite(self, x, y, width, height):
        sprite  = _pygame.Surface((width, height))
        sprite.set_colorkey((255, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite
    
    def parse_sprite(self, name):
        sprite = self.data["frames"][name]["frame"]
        
        return self.get_sprite(sprite["x"], sprite["y"], sprite["w"],sprite["h"])