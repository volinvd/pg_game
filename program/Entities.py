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
        print(fullname)
        image = pygame.image.load(fullname).convert_alpha()

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image


class Player(Unit):
    def __init__(self, position, name, health, group, screen_size, canvas):
        super().__init__(position, name, health, group, screen_size)

        self.image = self.load_image('player.png', 'data/sprites/entities/Player/')

        koef = round(canvas.cell_sizes[canvas.opened_in_full_screen] / 32)

        img_size = self.image.get_rect().size
        self.image = pygame.transform.scale(self.image, (int(img_size[0] * koef), int(img_size[1] * koef)))

        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = self.screen_size
        self.rect.x = int((self.rect.x - self.rect.w) / 2)
        self.rect.y = int((self.rect.y - self.rect.h) / 2)

        self.padding_x = self.rect.x
        self.canvas = canvas

    def move(self, keys):

        # передвижение по оси y
        if keys[pygame.K_w]:
            if self.rect.y - self.speed_by_y >= 0:  # проверка на то, выйдет ли персонаж за верхнюю гроницу
                self.rect = self.rect.move(0, -self.speed_by_y)

        elif keys[pygame.K_s]:
            # проверка на то, выйдет ли персонаж за нижнюю гроницу
            if self.rect.y + self.speed_by_y + self.rect.h <= 7 * self.canvas.cell_sizes[self.canvas.opened_in_full_screen]:
                self.rect = self.rect.move(0, self.speed_by_y)

        # передвижение по оси x
        if keys[pygame.K_a]:

            # проверяем, чо игрок находится по центру (self.padding_x) если нет, то двигаем игрока игаче канвас
            if self.canvas.left >= 0 or self.rect.x > self.padding_x:
                if self.rect.x - self.speed_by_x >= 0:
                    self.rect = self.rect.move(-self.speed_by_x, 0)
            else:
                self.canvas.change_left_padding(self.speed_by_x)

        elif keys[pygame.K_d]:

            # переменная, в которой координата правой границы
            right = len(self.canvas.matrix[0]) * self.canvas.cell_sizes[self.canvas.opened_in_full_screen] - \
                   self.canvas.window_size[0] + self.canvas.left

            # проверяем, чо игрок находится по центру (self.padding_x) если нет, то двигаем игрока игаче канвас
            if right <= -5 or self.rect.x < self.padding_x:
                if self.rect.x + self.speed_by_x <= self.canvas.window_size[0] - self.rect.w:
                    self.rect = self.rect.move(self.speed_by_x, 0)
            else:
                self.canvas.change_left_padding(-self.speed_by_x)


class BaseEnemy(Unit):
    pass
