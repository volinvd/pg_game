import pygame


class Canvas:
    def __init__(self):
        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h - 70
        self.curr_screen = 0
        self.cell_sizes = [int((self.window_size[1] + 70) / 7), int(self.window_size[1] / 7)]
        self.matrix = [[0] * 7 for _ in range(int(self.window_size[0] / 7))]

    def set_screen(self):
        self.curr_screen = not self.curr_screen
        if self.curr_screen:
            pygame.quit()
            pygame.init()
            return pygame.display.set_mode(self.window_size)
        else:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render(self, screen):
        cell_size = self.cell_sizes[self.curr_screen]
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[x])):
                pygame.draw.rect(screen, 'white', (x * cell_size + 3, y * cell_size,
                                                   cell_size, cell_size), 3)


def main():
    pygame.init()

    canvas = Canvas()
    screen = canvas.set_screen()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                screen = canvas.set_screen()

        screen.fill((0, 0, 0))
        canvas.render(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
