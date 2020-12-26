import pygame
import os

import program.Entities as Entities
import program.Weapons as Weapons
import program.Enchantment as Enchantment


class Cell(pygame.sprite.Sprite):
    def __init__(self, position, size, cell_type, sprite_group):

        super().__init__(sprite_group)

        """
        position - номер строки и столбца клетки
        sprite_group - группа спрайтов для отрисовки
        cell_type - тип клетки
        size - базовый размер клетки
        """

        # находим какую картинку необходимо загрузить (в зависимости от типа ячейки)
        if cell_type == 'surface':
            self.image = self.load_image('brick.png', 'data/sprites/surface/')
            self.image = pygame.transform.scale(self.image, (size, size))
            self.rect = self.image.get_rect()

        elif cell_type == 'wall':
            self.image = pygame.Surface((size, size))
            pygame.draw.rect(self.image, pygame.Color("white"), [size * position[1], size * position[0],
                                                                 size, size])
            self.rect = pygame.Rect(size * position[1], size * position[0], size, size)

        elif cell_type == 'empty':
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, pygame.Color((200, 200, 200)), [size * position[1], size * position[0],
                                                                         size, size])
            self.rect = pygame.Rect(size * position[1], size * position[0], size, size)

        # ставим на позицию
        self.rect.x = size * position[1]
        self.rect.y = size * position[0]
        self.position = position

    def load_image(self, name, directory, color_key=None):

        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname)

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image
        return image


class Canvas:
    def __init__(self):

        # получаем инфу о экране пользователя
        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h
        self.opened_in_full_screen = True

        # создаем размер клетки (полноэкранный режим)
        self.cell_size = int((self.window_size[1]) / 8)

        # группы спрайтов для поверхности (плоскость/сткны и пустые клетки)
        self.air_sprites = pygame.sprite.Group()
        self.surface_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()

        self.player_sprites = pygame.sprite.Group()
        self.pet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # словарь соответствия типов клеток с их группами
        self.dictionary_of_cell_group = {'empty': self.air_sprites,
                                         'surface': self.surface_sprites,
                                         'wall': self.wall_sprites}

        # читаем уровень из файла
        self.field = self.get_field('first_level.txt', 'data/levels/')
        self.players = []
        self.enemies = []
        self.pets = []

    def get_field(self, file_name, directory):

        """
        Функция обрабатывает файл с именем file_name в дирректории directory
        И возвращает матрицу, состоящую из объектов класса Cell.
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

    def render(self, screen):

        """
        эта функция отрисовывает все спрайты на screen
        """

        self.air_sprites.draw(screen)
        self.surface_sprites.draw(screen)
        self.wall_sprites.draw(screen)

        self.player_sprites.draw(screen)
        self.pet_sprites.draw(screen)
        self.enemy_sprites.draw(screen)

    def change_left_padding(self, left=0, top=0):

        """
        эта функция сдвигает все клетки по оси x на left или по оси y на top
        """

        for x in range(len(self.field)):
            for y in range(len(self.field[x])):
                self.field[x][y].rect.x += left
                self.field[x][y].rect.y += top


def main():
    pygame.init()

    canvas = Canvas()
    screen = canvas.set_screen("change_size_type")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                screen = canvas.set_screen("window_size")

        screen.fill((200, 200, 200))
        canvas.render(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
