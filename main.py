import pygame
import os

import program.Entities as Entities
import program.Weapons as Weapons
import program.Enchantment as Enchantment


class Cell(pygame.sprite.Sprite):
    def __init__(self, position, group, screen_size, size, left):

        super().__init__(group)

        """
        
        position - номер строки и столбца клетки
        group - группа спрайтов для отрисовки
        screen_size - азмер экрана в пикселях, нужен для вычисления размера клетки
        size - базовый размер клетки
        left - отстп слева
        
        """

        self.image = self.load_image('brick.png', 'data/sprites/surface/')

        self.image = pygame.transform.scale(self.image, (size, size))

        self.rect = self.image.get_rect()

        self.rect.x = size * position[1]
        self.rect.y = size * position[0]

        self.position = position
        self.left = left

        self.screen_size = screen_size

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

    def set_size(self, size):
        self.image = pygame.transform.scale(self.image, (size, size))

        self.rect = self.image.get_rect()

        self.rect.x = size * self.position[1] + self.left
        self.rect.y = size * self.position[0]


class Canvas:
    def __init__(self, group):

        """

        переменная group хранит в себе группу спрайтов,
        к коорой будут добавляться спрайты ячеек.

        """

        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h - 70
        self.opened_in_full_screen = True

        self.rect = pygame.Rect(0, 0, info.current_w, info.current_h - 70)

        self.cell_sizes = [int((self.window_size[1] + 70) / 7), int(self.window_size[1] / 7)]

        self.matrix = [[Cell((i, j), group, (info.current_w, info.current_h),
                             self.cell_sizes[0], 0) for j in range(15)] for i in range(7)]
        self.group = group

        self.left = 0

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
        self.set_cell_size(self.cell_sizes[self.opened_in_full_screen])
        if action == 'window_size':
            pygame.quit()
            pygame.init()
            return pygame.display.set_mode(self.window_size)
        elif action == "change_size_type":
            if self.opened_in_full_screen:
                pygame.quit()
                pygame.init()
                return pygame.display.set_mode(self.window_size)
            else:
                return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render(self, screen):
        pass

    def set_cell_size(self, size):
        self.group = pygame.sprite.Group()
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[x])):
                self.matrix[x][y].set_size(size)

    def change_left_padding(self, left):
        self.left += left
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[x])):
                self.matrix[x][y].rect.x += left


def main():
    pygame.init()

    ground = pygame.sprite.Group()
    canvas = Canvas(ground)
    screen = canvas.set_screen("change_size_type")

    player_sprite_group = pygame.sprite.Group()
    player = Entities.Player([0, 0], 'Player', 100, player_sprite_group, canvas.window_size, canvas)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                screen = canvas.set_screen("window_size")

            keys = pygame.key.get_pressed()
            if keys:
                player.move(keys)

        screen.fill((200, 200, 200))
        canvas.render(screen)

        ground.draw(screen)
        player_sprite_group.draw(screen)

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
