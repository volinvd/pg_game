import pygame
import os
import pytmx
import random

import program.Entities as Entities


class Canvas:
    def __init__(self, level):

        """
        info - переменная, хранящая информацию о экране пользователя
        self.screen - главный экран для отрисоки
        self.filename_of_maps - список, в котором хранятся пути к файлам карт
        self.level_map - список, в котором хранятся все уровни
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
        self.filename_of_maps = ['data/maps/gob.tmx', 'data/maps/first.tmx', 'data/maps/first.tmx'][level - 1]
        self.level_map = pytmx.load_pygame(self.filename_of_maps)
        self.sizes = [self.level_map.height, self.level_map.width]
        self.current_level = level

        self.tile_width = 100

        self.player_sprites = pygame.sprite.Group()
        self.pet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.inventory_group = pygame.sprite.Group()
        self.medicine_chest_group = pygame.sprite.Group()

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
                'air': Air,
                'enemy': '',
                'medicine_chest': ''
            }

        self.dictionary_of_levels_objects = {
            level: [[self.dictionary_of_types[obj.name](obj, self.tile_width, self.level_map.tilewidth)
                     for obj in object_groups if self.dictionary_of_types[obj.name]]
                    for object_groups in self.level_map.objectgroups]}
        level_enemies = [[Entities.Orc((int(obj.x * self.tile_width / self.level_map.tilewidth),
                                        int(obj.y * self.tile_width / self.level_map.tilewidth)), 'enemy', 100,
                                       self.enemy_sprites, 'up')
                          for obj in object_groups if obj.name == 'enemy']
                         for object_groups in self.level_map.objectgroups]
        level_enemies = [[enemies for enemies in enemies_list if enemies]
                         for enemies_list in level_enemies if enemies_list][0]
        self.enemies = {
            level: level_enemies
        }
        self.medicine_chest = [[MedicineChest(obj, 50, self.level_map.tilewidth, self.medicine_chest_group)
                                for obj in object_groups if obj.name == 'medicine_chest']
                               for object_groups in self.level_map.objectgroups]
        self.medicine_chest = [[ap for ap in ap_list if ap]
                               for ap_list in self.medicine_chest if ap_list][0]

        self.pets = []
        self.minimap = MiniMap(self.level_map, self.players[0], self.window_size)
        dict_of_changing_padding = {1: (-100, -100),
                                    2: (-200, -200),
                                    3: (-200, -200)}
        self.change_padding(*dict_of_changing_padding[self.current_level])

    def update_player_coord(self, keys=None, mouse=None):

        """
        вынес передвижение игрока в канвас для удобства
        :param keys: список нажатых клавишь
        :param mouse: клик мышки
        :return:
        """
        self.animate_enemies_sprites()
        if self.players[0].death:
            self.players[0].update()
        else:
            if keys is not None:
                left, top = self.players[0].move_with_keyboard(keys,
                                                               self.dictionary_of_levels_objects[self.current_level])
                self.change_padding(left, top)

                if keys[pygame.K_d]:
                    self.players[0].move_direction = "right"
                elif keys[pygame.K_a]:
                    self.players[0].move_direction = "left"

                self.animate_player_sprite(keys)

            elif mouse is not None and not self.players[0].death:
                path_increments = \
                    self.players[0].move_with_mouse_click(self.dictionary_of_levels_objects[self.current_level])

                # Going through the list and using the function change_padding to move the player
                for left, top in path_increments:
                    self.change_padding(left, top)

    def animate_player_sprite(self, keys):
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

    def animate_enemies_sprites(self):
        for enemy in self.enemies[self.current_level]:

            if enemy.move_direction == "right":
                enemy.update("move right")
            elif enemy.move_direction == "left":
                enemy.update("move left")

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
        length = len(self.enemies[self.current_level])
        some_list = [enemy for enemy in self.enemies[self.current_level] if enemy.health > 0]
        if len(some_list) != length:
            self.enemy_sprites = pygame.sprite.Group()
            for enemy in self.enemies[self.current_level]:
                self.enemy_sprites.add(enemy)
                if not enemy.death:
                    self.enemy_sprites.add(enemy.hp_bar)
        if self.players[0].health <= 0:
            self.players[0].die()

        screen = self.screen.copy()
        for layer in self.level_map.visible_layers:
            if layer.__class__.__name__ == 'TiledTileLayer':
                for x, y, gid in layer:

                    """
                    layer - картеж вида (0, 0, 0), где первые 2 числа координаты по x и y, 
                    последняя индекс слоя, на котором мы и находим картинку
                    """
                    tile = self.level_map.get_tile_image_by_gid(gid)
                    if tile is not None:
                        tile = pygame.transform.scale(tile, (self.tile_width, self.tile_width))
                        screen.blit(tile, (x * self.tile_width + self.left_padding,
                                           y * self.tile_width + self.top_padding))

        self.pet_sprites.draw(screen)
        self.player_sprites.draw(screen)
        self.enemy_sprites.draw(screen)
        self.medicine_chest_group.draw(screen)

        if self.minimap.state == 'base':
            if self.players[0].inventory_state == 'open':
                self.inventory_group.draw(screen)
            else:
                for enemy in self.enemies[self.current_level]:
                    if enemy.attack_state:
                        enemy.tick += 1
                        enemy.update()
                        if enemy.tick == 30:
                            enemy.tick = 0
                            enemy.attack_state = False
                    if not enemy.player_in_vision(self.players[0].vision):
                        enemy.move(self.dictionary_of_levels_objects[self.current_level])
                    else:
                        enemy.chase_player(self.dictionary_of_levels_objects[self.current_level], self.players[0])
        if self.players[0].attack_state:
            self.players[0].tick += 1
            if self.players[0].tick == 7:
                self.players[0].tick = 0
                self.players[0].attack_state = False
        self.minimap.render(screen)
        self.screen.blit(screen, (0, 0))

    def change_padding(self, left=0, top=0):

        """
        эта функция сдвигает все клетки по оси x на left или по оси y на top
        """

        self.left_padding += left
        self.top_padding += top
        self.minimap.left_player_padding += left
        self.minimap.top_player_padding += top

        # пробегаемся по объектам Wall, и изменяем его положение в зависимости от переданных параметров
        for walls_group in self.dictionary_of_levels_objects[self.current_level]:
            for wall in walls_group:
                wall.rect.x += left
                wall.rect.y += top

        for enemy in self.enemies[self.current_level]:
            enemy.rect.x += left
            enemy.rect.y += top
            for collision_img in enemy.collision_images:
                collision_img.rect.x += left
                collision_img.rect.y += top
            enemy.hp_bar.rect.x += left
            enemy.hp_bar.rect.y += top
            enemy.vision.rect.x += left
            enemy.vision.rect.y += top

        for ap in self.medicine_chest:
            ap.rect.x += left
            ap.rect.y += top
            if pygame.sprite.collide_rect(ap, self.players[0].vision):
                ap.is_use = True
                self.players[0].heal()

        length = len(self.medicine_chest)
        self.medicine_chest = [ap for ap in self.medicine_chest if not ap.is_use]
        if len(self.medicine_chest) != length:
            self.medicine_chest_group = pygame.sprite.Group()
            for ap in self.medicine_chest:
                self.medicine_chest_group.add(ap)

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
    
    def set_minimap_position(self, event):

        """
        :param event: какое-либо событие
        :return: просто прирывает выполнение функции
        """

        if event.type == pygame.MOUSEBUTTONDOWN and self.minimap.state == 'open':
            if event.button == 4:
                self.minimap.koef += 1
            if event.button == 5:
                self.minimap.koef -= 1
            self.minimap.koef = 20 if self.minimap.koef > 20 else self.minimap.koef
            self.minimap.koef = 1 if self.minimap.koef < 1 else self.minimap.koef
        if event.type == pygame.MOUSEWHEEL and self.minimap.state == 'open':
            self.minimap.koef += event.y
            self.minimap.koef = 20 if self.minimap.koef > 20 else self.minimap.koef
            self.minimap.koef = 1 if self.minimap.koef < 1 else self.minimap.koef

        # начало смены координат миникарты
        if self.minimap.koef >= 6:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.minimap.change_position:

                mouse_coord = event.pos

                self.minimap.difference_x = mouse_coord[0]
                self.minimap.difference_y = mouse_coord[1]
                self.minimap.change_position = True

            # передвижение клетки
            if event.type == pygame.MOUSEMOTION and self.minimap.change_position:
                self.minimap.change_padding(event.pos[0] - self.minimap.difference_x,
                                            event.pos[1] - self.minimap.difference_y)
                self.minimap.difference_x = event.pos[0]
                self.minimap.difference_y = event.pos[1]

            # конец смены координат клетки
            if event.type == pygame.MOUSEBUTTONUP and self.minimap.change_position:
                self.minimap.change_position = False


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


class Air(Obstacle):
    pass


class MiniMap:
    def __init__(self, level_map, player, screen_size):
        self.level_map = level_map
        self.player = player
        self.left_padding, self.top_padding = 0, 0
        self.left_player_padding, self.top_player_padding = 0, 0
        self.tile_width = 5
        self.koef = 1
        self.state = 'base'
        self.difference_x = 0
        self.difference_y = 0
        self.change_position = False
        self.size = 0, 0
        self.screen_size = screen_size

    def render(self, screen):
        """
        Пробегается по видимым слоям текущего уровня и отрисовывает их на экране
        """
        if self.state == 'base':
            screen_2 = pygame.Surface((500 * round(self.koef), 300 * round(self.koef)), pygame.SRCALPHA)
            # фон для миникарты
            pygame.draw.rect(screen_2, (51, 51, 51, 200), (0, 0,
                                                           500 * round(self.koef), 300 * round(self.koef)))
            max_x = max_y = 0
            for layer in self.level_map.visible_layers:
                if layer.__class__.__name__ == 'TiledTileLayer':
                    for x, y, gid in layer:

                        if layer.name == 'пол' and gid in (4, 6):
                            pygame.draw.rect(screen_2, '#a9a9a9', (x * self.tile_width * round(self.koef),
                                                                   y * self.tile_width * round(self.koef),
                                                                   self.tile_width * round(self.koef),
                                                                   self.tile_width * round(self.koef)))
                        if x > max_x:
                            max_x = x
                        if y > max_y:
                            max_y = y
            x, y = (self.screen_size[0] - max_x * self.tile_width * round(self.koef),
                    self.screen_size[1] - max_y * self.tile_width * round(self.koef))

            screen.blit(screen_2, (x - 2, y - 2))
            x, y, w, h = (-self.left_player_padding // 20 + x + self.player.rect.x // 32 * 5 - self.screen_size[0] // 20,
                          -self.top_player_padding // 20 + y + self.player.rect.y // 32 * 5 - self.screen_size[1] // 20,
                          self.player.rect.w // 32 * 5, self.player.rect.h // 32 * 5)

            pygame.draw.rect(screen, 'blue', [x - 2, y - 2, w * round(self.koef), h * round(self.koef)])
        else:

            screen_2 = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            if self.koef < 6:
                self.left_padding = self.top_padding = 0
            max_x = max_y = 0
            for layer in self.level_map.visible_layers:
                if layer.__class__.__name__ == 'TiledTileLayer':
                    for x, y, gid in layer:

                        """
                        layer - картеж вида (0, 0, 0), где первые 2 числа координаты по x и y, 
                        последняя индекс слоя, на котором мы и находим картинку
                        """
                        tile = self.level_map.get_tile_image_by_gid(gid)
                        if tile is not None:
                            tile = pygame.transform.scale(tile,
                                                          (self.tile_width * round(self.koef), self.tile_width * round(self.koef)))
                            screen_2.blit(tile, (self.left_padding + x * self.tile_width * round(self.koef),
                                                 self.top_padding + y * self.tile_width * round(self.koef)))
                        if x > max_x:
                            max_x = x
                        if y > max_y:
                            max_y = y

            left = self.screen_size[0] - max_x * round(self.koef) * self.tile_width
            top = self.screen_size[1] - max_y * round(self.koef) * self.tile_width
            left //= 2
            top //= 2
            left = 2 if left < 0 else left
            top = 2 if top < 0 else top
            screen.blit(screen_2, (left, top))
            pygame.draw.rect(screen, 'red', [left, top, (max_x + 1) * round(self.koef) * self.tile_width,
                                             (max_y + 1) * round(self.koef) * self.tile_width], 2)
            self.size = max_x * round(self.koef) * self.tile_width, max_y * round(self.koef) * self.tile_width

    def change_padding(self, left=0, top=0):

        """
        эта функция сдвигает все клетки по оси x на left или по оси y на top
        """

        self.left_padding += left
        self.top_padding += top
        self.left_padding = 0 if self.left_padding > 0 else self.left_padding
        self.top_padding = 0 if self.top_padding > 0 else self.top_padding

        self.left_padding = -(self.size[0] - self.screen_size[0]) \
            if self.left_padding < -(self.size[0] - self.screen_size[0]) else self.left_padding

        self.top_padding = -(self.size[1] - self.screen_size[1]) \
            if self.top_padding < -(self.size[1] - self.screen_size[1]) else self.top_padding


class MedicineChest(pygame.sprite.Sprite):
    def __init__(self, obj, tile_size, base_tile_width, group):

        """
        :param obj: это объект, реаизованый в карте, из него берутся свойства, начальные координаты и т.д.
        :param tile_size: - размер клетки, он фиксирован и равен 100
        :param base_tile_width: - базовый размер тайла, то есть самой картинки (32*32)
        self.rect и self.image нужны для проверки столкновений со стеной
        """
        super().__init__(group)
        self.x = int(obj.x * tile_size * 2 / base_tile_width)
        self.y = int(obj.y * tile_size * 2 / base_tile_width)
        self.width = int(obj.width * tile_size / base_tile_width)
        self.height = int(obj.height * tile_size / base_tile_width)
        self.tile_size = tile_size
        self.obj = obj
        self.is_use = False

        self.image = self.load_image('dungetileset.png', 'data/sprites/spritesheets/tiles/')
        single_image = self.image.subsurface((48, 112, 16, 16))
        self.image = pygame.transform.scale(single_image, (tile_size, tile_size))
        self.rect = single_image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def load_image(self, name, directory, color_key=None):
        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname)

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        return image
