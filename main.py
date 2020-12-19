import pygame


class Canvas:
    def __init__(self):
        info = pygame.display.Info()
        self.window_size = info.current_w, info.current_h - 60
        self.curr_screen = 0

    def set_screen(self):
        self.curr_screen = not self.curr_screen
        if self.curr_screen:
            pygame.quit()
            pygame.init()
            return pygame.display.set_mode(self.window_size)
        else:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render(self, screen):
        pass


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
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
