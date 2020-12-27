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

        self.enemies = []
        self.pets = []

    def get_field(self, file_name, directory):

        """
        Будем использовать для хранения объектов, в том числе и стен
        """

        fullname = os.path.join(directory, file_name)
        with open(fullname, 'r', encoding='utf8') as level:
            field = [line.split() for line in level.readlines()]
        return [[Cell((row, col),
                      self.cell_size,
                      field[row][col],
                      self.dictionary_of_cell_group[field[row][col]])
                 for col in range(len(field[row]))] for row in range(len(field))]

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
                        self.screen.blit(tile, (x * self.tile_width + self.left_padding,
                                                y * self.tile_width + self.top_padding))

        self.player_sprites.draw(self.screen)
        self.pet_sprites.draw(self.screen)
        self.enemy_sprites.draw(self.screen)

    def change_padding(self, left=0, top=0):

        """
        эта функция сдвигает все клетки по оси x на left или по оси y на top
        """

        self.left_padding += left
        self.top_padding += top


def main():
    pygame.init()

    canvas = Canvas()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                canvas.screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                canvas.screen = canvas.set_screen("window_size")

        keys = pygame.key.get_pressed()
        if keys:
            """
            Если есть нажатые клавиши, вызывается передвижения метод игрока
            Он возвращает перемещения по оси x и y
            Потом мы сдвигаем канвас на эти значения
            """
            left, top = canvas.players[0].move_on_wasd(keys)
            canvas.change_padding(left, top)

        canvas.screen.fill((200, 200, 200))
        canvas.render()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
