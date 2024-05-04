import random
import pygame


# класс спрайтов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, y, sprite_sheet, scale):
        pygame.sprite.Sprite.__init__(self)

        self.animation_list = []

        # позволяет отслеживать стадию анимации
        self.frame_index = 0

        self.update_time = pygame.time.get_ticks()

        # случайное направление врага
        self.direction = random.choice([-1, 1])  # если влево, то -1, вправо 1

        # если враг движется вправо, то поменять направление изображения в правую сторону
        if self.direction == 1:
            self.flip = True
        else:
            self.flip = False

        # загрузка изображения из таблицы спрайтов (spritesheet)
        animation_steps = 6
        for animation in range(animation_steps):
            image = sprite_sheet.get_image(animation, 46, 30, scale, (0, 0, 0))
            image = pygame.transform.flip(image, self.flip, False)  # False - переворачивать в направлении X, а не Y

            # прозрачность изображения
            image.set_colorkey((0, 0, 0))

            # по окончанию цикла будет заполнен список с отдельными изображениями для каждого этапа анимации
            self.animation_list.append(image)

        # выбрать начальное изображать и создать прямоугольник
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()

        # задать расположение врага относительно выбора направления
        if self.direction == 1:
            self.rect.x = 0
        else:
            self.rect.x = SCREEN_WIDTH
        self.rect.y = y

    def update(self, scroll, SCREEN_WIDTH):
        # обновление анимации
        animation_cooldown = 50  # скорость выполнения анимации

        # обновлять изображение в зависимости от текущего кадра
        self.image = self.animation_list[self.frame_index]

        # если прошло достаточно времени с момента анимации, то перейти к следующему этапу анимации
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            # сбросить время обновления
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # если анимация закончилась, то запустить ее заново
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

        # движение врага
        self.rect.x += self.direction * 2  # фиксированная скорость в два раза больше
        self.rect.y += scroll

        # проверка если враг исчез с экрана
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()  # удаление экземпляра врага из группы спрайтов
