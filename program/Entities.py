import pygame
import os


class Unit(pygame.sprite.Sprite):
    def __init__(self, position, name, health, group, screen_size):

        super().__init__(group)

        self.image = pygame.Surface((90, 90))
        pygame.draw.rect(self.image, pygame.Color("blue"), [position[0], position[1], 90, 90])
        self.rect = pygame.Rect(position[0], position[1], 90, 90)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed_by_x, self.speed_by_y = 10, 10

        self.name = name
        self.health = health
        self.screen_size = screen_size

    def get_damage(self, damage):
        self.health -= damage

    def load_image(self, name, directory, color_key=None):

        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname).convert_alpha()

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image


class Player(Unit):
    pass


class BaseEnemy(Unit):
    pass
