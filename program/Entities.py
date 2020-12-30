import pygame
import os
import pprint


class CollisionImage(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface((size[2], size[3]), pygame.SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color("white"), [size[0], size[1],
                                                             size[2], size[3]], 1)
        self.rect = pygame.Rect(size[0], size[1], size[2], size[3])


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, name, health, group):
        super().__init__(group)

        self.image = pygame.Surface((90, 90))
        pygame.draw.rect(self.image, pygame.Color("blue"), [position[0], position[1], 90, 90])
        self.rect = pygame.Rect(position[0], position[1], 90, 90)
        self.position = position
        self.move_direction = "right"

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed_by_x, self.speed_by_y = 15, 15

        self.name = name
        self.health = health
        self.size = 120

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
                print(frame_location)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame, (self.size, self.size))
                frame_list.append(frame)

            self.frames[key] = frame_list

        print(self.frames)
        print(self.sp_description)

    def update(self, direction):
        if self.cur_frame[0] == direction:
            print("in", self.cur_frame[1], direction)
            if self.cur_frame[1] - 1 == len(self.frames[direction]) or \
                    self.cur_frame[1] + 1 == len(self.frames[direction]):
                self.cur_frame = (direction, 0)

            else:
                self.cur_frame = (direction, self.cur_frame[1] + 1)
        else:
            self.cur_frame = (direction, 0)

        print("out", self.cur_frame[1], direction)

        self.image = self.frames[direction][self.cur_frame[1]]


class Player(Entity):
    def __init__(self, position, name, health, group):
        super().__init__(position, name, health, group)

        """
        obstacles - список, который хранит то, с чем персонаж не может контактировать (стена, преграда)
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

        spritesheet_img = self.load_image("Adventurer Sprite Sheet v1.1.png", "data\sprites\spritesheets")
        self.animate(spritesheet_img, 13, 16, self.rect.x, self.rect.y, sp_description)

        # получинеие данных из изображения персонажа
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h

        # список стен вокруг персонажа
        self.collision_images = [CollisionImage((x + 10, y, w - 10, 10)),
                                 CollisionImage((x + w, y + 10, 10, h - 10)),
                                 CollisionImage((x + 10, y + h, w - 10, 10)),
                                 CollisionImage((x, y + 10, 10, h - 10))]

    def move_on_wasd(self, keys, level_walls):

        """
        flag = True
        for wall_group in level_walls:
            for wall in wall_group:
                if pygame.sprite.collide_rect(self.collision_images[0], wall):
                    flag = False
        if flag:
            ...
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
    pass
