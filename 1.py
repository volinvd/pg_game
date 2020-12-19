import os
import pygame


def load_image(name, color_key=None):
    fullname = os.path.join('data/sprites/', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def show_sprite(sprite, group, koef):
    img = load_image('chort_run_anim_f3.png')
    img_size = img.get_rect().size
    img = pygame.transform.scale(img, (img_size[0] * koef, img_size[1] * koef))

    sprite.image = img
    sprite.rect = [100, 100]
    group.add(sprite)


def main():
    size = 1440, 800
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Миникарта')

    # группа, содержащая все спрайты
    all_sprites = pygame.sprite.Group()

    image = load_image('chort_run_anim_f3.png')
    img_size = image.get_rect().size
    image = pygame.transform.scale(image, (img_size[0], img_size[1]))

    sprite = pygame.sprite.Sprite(all_sprites)
    sprite.image = image
    sprite.rect = [100, 100]

    running = True
    running_spr = False
    k = 1
    fps = 60
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                running_spr = True
                k = 1

        screen.fill(pygame.Color("white"))
        if running_spr:
            show_sprite(sprite, all_sprites, k)
            k += 1
            all_sprites.draw(screen)
        clock.tick(fps)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
