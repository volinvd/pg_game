import pygame
import os
import pprint


class CollisionImage(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface((size[2], size[3]), pygame.SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color("white"), [size[0], size[1],
                                                             size[2], size[3]], 1)
        self.rect = pygame.Rect(size[0], size[1], size[2], size[3])


class Entity(pygame.sprite.Sprite):
    def __init__(self, position, name, health, group):
        super().__init__(group)

        self.image = pygame.Surface((90, 90))
        pygame.draw.rect(self.image, pygame.Color("blue"), [position[0], position[1], 90, 90])
        self.rect = pygame.Rect(position[0], position[1], 90, 90)
        self.position = position
        self.move_direction = "right"

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        self.speed_by_x, self.speed_by_y = 15, 15

        self.name = name
        self.health = health
        self.size = 120

    def get_damage(self, damage):
        self.health -= damage

    def load_image(self, name, directory, color_key=None):

        fullname = os.path.join(directory, name)
        image = pygame.image.load(fullname)

        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        return image

    def animate(self, sheet, columns, rows, x, y, sp_description):
        self.frames = {}
        self.cut_sheet(sheet, columns, rows, sp_description)
        self.cur_frame = ("move right", 0)
        self.image = self.frames["move right"][0]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows, sp_description):
        self.sp_description = sp_description
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)

        for key, list_with_coordinates in self.sp_description.items():
            frame_list = []

            for coordinate in list_with_coordinates:
                frame_location = (self.rect.w * coordinate[0], self.rect.h * coordinate[1])
                print(frame_location)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame, (self.size, self.size))
                frame_list.append(frame)

            self.frames[key] = frame_list

        print(self.frames)
        print(self.sp_description)

    def update(self, direction):
        if self.cur_frame[0] == direction:
            print("in", self.cur_frame[1], direction)
            if self.cur_frame[1] - 1 == len(self.frames[direction]) or \
                    self.cur_frame[1] + 1 == len(self.frames[direction]):
                self.cur_frame = (direction, 0)

            else:
                self.cur_frame = (direction, self.cur_frame[1] + 1)
        else:
            self.cur_frame = (direction, 0)

        print("out", self.cur_frame[1], direction)

        self.image = self.frames[direction][self.cur_frame[1]]

    def a_star_pathfinding(self, level_walls, start_point, end_point, collision_images):
        path = [start_point]

        # List of nodes algorithm had checked
        closed_node_list = []

        window_width, window_height = pygame.display.get_surface().get_size()
        counter = 0

        # The algorithm stops when there are no blocks to check. This means there is no solution
        # The amount of blocks is calculated by the formula - screen size divided by block size
        while counter <= (window_width * window_height) // (self.size ** 2):
            counter += 1
            current_node = path[-1]

            # This is the amount the algorithm adds the coordinates of current node to find all adjacent nodes
            # Node size depends on the Entity.size variable
            possible_node_positions = [(0, -self.size), (0, self.size), (-self.size, 0), (self.size, 0),
                                       (-self.size, -self.size), (-self.size, self.size), (self.size, -self.size),
                                       (self.size, self.size)]

            # F value of the best node has to be high, in order to change to the best following node value
            best_node_f = 1000000000000
            best_node = current_node

            # Going through the list of adjacent nodes to find the best one
            for index, (x_coord, y_coord) in enumerate(possible_node_positions):
                obstacle_in_node = False

                # Checking if the adjacent node has an obstacle in it
                if index == 0:
                    obstacle_in_node = any([any([pygame.sprite.collide_rect(collision_images[0], wall) for wall in
                                                 wall_group]) for wall_group in level_walls])
                elif index == 1:
                    obstacle_in_node = any([any([pygame.sprite.collide_rect(collision_images[2], wall) for wall in
                                                 wall_group]) for wall_group in level_walls])
                elif index == 2:
                    obstacle_in_node = any([any([pygame.sprite.collide_rect(collision_images[3], wall) for wall in
                                                 wall_group]) for wall_group in level_walls])
                elif index == 3:
                    obstacle_in_node = any([any([pygame.sprite.collide_rect(collision_images[1], wall) for wall in
                                                 wall_group]) for wall_group in level_walls])
                elif index == 4:
                    obstacle_in_node = any([any([any([pygame.sprite.collide_rect(collision_images[0], wall)
                                                     for wall in wall_group]) for wall_group in level_walls]),
                                           any([any([pygame.sprite.collide_rect(collision_images[3], wall)
                                                     for wall in wall_group]) for wall_group in level_walls])])
                elif index == 5:
                    obstacle_in_node = any([any([any([pygame.sprite.collide_rect(collision_images[2], wall)
                                                      for wall in wall_group]) for wall_group in level_walls]),
                                            any([any([pygame.sprite.collide_rect(collision_images[3], wall)
                                                      for wall in wall_group]) for wall_group in level_walls])])
                elif index == 6:
                    obstacle_in_node = any([any([any([pygame.sprite.collide_rect(collision_images[0], wall)
                                                      for wall in wall_group]) for wall_group in level_walls]),
                                            any([any([pygame.sprite.collide_rect(collision_images[1], wall)
                                                      for wall in wall_group]) for wall_group in level_walls])])
                elif index == 7:
                    obstacle_in_node = any([any([any([pygame.sprite.collide_rect(collision_images[1], wall)
                                                      for wall in wall_group]) for wall_group in level_walls]),
                                            any([any([pygame.sprite.collide_rect(collision_images[2], wall)
                                                      for wall in wall_group]) for wall_group in level_walls])])

                # If there is no obstacle in the node, the player could go into it
                if not obstacle_in_node:
                    adjacent_node = current_node[0] + x_coord, current_node[1] + y_coord

                    # If the node was already checked, it can't be the best one
                    if adjacent_node not in closed_node_list:
                        # Value of distance in nodes between the start node and the current node
                        node_g_value = (len(path) - 1) * self.size
                        # Value of estimated distance between the current node and the end node
                        node_h_value = (adjacent_node[0] - end_point[0]) ** 2 + (adjacent_node[1] - end_point[1]) ** 2
                        # Value of total cost of the node (G + H)
                        node_f_value = node_g_value + node_h_value

                        if node_f_value < best_node_f:
                            closed_node_list.append(best_node)

                            # Changing the best node
                            best_node = adjacent_node
                            best_node_f = node_f_value
                        else:
                            closed_node_list.append(adjacent_node)

            path.append(best_node)

            if best_node not in closed_node_list:
                # Checking if the best node contains the end_point
                # If it does the algorithm found the path, if it doesn't algorithm continues searching
                if (end_point[0] in range(best_node[0] - self.size, best_node[0] + self.size + 1)
                        and end_point[1] in range(best_node[1] - self.size, best_node[1] + self.size + 1)):

                    path.append(end_point)
                    return path

            closed_node_list.append(best_node)
        # If the path couldn't be found, function returns None
        return None


class Player(Entity):
    def __init__(self, position, name, health, group):
        super().__init__(position, name, health, group)

        """
        obstacles - список, который хранит то, с чем персонаж не может контактировать (стена, преграда)
        """

        self.image = self.load_image('player.png', 'data/sprites/entities/Player/')
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position

        sp_description = {"look around right": [(x, 0) for x in range(0, 13)],
                          "move right": [(x, 1) for x in range(0, 8)],
                          "beat right up": [(x, 2) for x in range(0, 10)],
                          "beat right down": [(x, 3) for x in range(0, 10)],
                          "sweeping edge beat right": [(x, 4) for x in range(0, 8)],
                          "jump right": [(x, 5) for x in range(0, 10)],
                          "fall from the portal right": [(x, 7) for x in range(0, 7)],
                          "look around left": [(x, 8) for x in range(0, 13)],
                          "move left": [(x, 9) for x in range(0, 8)],
                          "beat left up": [(x, 11) for x in range(0, 10)],
                          "beat left down": [(x, 12) for x in range(0, 10)],
                          "sweeping edge beat left": [(x, 13) for x in range(0, 8)],
                          "jump left": [(x, 14) for x in range(0, 6)],
                          "fall from the portal left": [(x, 15) for x in range(0, 7)]}

        spritesheet_img = self.load_image("Adventurer Sprite Sheet v1.1.png", "data\sprites\spritesheets")
        self.animate(spritesheet_img, 13, 16, self.rect.x, self.rect.y, sp_description)

        # получинеие данных из изображения персонажа
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h

        # список стен вокруг персонажа
        self.collision_images = [CollisionImage((x + 10, y, w - 10, 10)),
                                 CollisionImage((x + w, y + 10, 10, h - 10)),
                                 CollisionImage((x + 10, y + h, w - 10, 10)),
                                 CollisionImage((x, y + 10, 10, h - 10))]

    def move_with_keyboard(self, keys, level_walls):

        """
        flag = True
        for wall_group in level_walls:
            for wall in wall_group:
                if pygame.sprite.collide_rect(self.collision_images[0], wall):
                    flag = False
        if flag:
            ...
        этот однообразный код при ходьбе проверяет столкновение
        с группой спрайтов, помеченных как припятствие при инициализации
        функция возвращает перемещение по x и y
        так как двигаем мы canvas, а он главнее, чем игрок
        """

        # передвижение по оси y
        y = x = 0
        if keys[pygame.K_w]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[0], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                y = self.speed_by_y

        elif keys[pygame.K_s]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[2], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                y = -self.speed_by_y

        # передвижение по оси x
        if keys[pygame.K_a]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[3], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                x = self.speed_by_x

        elif keys[pygame.K_d]:
            flag = not any([any([pygame.sprite.collide_rect(self.collision_images[1], wall) for wall in wall_group])
                            for wall_group in level_walls])
            if flag:
                x = -self.speed_by_x
        return x, y

    def move_with_mouse_click(self, level_walls):
        # List for the path written down in a form of (+- self.speed_by_x, +- self.speed_by_y)
        path_increments = []

        # Getting the position of the mouse after mouse click
        mouse_click_coords = pygame.mouse.get_pos()

        # This variable is a flag, that checks if the mouse was clicked not on the floor
        # (on the decorative items, walls or air)
        prohibited_sprites_not_clicked = not any([any([sprite for sprite in wall
                                                       if sprite.rect.collidepoint(mouse_click_coords)])
                                                  for wall in level_walls])

        if prohibited_sprites_not_clicked:
            path = Entity.a_star_pathfinding(self, level_walls, (self.rect.x + self.size // 2, self.rect.y +
                                                                 self.size // 2), mouse_click_coords,
                                             self.collision_images)
            # If the algorithm found the path we divide given path by increments equal to self.speed_by_x/y
            if path is not None:

                # Going through the path list
                for index, (current_node_x, current_node_y) in enumerate(path[:-1]):
                    next_node_x, next_node_y = path[index + 1][0], path[index + 1][1]

                    # Getting the amount of increments by finding distance between current
                    # and next node and dividing it by self.speed_by_x
                    amount_of_increments = round(round(((current_node_x - next_node_x) ** 2 +
                                                        (current_node_y - next_node_y) ** 2) ** 0.5) // self.speed_by_x)
                    # Dividing our path into increments
                    for _ in range(amount_of_increments):
                        if current_node_x + self.size == next_node_x and current_node_y + self.size == next_node_y:
                            path_increments.append((-self.speed_by_x, -self.speed_by_y))
                        elif current_node_x + self.size == next_node_x and current_node_y - self.size == next_node_y:
                            path_increments.append((-self.speed_by_x, self.speed_by_y))
                        elif current_node_x - self.size == next_node_x and current_node_y + self.size == next_node_y:
                            path_increments.append((self.speed_by_x, -self.speed_by_y))
                        elif current_node_x - self.size == next_node_x and current_node_y - self.size == next_node_y:
                            path_increments.append((self.speed_by_x, self.speed_by_y))
                        elif current_node_x + self.size == next_node_x:
                            path_increments.append((-self.speed_by_x, 0))
                        elif current_node_x - self.size == next_node_x:
                            path_increments.append((self.speed_by_x, 0))
                        elif current_node_y + self.size == next_node_y:
                            path_increments.append((0, -self.speed_by_y))
                        elif current_node_y - self.size == next_node_y:
                            path_increments.append((0, self.speed_by_y))

        return path_increments


class BaseEnemy(Entity):
    pass
