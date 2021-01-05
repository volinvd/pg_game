import pygame
import os

from program import map


def main():
    pygame.init()

    canvas = map.Canvas()
    running = True

    square_coordinate = None
    difference_x = 0
    difference_y = 0
    change_coord = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                canvas.screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                canvas.screen = canvas.set_screen("window_size")

            if event.type == pygame.KEYUP and (event.key == pygame.K_e or event.key == pygame.K_i):
                if canvas.players[0].inventory_state == 'open':
                    canvas.players[0].inventory_state = 'close'
                else:
                    canvas.players[0].inventory_state = 'open'

            if canvas.players[0].inventory_state == 'open':
                canvas.set_inventory_cell_position(event)
        keys = pygame.key.get_pressed()
        if keys and canvas.players[0].inventory_state == 'close':
            """
            Если есть нажатые клавиши, вызывается передвижения метод игрока
            Он возвращает перемещения по оси x и y
            Потом мы сдвигаем канвас на эти значения
            """
            canvas.update_player_coord(keys=keys)

        canvas.screen.fill((200, 200, 200))
        canvas.render()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
