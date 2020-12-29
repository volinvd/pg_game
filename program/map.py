import pygame
import os
import pytmx

import program.Entities as Entities
import program.Weapons as Weapons
import program.Enchantment as Enchantment


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

        self.left_padding, self.top_padding = 0, 0

        self.players = [Entities.Player((self.window_size[0] // 2, self.window_size[1] // 2),
                                        'Player', 100, self.player_sprites)]

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

        self.enemies = []
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
        if mouse is not None:
            pass

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

        self.player_sprites.draw(screen)
        self.pet_sprites.draw(screen)
        self.enemy_sprites.draw(screen)
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


