import pygame

import program.Entities as Entities
import program.Weapons as Weapons
import program.Enchantment as Enchantment


class Canvas:
    def __init__(self):
        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h - 70
        self.opened_in_full_screen = True
        self.cell_sizes = [int((self.window_size[1] + 70) / 7), int(self.window_size[1] / 7)]
        self.matrix = [[0] * 15 for _ in range(7)]

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
        cell_size = self.cell_sizes[self.opened_in_full_screen]
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[x])):
                pygame.draw.rect(screen, 'black', (y * cell_size + 3 + self.left, x * cell_size,
                                                   cell_size, cell_size), 3)

    def change_left_padding(self, left):
        self.left += left


def main():
    pygame.init()

    canvas = Canvas()
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
        player_sprite_group.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()