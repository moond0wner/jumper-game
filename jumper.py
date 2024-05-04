# импортирование и инициализация
import pygame
import random
import os
from pygame.locals import *
from pygame import mixer
from spritesheet import Spritesheet
from enemy_on_game import Enemy

mixer.init()
pygame.init()

# настройки игрового окна
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# создание игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('JumPy')

# Цвета (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PANEL_COLOR = (166, 202, 240)

# шрифт
font_small = pygame.font.SysFont('Lucida_Sans', 18)
font_big = pygame.font.SysFont('Lucida_Sans', 24)

# настройка FPS
clock = pygame.time.Clock()
FPS = 60

# загрузка изображений
background = pygame.image.load('img/background.jpg').convert_alpha()
platform_img = pygame.image.load('img/platform.png').convert_alpha()

# загрузка разноцветных лягушек для выбора игроку
green_frog = pygame.image.load('img/GreenFrogIdle.png').convert_alpha()
blue_frog = pygame.image.load('img/BlueFrogIdle.png').convert_alpha()
purple_frog = pygame.image.load('img/PurpleFrogIdle.png').convert_alpha()

# загрузка спрайтов врага
enemy_img = pygame.image.load('img/sprite_enemy(46x30).png').convert_alpha()
enemy_sheet = Spritesheet(enemy_img)


# функция стартового меню
def start_menu():
    # установка и настройка звукового сопровождения для меню
    pygame.mixer.music.load('music & sound/menu_music.mp3')  # Come Play With Me - Kevin MacLeod
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1, 0.0)

    running = True
    while running:
        font_surface = pygame.font.SysFont('Lucida_Sans', 60)
        text_surface = font_surface.render("JumPy", True, WHITE)  # название игры

        font_surface2 = pygame.font.SysFont('Lucida_Sans', 18)
        text_surface2 = font_surface2.render("Нажмите SPACE чтобы начать играть", True, BLACK)  # для запуска игры

        screen.blit(background, (0, 0))
        screen.blit(text_surface, (100, 150))
        screen.blit(text_surface2, (30, 300))

        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if key[pygame.K_SPACE]:
                print("Нажата клавиши SPACE. Время выбрать персонажа!")
                select_frog()

        pygame.display.flip()


def select_frog():
    global green_frog, blue_frog, purple_frog
    # установка и настройка звукового сопровождения для меню
    pygame.mixer.music.load('music & sound/menu_music.mp3')  # Come Play With Me - Kevin MacLeod
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1, 0.0)

    # создание и настройка текста
    font_surface = pygame.font.SysFont('Lucida_Sans', 30)
    text_surface = font_surface.render("Выбери лягушку!", True, WHITE)  # текст предлагающий выбрать лягушку

    # настройка платформы
    platform = pygame.transform.scale(platform_img, (40, 10))

    # настройка лягушек
    green_frog_rect = green_frog.get_rect(topleft=(178, 275))
    blue_frog_rect = blue_frog.get_rect(topleft=(3, 270))
    purple_frog_rect = purple_frog.get_rect(topleft=(348, 280))

    # переменная которая вернет выбор лягушки
    selected_frog = None

    running = True
    while running:

        # отображение бг и текста
        screen.blit(background, (0, 0))
        screen.blit(text_surface, (60, 150))

        # отображение платформ
        for i in range(3):
            screen.blit(platform, (175 * i, 300))

        # отображение лягушек
        screen.blit(green_frog, (178, 275))
        screen.blit(blue_frog, (3, 270))
        screen.blit(purple_frog, (348, 280))

        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and green_frog_rect.collidepoint(pos):
                    game_loop('green')
                    print("Green")
                    running = False
                if pygame.mouse.get_pressed()[0] and blue_frog_rect.collidepoint(pos):
                    game_loop('blue')
                    print('Blue')
                    running = False
                if pygame.mouse.get_pressed()[0] and purple_frog_rect.collidepoint(pos):
                    game_loop('purple')
                    print("Purple")
                    running = False

        pygame.display.flip()

    print(selected_frog)


def game_loop(color):
    print(f"Игра запущена с объектом: {color}")
    frog_player = color

    # переменные
    GRAVITY = 1
    MAX_PLATFORMS = 10
    SCROLL_THRESHOLD = 200
    scroll = 0
    background_scroll = 0
    score = 0
    game_over = False
    fade_count = 0

    # загрузка и настройка звукового сопровождения для основной игры
    pygame.mixer.music.load('music & sound/main_music.mp3')  # Pixel Peeker Polka – Faster - Kevin MacLeod.
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1, 0.0)
    jump_fx = pygame.mixer.Sound('music & sound/jump.wav')
    death_fx = pygame.mixer.Sound('music & sound/death.wav')
    jump_fx.set_volume(0.5)
    death_fx.set_volume(0.5)

    # функция вывода текста на экран
    def draw_text(text, font, color, x, y):
        image = font.render(text, True, color)
        screen.blit(image, (x, y))

    # функция для рисования заднего фона

    def draw_bg(background_scroll):
        screen.blit(background, (0, 0 + background_scroll))
        screen.blit(background, (0, -600 + background_scroll))  # Второй фон будет нарисован над первым на 600 пикселей
        # По мере прокрутки экрана, фон никогда не закончится, потому что за ним последует второй, а потом снова первый.
        # И так циклически.

    # рисование информационной панели
    def draw_panel():
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 30))
        pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
        draw_text("Очки: " + str(score), font_small, WHITE, 0, 0)

    # запись максимального балла в txt файл
    if os.path.exists('max_score.txt'):
        with open('max_score.txt', 'r') as file:
            max_score = int(file.read())  # если этого файла не существует, то приравниваем к нулю
    else:
        max_score = 0

    # ИГРОК
    class Player():
        def __init__(self, x, y, jumper_image):
            self.image = jumper_image
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.width = 30
            self.height = 33
            self.image.set_colorkey(WHITE)
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.center = (x, y)
            self.vel_y = 0  # скорость в направлении Y; # если переменная отрицательная, то игрок летит вверх
            self.flip = False

        def move(self):
            scroll = 0

            # d - дельта - изменение величины
            dx = 0  # изменение в координате X
            dy = 0  # изменение в координате Y

            # обработка нажатий клавиш
            key = pygame.key.get_pressed()
            if key[pygame.K_a]:
                dx -= 10
                self.flip = True
            if key[pygame.K_d]:
                dx = 10
                self.flip = False

            # гравитация
            self.vel_y += GRAVITY
            dy += self.vel_y  # увеличение координаты Y означает что игрок передвигается вниз по экрану

            # проверка на то, не выходит ли игрок за пределы экрана
            if self.rect.left + dx < 0:
                dx = -self.rect.left
            if self.rect.right + dx > SCREEN_WIDTH:
                dx = SCREEN_WIDTH - self.rect.right

            # проверка столкновений с платформой
            for platform in platform_group:
                # столкновение в Y направлении
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверка находится ли игрок над платформой
                    if self.rect.bottom < platform.rect.centery:
                        if self.vel_y > 0:
                            self.rect.bottom = platform.rect.top
                            dy = 0
                            self.vel_y = -20
                            jump_fx.play()

            # проверка если игрок отскочил в верхнюю часть экрана
            if self.rect.top <= SCROLL_THRESHOLD:
                # если игрок совершает прыжок
                if self.vel_y < 0:
                    scroll = -dy

            # обновить положение
            self.rect.x += dx
            self.rect.y += dy + scroll
            # при достижении порога прокрутки, игрок остается на месте так как значение равно нулю

            # создание маски
            # маска в отличие от прямоугольника позволяет точно определить столкновение по пикселям
            self.mask = pygame.mask.from_surface(self.image)

            return scroll

        def draw(self):
            screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 10, self.rect.y - 10))
            # False - переворачивать в направлении X, а не Y

    # ПЛАТФОРМА
    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, width, moving):
            # унаследуем функциональность классов спрайтов pygame
            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.transform.scale(platform_img, (width, 10))
            self.moving = moving

            # счетчик движения
            self.move_count = random.randint(0, 50)

            # случайная скорость для каждой платформы
            self.speed = random.randint(1, 2)

            # случайное направление платформы
            self.direction = random.choice([-1, 1])  # если влево, то -1, вправо 1

            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

        def update(self, scroll):
            # если это движущиеся платформа, то она будет перемещаться из стороны в сторону по X
            if self.moving == True:
                self.move_count += 1
                self.rect.x += self.direction * self.speed

            # Если платформа полностью сдвинулась или уперлась в стену, то изменяется ее направление.
            # Так как координата X и Y в pygame находится в верхней левой части экрана
            # то это объясняет то, что если левая часть платформы меньше 0 (то есть вышла за пределы экрана)
            # то изменить ее направление на противоположное.
            if self.move_count >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction *= -1
                self.move_count = 0

            # обновить вертикальное положение платформы
            self.rect.y += scroll  # это определяет как далеко находятся платформы на экране когда игрок прыгает

            # проверка если платформа исчезла с экрана
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()  # удаление платформы

    if frog_player == "green":
        jumper = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, green_frog)
    elif frog_player == "blue":
        jumper = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, blue_frog)
    elif frog_player == "purple":
        jumper = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, purple_frog)

    # группа спрайтов
    platform_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()

    # создание стартовой НЕПОДВИЖНОЙ платформы
    platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
    platform_group.add(platform)

    # ИГРОВОЙ ЦИКЛ
    running = True
    while running:

        # задаем частоту
        clock.tick(FPS)

        # если игра не закончена
        if not game_over:

            # движение игрока
            scroll = jumper.move()

            # рисовка фона
            background_scroll += scroll  # пока игра продолжается это переменная будет увеличиваться;

            # scroll обнуляется когда игрок отклоняется от порога прокрутки
            if background_scroll >= 600:
                background_scroll = 0
            draw_bg(background_scroll)

            # создание платформ
            if len(platform_group) < MAX_PLATFORMS:
                # платформы создаются случайным образом (по размерам и расположению),
                # чтобы на следующей попытке они не повторялись.
                p_w = random.randint(40, 60)
                p_x = random.randint(0, SCREEN_WIDTH - p_w)
                p_y = platform.rect.y - random.randint(80, 120)  # используется платформа которая создана раннее;
                # таким образом это помогает отслеживать где находилась предыдущая платформа и отталкиваться от нее.

                # задаем тип платформ; 1 - движущиеся, 2 - статичные.
                p_type = random.randint(1, 2)

                # Добавление движущихся платформ по достижению 500 очков
                if p_type == 1 and score > 500:
                    p_moving = True
                else:
                    p_moving = False
                platform = Platform(p_x, p_y, p_w, p_moving)
                platform_group.add(platform)

            # обновление платформ
            platform_group.update(scroll)

            # создание врагов по достижению 1500 очков
            if len(enemy_group) == 0 and score > 1500:
                enemy = Enemy(SCREEN_WIDTH, 100, enemy_sheet, 1.5)
                enemy_group.add(enemy)

            # обновление врагов
            enemy_group.update(scroll, SCREEN_WIDTH)

            # обновление очков
            if scroll > 0:
                score += scroll

            # линия показывающая последнее максимальное количество очков набранное игроком
            # это линия появиться когда игрок будет приближаться к своему рекорду по очкам
            pygame.draw.line(screen, WHITE, (0, score - max_score + SCROLL_THRESHOLD),
                             (SCREEN_WIDTH, score - max_score + SCROLL_THRESHOLD), 3)
            draw_text("Максимум очков!", font_small, WHITE, SCREEN_WIDTH - 300, score - max_score + SCROLL_THRESHOLD)

            # рисовка спрайтов
            platform_group.draw(screen)
            jumper.draw()
            enemy_group.draw(screen)

            # рисовка панели
            draw_panel()

            # проверка завершения игры
            # если упал, то есть пропал с экрана
            if jumper.rect.top > SCREEN_HEIGHT:
                game_over = True  # это означает если игрок опустился ниже экрана, игра заканчивается
                death_fx.play()
                pygame.mixer.music.stop()

            # столкновение с врагом
            # Если произошло первоначальное прямоугольное столкновение
            if pygame.sprite.spritecollide(jumper, enemy_group, False):
                # искать более точное определение
                if pygame.sprite.spritecollide(jumper, enemy_group, False, pygame.sprite.collide_mask):
                    game_over = True
                    death_fx.play()
                    pygame.mixer.music.stop()
        else:
            if fade_count < SCREEN_WIDTH:  # пока счетчик затемнения меньше ширины экрана
                fade_count += 5  # он будет увеличиваться (экран будет затухать)
                for y in range(0, 6, 2):  # 6 прямоугольников для затухания, 3 по каждой стороне
                    pygame.draw.rect(screen, BLACK,
                                     (0, y * 100, fade_count, SCREEN_HEIGHT // 6))  # затухает с левой стороны
                    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_count, (y + 1) * 100, SCREEN_WIDTH,
                                                     SCREEN_HEIGHT // 6))  # с правой стороны экрана
            else:
                draw_text("Игра окончена!", font_big, WHITE, 100, 200)
                draw_text("Очки: " + str(score), font_big, WHITE, 100, 250)
                draw_text("Нажмите Enter чтобы начать игру заново", font_small, WHITE, 20, 300)

                # обновить максимальный балл
                if score > max_score:
                    max_score = score
                    with open('max_score.txt', 'w') as file:
                        file.write(str(max_score))

                key = pygame.key.get_pressed()
                if key[pygame.K_RETURN]:
                    # сбросить настройки
                    game_over = False
                    score = 0
                    scroll = 0
                    pygame.mixer.music.play()
                    fade_count = 0  # этот счетчик нужно сбросить поскольку, после второй попытки затухания не будет так как
                    # значение счетчика равно ширине экрана.

                    # вернуть на стартовую позицию
                    jumper.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

                    # очистить платформы
                    platform_group.empty()

                    # сбросить врагов
                    enemy_group.empty()

                    # создание стартовой НЕПОДВИЖНОЙ платформы
                    platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
                    platform_group.add(platform)
                    # по сколько game_over = false, то все остальные платформы будут загружены

        # обработчик событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # обновить максимальный балл
                if score > max_score:
                    max_score = score
                    with open('max_score.txt', 'w') as file:
                        file.write(str(max_score))
                running = False

        # обновление
        pygame.display.update()

    pygame.quit()





if __name__ == "__main__":
    start_menu()  # Запуск главной функции
