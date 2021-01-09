import pygame
import os
import pytmx
import random

import program.Entities as Entities


class Canvas:
    def __init__(self):

        """
        info - переменная, хранящая информацию о экране пользователя
        self.screen - главный экран для отрисоки
        self.filename_of_maps - список, в котором хранятся пути к файлам карт
        self.level_maps - список, в котором хранятся все уровни
        self.sizes - размеры уровня в клетках по x и y
        self.current_level - переменная, хранящая порядковый номер текущего уровня
        self.dictionary_of_levels_objects - словарь, ключем которого является порядковый номер уровня
        а значением по ключу является список объектов, которые берутся из групп объектов карты
        self.dictionary_of_types - словарь, который возвращает класс в зависимости от имени объекта
        """

        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h
        self.opened_in_full_screen = True

        self.screen = self.set_screen("change_size_type")
        self.filename_of_maps = ['data/maps/gob.tmx']
        self.level_maps = [pytmx.load_pygame(file_name) for file_name in self.filename_of_maps]
        self.sizes = [[level_map.height, level_map.width] for level_map in self.level_maps]
        self.current_level = 1

        self.tile_width = 100

        self.player_sprites = pygame.sprite.Group()
        self.pet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.inventory_group = pygame.sprite.Group()

        self.left_padding, self.top_padding = 0, 0

        self.players = [Entities.Player((self.window_size[0] // 2, self.window_size[1] // 2),
                                        'Player', 100, self.player_sprites, self.window_size, self.inventory_group)]
        self.dictionary_of_types = \
            {
                'wall': Wall,
                'table': Table,
                'armor': Armor,
                'stool': Stool,
                'cupboard': Cupboard,
                'stairs': Stairs,
                'bed': Bed,
                'decorative_ax': DecorativeAx,
            }

        self.dictionary_of_levels_objects = \
            {
                1: [[self.dictionary_of_types[obj.name](obj, self.tile_width, self.level_maps[0].tilewidth)
                     for obj in object_groups if self.dictionary_of_types[obj.name]]
                    for object_groups in self.level_maps[0].objectgroups],

                2: []
            }

        self.enemies = \
            [
                Entities.BaseEnemy((2935, 2570), 'enemy', 100, self.enemy_sprites, 'up'),
                Entities.BaseEnemy((4000, 2570), 'enemy', 100, self.enemy_sprites, 'up'),
                Entities.BaseEnemy((1935, 2570), 'enemy', 100, self.enemy_sprites, 'up')
            ]
        self.pets = []
        self.change_padding(-100, -100)

    def update_player_coord(self, keys=None, mouse=None):

        """
        вынес передвижение игрока в канвас для удобства
        :param keys: список нажатых клавишь
        :param mouse: клик мышки
        :return:
        """

        if keys is not None:

            left, top = self.players[0].move_on_wasd(keys, self.dictionary_of_levels_objects[1])
            self.change_padding(left, top)

            if keys[pygame.K_d]:
                self.players[0].move_direction = "right"
            elif keys[pygame.K_a]:
                self.players[0].move_direction = "left"

            self.animate_sprite(keys)

        if mouse is not None:
            pass

    def animate_sprite(self, keys):
        if not keys[pygame.K_w] and not keys[pygame.K_a] and not keys[pygame.K_s] and not keys[pygame.K_d]:
            if self.players[0].move_direction == "right":
                if random.randint(0, 100) > 70:
                    self.players[0].update("look around right")
            elif self.players[0].move_direction == "left":
                if random.randint(0, 100) > 70:
                    self.players[0].update("look around left")

        elif self.players[0].move_direction == "right":
            if keys[pygame.K_d]:
                self.players[0].update("move right")
            elif keys[pygame.K_w]:
                self.players[0].update("move right")
            elif keys[pygame.K_s]:
                self.players[0].update("move right")

        elif self.players[0].move_direction == "left":
            if keys[pygame.K_a]:
                self.players[0].update("move left")
            elif keys[pygame.K_d]:
                self.players[0].update("move left")
            elif keys[pygame.K_w]:
                self.players[0].update("move left")
            elif keys[pygame.K_s]:
                self.players[0].update("move left")

    def set_screen(self, action):
        """
        Accepts two types of action "window_size" and "change_size_type".
        "window_size" - changes the size of the window to a windowed view
        "change_size_type" - changes the type of the displayed window depending on the current view of its display.
        Windowed to full-screen, full-screen to windowed.

        Принимает два типа действия "window_size" и "change_size_type".
        "window_size" - изменяет размер окна на оконный вид
        "change_size_type" - изменяет тип отображаемого окна в зависимости от текущего вида его отображения.
        Оконный на полноэкранный, полноэкранный на оконный.

        :param action:
        :return:
        """
        self.opened_in_full_screen = not self.opened_in_full_screen
        if action == 'window_size':
            pygame.quit()
            pygame.init()
            return pygame.display.set_mode((self.window_size[0], self.window_size[1] - 70))
        elif action == "change_size_type":
            if self.opened_in_full_screen:
                pygame.quit()
                pygame.init()
                return pygame.display.set_mode((self.window_size[0], self.window_size[1] - 70))
            else:
                return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render(self):
        """
        Пробегается по видимым слоям текущего уровня и отрисовывает их на экране
        """

        screen = self.screen.copy()
        for layer in self.level_maps[self.current_level - 1].visible_layers:
            if layer.__class__.__name__ == 'TiledTileLayer':
                for x, y, gid in layer:

                    """
                    layer - картеж вида (0, 0, 0), где первые 2 числа координаты по x и y, 
                    последняя индекс слоя, на котором мы и находим картинку
                    """
                    tile = self.level_maps[self.current_level - 1].get_tile_image_by_gid(gid)
                    if tile is not None:
                        tile = pygame.transform.scale(tile, (self.tile_width, self.tile_width))
                        screen.blit(tile, (x * self.tile_width + self.left_padding,
                                           y * self.tile_width + self.top_padding))

        self.pet_sprites.draw(screen)
        self.enemy_sprites.draw(screen)

        if self.players[0].inventory_state == 'open':
            self.inventory_group.draw(screen)
        else:
            for enemy in self.enemies:
                enemy.move(self.dictionary_of_levels_objects[1])
        self.player_sprites.draw(screen)
        self.screen.blit(screen, (0, 0))

    def change_padding(self, left=0, top=0):

        """
        эта функция сдвигает все клетки по оси x на left или по оси y на top
        """

        self.left_padding += left
        self.top_padding += top

        # пробегаемся по объектам Wall, и изменяем его положение в зависимости от переданных параметров
        for walls_group in self.dictionary_of_levels_objects[1]:
            for wall in walls_group:
                wall.rect.x += left
                wall.rect.y += top

        for enemy in self.enemies:
            enemy.rect.x += left
            enemy.rect.y += top
            for collision_img in enemy.collision_images:
                collision_img.rect.x += left
                collision_img.rect.y += top
            enemy.hp_bar.rect.x += left
            enemy.hp_bar.rect.y += top

    def set_inventory_cell_position(self, event):

        """
        :param event: какое-либо событие
        :return: просто прирывает выполнение функции
        """

        # начало смены координат клетки
        if event.type == pygame.MOUSEBUTTONDOWN and not self.players[0].change_inventory_cell_position:

            mouse_coord = event.pos
            self.players[0].first_inventory_cell = [
                [cell for cell in cell_group
                 if (cell.rect.x <= mouse_coord[0] <= cell.rect.x + cell.size and
                     cell.rect.y <= mouse_coord[1] <= cell.rect.y + cell.size)]
                for cell_group in self.players[0].inventory.inventory_cells]

            self.players[0].first_inventory_cell = [item for item in self.players[0].first_inventory_cell if item]

            if not self.players[0].first_inventory_cell:
                self.players[0].change_inventory_cell_position = False
                self.players[0].first_inventory_cell = self.players[0].second_inventory_cell = None
                self.players[0].difference_x = self.players[0].difference_y = 0
                return

            self.players[0].first_inventory_cell = self.players[0].first_inventory_cell[0][0]
            self.players[0].difference_x = mouse_coord[0] - self.players[0].first_inventory_cell.rect.x
            self.players[0].difference_y = mouse_coord[1] - self.players[0].first_inventory_cell.rect.y
            self.players[0].change_inventory_cell_position = True

        # передвижение клетки
        if event.type == pygame.MOUSEMOTION and self.players[0].change_inventory_cell_position:
            self.players[0].first_inventory_cell.rect.x = event.pos[0] - self.players[0].difference_x
            self.players[0].first_inventory_cell.rect.y = event.pos[1] - self.players[0].difference_y

        # конец смены координат клетки
        if event.type == pygame.MOUSEBUTTONUP and self.players[0].change_inventory_cell_position:
            self.players[0].change_inventory_cell_position = False

            self.players[0].second_inventory_cell = \
                [[cell for cell in cell_group if pygame.sprite.collide_rect(cell, self.players[0].first_inventory_cell)]
                 for cell_group in self.players[0].inventory.inventory_cells]

            self.players[0].second_inventory_cell = [[cell for cell in item if cell != self.players[0].first_inventory_cell]
                                          for item in self.players[0].second_inventory_cell]
            self.players[0].second_inventory_cell = [item for item in self.players[0].second_inventory_cell if item]

            if not self.players[0].second_inventory_cell:
                self.players[0].first_inventory_cell.rect.x, self.players[0].first_inventory_cell.rect.y = \
                    self.players[0].first_inventory_cell.base_position
                return

            self.players[0].second_inventory_cell = self.players[0].second_inventory_cell[0][0]
            self.players[0].second_inventory_cell.rect.x, self.players[0].second_inventory_cell.rect.y = \
                self.players[0].first_inventory_cell.base_position
            self.players[0].first_inventory_cell.rect.x, self.players[0].first_inventory_cell.rect.y = \
                self.players[0].second_inventory_cell.base_position

            self.players[0].first_inventory_cell.base_position = self.players[0].first_inventory_cell.rect.x, self.players[0].first_inventory_cell.rect.y
            self.players[0].second_inventory_cell.base_position = \
                self.players[0].second_inventory_cell.rect.x, self.players[0].second_inventory_cell.rect.y


class Obstacle:
    def __init__(self, obj, tile_size, base_tile_width):

        """
        :param obj: это объект, реаизованый в карте, из него берутся свойства, начальные координаты и т.д.
        :param tile_size: - размер клетки, он фиксирован и равен 100
        :param base_tile_width: - базовый размер тайла, то есть самой картинки (32*32)
        self.rect и self.image нужны для проверки столкновений со стеной
        """

        self.x = int(obj.x * tile_size / base_tile_width)
        self.y = int(obj.y * tile_size / base_tile_width)
        self.width = int(obj.width * tile_size / base_tile_width)
        self.height = int(obj.height * tile_size / base_tile_width)
        self.tile_size = tile_size
        self.obj = obj
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)


class Wall(Obstacle):
    pass


class Table(Obstacle):
    pass


class Armor(Obstacle):
    pass


class Stool(Obstacle):
    pass


class Cupboard(Obstacle):
    pass


class Stairs(Obstacle):
    pass


class Bed(Obstacle):
    pass


class DecorativeAx(Obstacle):
    pass
