import pygame
import os


class MyImage(pygame.sprite.Sprite):
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

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed_by_x, self.speed_by_y = 10, 10

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

        # получинеие данных из изображения персонажа
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h

        # список стен вокруг персонажа
        self.collision_images = [MyImage((x + 10, y, w - 10, 10)),
                                 MyImage((x + w, y + 10, 10, h - 10)),
                                 MyImage((x + 10, y + h, w - 10, 10)),
                                 MyImage((x, y + 10, 10, h - 10))]

    def move_on_wasd(self, keys, level_walls):

        """
        flag = True
        for obstacle in self.obstacles:
            if pygame.sprite.spritecollide(self.collision_images[0], obstacle, False):
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
            flag = True
            for wall_group in level_walls:
                for wall in wall_group:
                    if pygame.sprite.collide_rect(self.collision_images[0], wall):
                        flag = False
            if flag:
                y = self.speed_by_y

        elif keys[pygame.K_s]:
            flag = True
            for wall_group in level_walls:
                for wall in wall_group:
                    if pygame.sprite.collide_rect(self.collision_images[2], wall):
                        flag = False
            if flag:
                y = -self.speed_by_y

        # передвижение по оси x
        if keys[pygame.K_a]:
            flag = True
            for wall_group in level_walls:
                for wall in wall_group:
                    if pygame.sprite.collide_rect(self.collision_images[3], wall):
                        flag = False
            if flag:
                x = self.speed_by_x

        elif keys[pygame.K_d]:
            flag = True
            for wall_group in level_walls:
                for wall in wall_group:
                    if pygame.sprite.collide_rect(self.collision_images[1], wall):
                        flag = False
            if flag:
                x = -self.speed_by_x
        return x, y


class BaseEnemy(Entity):
    pass
