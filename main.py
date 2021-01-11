import pygame
import os
import sys
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from program import map


def main(level):
    pygame.init()

    canvas = map.Canvas(level)
    running = True

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


class MenuWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/menu_ui/menu.ui', self)
        self.setWindowTitle("Dungeon Pig Launcher")

        self.settings_window = None

        self.setupUI()

    def setupUI(self):
        self.levels.setVisible(False)
        self.settings.clicked.connect(self.load_settings)
        self.new_game.clicked.connect(self.load_base_levels)

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
        self.main_menu.hide()

        self.first_level.clicked.connect(self.load_game_level)
        self.second_level.clicked.connect(self.load_game_level)
        self.third_level.clicked.connect(self.load_game_level)


    def load_game_level(self):
        self.close()
        main(int(self.sender().text()))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = MenuWidget()
    menu.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())