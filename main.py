import pygame
import os
import sys
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from program import map


def load_image(name, directory, color_key=None):
    fullname = os.path.join(directory, name)
    image = pygame.image.load(fullname)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Message(pygame.sprite.Sprite):
    def __init__(self, filename, directory, screen_size, group):
        super().__init__(group)
        self.image = load_image(filename, directory)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = (screen_size[1] - self.rect.h) // 2
        self.screen_size = screen_size

    def update_coord(self):

        if self.rect.x < (self.screen_size[0] - self.rect.w) // 2:
            self.rect.x += 10


def main(level):
    pygame.init()

    canvas = map.Canvas(level)
    running = True
    control_mode = 'keyboard'
    k = 0
    player_death_number = 60
    win = False
    message_group = pygame.sprite.Group()
    message = None
    while running:
        if canvas.players[0].death and player_death_number > 0:
            player_death_number -= 1

        if all([enemy.death for enemy in canvas.enemies[canvas.current_level]]) and player_death_number > 0:
            win = True
            player_death_number -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_F11:
                canvas.screen = canvas.set_screen("change_size_type")

            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                global menu
                menu.setVisible(True)
                pygame.quit()
                return

            if event.type == pygame.KEYUP and \
                    (event.key == pygame.K_e or event.key == pygame.K_i) and canvas.minimap.state == 'base':
                if canvas.players[0].inventory_state == 'open':
                    canvas.players[0].inventory_state = 'close'
                else:
                    canvas.players[0].inventory_state = 'open'

            if event.type == pygame.KEYUP and event.key == pygame.K_m:
                if canvas.minimap.state == 'base':
                    canvas.minimap.state = 'open'
                else:
                    canvas.minimap.state = 'base'
                    canvas.minimap.koef = 1
                    canvas.minimap.top_padding = canvas.minimap.left_padding = 0

            if canvas.players[0].inventory_state == 'open':
                canvas.set_inventory_cell_position(event)
            if canvas.minimap.state == 'open':
                canvas.set_minimap_position(event)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    canvas.players[0].attack_with_mouse_click(canvas.enemies[canvas.current_level])
                    k = 4

        if control_mode == 'keyboard':
            keys = pygame.key.get_pressed()
            if keys:
                """
                Если есть нажатые клавиши, вызывается передвижения метод игрока
                Он возвращает перемещения по оси x и y
                Потом мы сдвигаем канвас на эти значения
                """
                canvas.update_player_coord(keys=keys)

        if k > 0:
            if canvas.players[0].move_direction == "right":
                canvas.players[0].update("beat right")
            elif canvas.players[0].move_direction == "left":
                canvas.players[0].update("beat left")
            k -= 1

        canvas.screen.fill((200, 200, 200))
        canvas.render()

        if player_death_number <= 0 and message is None:
            file_name = 'you_win.png' if win else 'gameover.png'
            directory = 'data/sprites/'

            message = Message(file_name, directory, canvas.window_size, message_group)
            player_death_number = 1
        if message is not None:
            message.update_coord()
            message_group.draw(canvas.screen)

        pygame.display.flip()
    pygame.quit()


class MenuWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/menu_ui/menu.ui', self)
        self.setWindowTitle("Dungeon Pig Launcher")

        self.settings_window = None

        self.setupUI()

    def setupUI(self):
        self.levels.setVisible(False)
        self.back_to_menu.setVisible(False)

        self.settings.clicked.connect(self.load_settings)
        self.new_game.clicked.connect(self.load_base_levels)

        self.back_to_menu.setIcon(QIcon('data/menu_ui/arrow.png'))
        self.back_to_menu.setIconSize(QSize(72, 72))

        self.new_game.setIcon(QIcon('data/menu_ui/Начать.png'))
        self.new_game.setIconSize(QSize(238, 70))

        self.settings.setIcon(QIcon('data/menu_ui/Настройки.png'))
        self.settings.setIconSize(QSize(238, 70))

        self.first_level.setIcon(QIcon('data/menu_ui/Уровень1.png'))
        self.first_level.setIconSize(QSize(68, 70))

        self.second_level.setIcon(QIcon('data/menu_ui/Уровень2.png'))
        self.second_level.setIconSize(QSize(68, 70))

        self.third_level.setIcon(QIcon('data/menu_ui/Уровень3.png'))
        self.third_level.setIconSize(QSize(68, 70))

    def load_settings(self):
        pass

    def load_base_levels(self):
        """Будет сбрасывать данные игры к базовым"""
        self.load_levels()

    def load_levels(self):
        self.levels.show()
        self.back_to_menu.show()
        self.main_menu.hide()

        self.back_to_menu.clicked.connect(self.load_main_menu)
        self.first_level.clicked.connect(self.load_game_level)
        self.second_level.clicked.connect(self.load_game_level)
        self.third_level.clicked.connect(self.load_game_level)

    def load_main_menu(self):
        self.levels.setVisible(False)
        self.back_to_menu.setVisible(False)

        self.main_menu.show()

    def load_game_level(self):
        print(self.sender())
        self.setVisible(False)
        main(int(self.sender().text()))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


menu = None
if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = MenuWidget()
    menu.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
