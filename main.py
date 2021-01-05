import pygame
import os

from program import map


def main():
    pygame.init()

    canvas = map.Canvas()
    running = True
    control_mode = 'mouse'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                canvas.screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                canvas.screen = canvas.set_screen("window_size")
        if control_mode == 'keyboard':
            keys = pygame.key.get_pressed()
            if keys:
                """
                Если есть нажатые клавиши, вызывается передвижения метод игрока
                Он возвращает перемещения по оси x и y
                Потом мы сдвигаем канвас на эти значения
                """
                canvas.update_player_coord(keys=keys)
        elif control_mode == 'mouse':
            mouse_clicked = pygame.mouse.get_pressed()[0]
            if mouse_clicked:
                """
                Если есть нажатие клавиши мыши, вызывается метод передвижения игрока
                Он возвращает перемещения по оси x и y
                Потом мы сдвигаем канвас на эти значения
                """
                canvas.update_player_coord(mouse=mouse_clicked)

        canvas.screen.fill((200, 200, 200))
        canvas.render()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
