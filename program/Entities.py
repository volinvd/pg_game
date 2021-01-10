import pygame
import os
import pprint
import random


class CollisionImage(pygame.sprite.Sprite):
    def __init__(self, size, group=None):
        if group is not None:
            super().__init__(group)
        self.image = pygame.Surface((size[2], size[3]))
        pygame.draw.rect(self.image, pygame.Color("white"), [size[0], size[1],
                                                             size[2], size[3]])
        self.rect = pygame.Rect(size[0], size[1], size[2], size[3])

    def update_coord(self, x, y):
        self.rect.x += x
        self.rect.y += y


class Inventory(pygame.sprite.Sprite):
    def __init__(self, position, group):

        """
        :param position: позиция инвентаря (по центру экрана)
        :param group: группа спрайтов инвентаря
        self.size - размер инвентаря
        self.inventory_cells - матрица клеток инвентаря
        """

        super().__init__(group)

        self.size = 974, 392

        self.image = self.load_image('inventory.png', 'data/sprites/inventory/')
        self.rect = pygame.Rect(position[0], position[1], self.size[0], self.size[1])

        self.position = position
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.inventory_cells = [[InventoryCell(position, (82 + x * 62, 59 + y * 62), group)
                                 for y in range(3)] for x in range(8)]

    def load_image(self, name, directory, color_key=None):
        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname)

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        return image


class InventoryCell(pygame.sprite.Sprite):
    def __init__(self, parent_position, position, group):
        """

        :param parent_position: позиция инветаря
        :param position: позиция клетки
        :param group: группа спрайтов инвентаря
        self.base_position - стартавая позиция клетки
        """
        super().__init__(group)

        self.size = 47
        self.image = pygame.Surface((self.size, self.size))

        color = random.choice(["yellow", 'orange', 'red', 'green'])
        pygame.draw.rect(self.image, pygame.Color(color), [0, 0, self.size, self.size])
        self.rect = pygame.Rect(position[0], position[1], self.size, self.size)

        self.position = position
        self.rect.x, self.rect.y = parent_position[0] + position[0], parent_position[1] + position[1]
        self.base_position = self.rect.x, self.rect.y


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, name, health, group):
        super().__init__(group)

        self.image = pygame.Surface((120, 120))
        pygame.draw.rect(self.image, pygame.Color("blue"), [0, 0, 120, 120])
        self.rect = pygame.Rect(position[0], position[1], 120, 120)
        self.position = position
        self.move_direction = "right"

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed_by_x, self.speed_by_y = 15, 15

        self.name = name
        self.health = health
        self.size = 120

        self.hp_bar = HPBar((position[0] + 20, position[1], 80, 8), group)

    def get_damage(self, damage):
        self.health -= damage

    def load_image(self, name, directory, color_key=None):

        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname)

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        return image

    def animate(self, sheet, columns, rows, x, y, sp_description):
        self.frames = {}
        self.cut_sheet(sheet, columns, rows, sp_description)
        self.cur_frame = ("move right", 0)
        self.image = self.frames["move right"][0]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows, sp_description):
        self.sp_description = sp_description
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)

        for key, list_with_coordinates in self.sp_description.items():
            frame_list = []

            for coordinate in list_with_coordinates:
                frame_location = (self.rect.w * coordinate[0], self.rect.h * coordinate[1])
                # print(frame_location)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame, (self.size, self.size))
                frame_list.append(frame)

            self.frames[key] = frame_list

        # print(self.frames)
        # print(self.sp_description)

    def update(self, direction):
        if self.cur_frame[0] == direction:
            # print("in", self.cur_frame[1], direction)
            if self.cur_frame[1] - 1 == len(self.frames[direction]) or \
                    self.cur_frame[1] + 1 == len(self.frames[direction]):
                self.cur_frame = (direction, 0)

            else:
                self.cur_frame = (direction, self.cur_frame[1] + 1)
        else:
            self.cur_frame = (direction, 0)

        # print("out", self.cur_frame[1], direction)

        self.image = self.frames[direction][self.cur_frame[1]]


class Player(Entity):
    def __init__(self, position, name, health, group, screen_size, inventory_group):
        super().__init__(position, name, health, group)

        """
        obstacles - список, который хранит то, с чем персонаж не может контактировать (стена, преграда)
        self.change_inventory_cell_position - меняются ли клетки инентаря местами
        self.first_inventory_cell = self.second_inventory_cell - первая и вторая клетки, которые меняют местами
        self.difference_x = self.difference_y - для передвижения клетки во время зажатия клавиши мыши
        """

        self.image = self.load_image('player.png', 'data/sprites/entities/Player/')
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        sp_description = {"look around right": [(x, 0) for x in range(0, 13)],
                          "move right": [(x, 1) for x in range(0, 8)],
                          "beat right up": [(x, 2) for x in range(0, 10)],
                          "beat right down": [(x, 3) for x in range(0, 10)],
                          "sweeping edge beat right": [(x, 4) for x in range(0, 8)],
                          "jump right": [(x, 5) for x in range(0, 10)],
                          "fall from the portal right": [(x, 7) for x in range(0, 7)],
                          "look around left": [(x, 8) for x in range(0, 13)],
                          "move left": [(x, 9) for x in range(0, 8)],
                          "beat left up": [(x, 11) for x in range(0, 10)],
                          "beat left down": [(x, 12) for x in range(0, 10)],
                          "sweeping edge beat left": [(x, 13) for x in range(0, 8)],
                          "jump left": [(x, 14) for x in range(0, 6)],
                          "fall from the portal left": [(x, 15) for x in range(0, 7)]}

        spritesheet_img = self.load_image("Adventurer Sprite Sheet v1.1.png", "data/sprites/spritesheets")
        self.animate(spritesheet_img, 13, 16, self.rect.x, self.rect.y, sp_description)

        # получинеие данных из изображения персонажа
        x, y, w, h = self.rect.x, self.rect.y, self.size, self.size

        # список стен вокруг персонажа
        self.collision_images = [CollisionImage((x + 20, y, w - 40, 10)),
                                 CollisionImage((x + w - 10, y + 20, 10, h - 20)),
                                 CollisionImage((x + 20, y + h + 10, w - 40, 10)),
                                 CollisionImage((x, y + 20, 10, h - 20))]

        self.change_inventory_cell_position = False
        self.first_inventory_cell = self.second_inventory_cell = None
        self.difference_x = self.difference_y = 0
        self.inventory = Inventory(((screen_size[0] - 974) // 2, (screen_size[1] - 392) // 2),
                                   inventory_group)
        self.inventory_state = 'close'
        self.screen_size = screen_size

    def move_on_wasd(self, keys, level_walls):

        """
        этот однообразный код при ходьбе проверяет столкновение
        с группой спрайтов, помеченных как припятствие при инициализации
        функция возвращает перемещение по x и y
        так как двигаем мы canvas, а он главнее, чем игрок
        """

        # передвижение по оси y
        y = x = 0
        if keys[pygame.K_w]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[0], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                y = self.speed_by_y

        elif keys[pygame.K_s]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[2], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                y = -self.speed_by_y

        # передвижение по оси x
        if keys[pygame.K_a]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[3], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                x = self.speed_by_x

        elif keys[pygame.K_d]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[1], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                x = -self.speed_by_x
        return x, y


class BaseEnemy(Entity):
    def __init__(self, position, name, health, group, direction):
        super().__init__(position, name, health, group)

        # получинеие данных из изображения моба
        x, y, w, h = self.rect.x, self.rect.y, self.size, self.size

        # список стен вокруг персонажа
        self.collision_images = [CollisionImage((x + 10, y, w - 20, 10)),
                                 CollisionImage((x + w - 10, y + 20, 10, h - 40)),
                                 CollisionImage((x + 20, y + h - 10, w - 40, 10)),
                                 CollisionImage((x, y + 20, 10, h - 40))]
        self.direction = direction
        self.speed_by_y = self.speed_by_x = 5

    def move(self, level_walls):
        if self.direction == 'up':
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[0], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                self.rect.y -= self.speed_by_y
                for collision_img in self.collision_images:
                    collision_img.rect.y -= self.speed_by_y
                self.hp_bar.rect.y -= self.speed_by_y
            else:
                self.direction = 'right'
        if self.direction == 'right':
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[1], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                self.rect.x += self.speed_by_x
                for collision_img in self.collision_images:
                    collision_img.rect.x += self.speed_by_x
                self.hp_bar.rect.x += self.speed_by_x
            else:
                self.direction = 'down'
        if self.direction == 'down':
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[2], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                self.rect.y += self.speed_by_y
                for collision_img in self.collision_images:
                    collision_img.rect.y += self.speed_by_y
                self.hp_bar.rect.y += self.speed_by_y
            else:
                self.direction = 'left'
        if self.direction == 'left':
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[3], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                self.rect.x -= self.speed_by_x
                for collision_img in self.collision_images:
                    collision_img.rect.x -= self.speed_by_x
                self.hp_bar.rect.x -= self.speed_by_x
            else:
                self.direction = 'up'


class HPBar(pygame.sprite.Sprite):
    def __init__(self, size, group):
        super().__init__(group)
        self.image = pygame.Surface((size[2], size[3]))
        pygame.draw.rect(self.image, pygame.Color("#68d37b"), [0, 0,
                                                             size[2], size[3]])
        pygame.draw.rect(self.image, pygame.Color("black"), [0, 0,
                                                             size[2], size[3]], 1)
        self.rect = pygame.Rect(size[0], size[1], size[2], size[3])
        self.max_hp = size[2]

    def update_coord(self, x, y):
        self.rect.x += x
        self.rect.y += y

