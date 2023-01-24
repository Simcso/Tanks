# Импорт библиотек
import pygame
import runpy
import sys
import os


def load_image(name, color_key=None):  # Получаем имя и ключ
    # Получаем путь
    path = os.path.join('data', name)
    # Получаем путь(конструкция для запуска как exe-файл)
    fullname = os.path.join(sys._MEIPASS, path) if hasattr(sys, "_MEIPASS") else path
    # Проверяем существует ли файл
    if not os.path.isfile(fullname):
        # Выводим сообщение
        print(f"Файл с изображением '{fullname}' не найден")
        # Завершаем программу
        sys.exit()
    # Загружаем спрайт
    image = pygame.image.load(fullname)
    # Проверяем нужно ли заменить фон
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    # Возвращаем спрайт
    return image


def load_music(name):  # Получаем имя
    # Получаем путь
    path = os.path.join('data', name)
    # Возвращаем музыку(конструкция для запуска как exe-файл)
    return pygame.mixer.Sound(os.path.join(sys._MEIPASS, path) if hasattr(sys, "_MEIPASS") else path)

# Запускаем pygame
pygame.init()

# Основные константы
FPS = 60
clock = pygame.time.Clock()

# Загрузка музыки
menu_music = load_music('menu_music.wav')
win_music = load_music('win_music.wav')
lose_music = load_music('lose_music.wav')


class Button:  # Класс кнопки
    # Получаем экран для добавления кнопки, x, y, ширину, высоту, текст, название шрифта и размер шрифта
    def __init__(self, screen, x, y, width, height, text='кнопка', font_name='Arial', font_size=40):
        # Задаём переменные
        self.screen, self.x, self.y, self.width, self.height, self.text = screen,  x, y, width, height, text
        self.font_name, self.font_size = font_name, font_size
        self.colors = {'normal': '#ffffff', 'cursor': '#666666'}
        # Создаём поверхность
        self.Surface = pygame.Surface((self.width, self.height))
        self.Surface.set_colorkey(0)
        self.Surface.set_alpha(20)
        self.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        # Создаём шрифт нужно цвета
        self.Text = pygame.font.SysFont(self.font_name, self.font_size).render(self.text, True, self.colors['normal'])
        # Проверяем находиться ли курсор на кнопке
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            # Создаём шрифт нужно цвета
            self.Text = pygame.font.SysFont(self.font_name, self.font_size).\
                render(self.text, True, self.colors['cursor'])
            # Проверяем нажата ли кнопка
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                return True
        # Добавляем текст на поверхность
        self.Surface.blit(self.Text, [self.Rect.width / 2 - self.Text.get_rect().width / 2,
                                      self.Rect.height / 2 - self.Text.get_rect().height / 2])
        # Накладываем поверхность поверх экрана
        self.screen.blit(self.Surface, self.Rect)


class Text:  # Класс текста
    # Получаем экран для добавления текста, x, y, ширину, высоту, текст, название шрифта и размер шрифта
    def __init__(self, screen, x, y, width, height, text='кнопка', font_name='Arial', font_size=40):
        # Задаём переменные
        self.screen, self.x, self.y, self.width, self.height, self.text = screen,  x, y, width, height, text
        self.font_name, self.font_size = font_name, font_size
        # Создаём поверхность
        self.Surface = pygame.Surface((self.width, self.height))
        self.Surface.set_colorkey(0)
        self.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Создаём шрифт
        self.Text = pygame.font.SysFont(self.font_name, self.font_size).render(self.text, True, '#ffffff')
        # Добавляем текст на поверхность
        self.Surface.blit(self.Text, [self.Rect.width / 2 - self.Text.get_rect().width / 2,
                                      self.Rect.height / 2 - self.Text.get_rect().height / 2])
        # Накладываем поверхность поверх экрана
        self.screen.blit(self.Surface, self.Rect)


def menu(screen, restart=False):  # Получаем экран и понимаем нужно ли перезапустить программу
    # Останавливаем всю музыку
    pygame.mixer.stop()
    # Проигрываем музыку меню
    menu_music.play()
    # Создаём фон нужного размера
    fon = pygame.transform.scale(load_image('fon.png'), (screen.get_width(), screen.get_height()))
    # Накладываем фон на экран
    screen.blit(fon, (0, 0))
    # Создаём текст
    Text(screen, (screen.get_width() - 320) // 2, (screen.get_height() - 300) // 2, 320, 80, 'Танки', 'Arial', 100)
    # Создаём кнопки
    start_game_button = Button(screen, (screen.get_width() - 100) // 2, (screen.get_height() - 100) // 2, 120, 45,
                               'Играть')
    exit_button = Button(screen, (screen.get_width() - 220) // 2, screen.get_height() // 2, 220, 45, 'Выход из игры')
    # Цикл
    while True:
        # Проверяем нажата ли кнопка "Играть"
        if start_game_button.update():
            # Проверяем нужно ли перезапустить программу
            if restart:
                # Перезапускаем программу
                runpy.run_module('game')
            return  # начинаем игру
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли клавиша esc или кнопка "Вернуться в меню"
            if (event.type == pygame.KEYDOWN and event.scancode == 41) or exit_button.update():
                # Завершаем программу
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(FPS)


def pause(screen):  # Получаем экран
    # Останавливаем всю музыку
    pygame.mixer.pause()
    # Создаём кнопки
    resume_game_button = Button(screen, (screen.get_width() - 190) // 2, (screen.get_height() - 100) // 2, 190, 45,
                                'Продолжить')
    return_to_menu_button = Button(screen, (screen.get_width() - 260) // 2, screen.get_height() // 2, 260, 45,
                                   'Вернутся в меню')
    # Создаём поверхность
    surface = pygame.Surface((screen.get_width(), screen.get_height()))
    # Изменяем alpha-канал, тем самым делая затемнение экрана
    surface.set_alpha(40)
    for _ in range(7):
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
    # Создаём текст
    Text(screen, (screen.get_width() - 320) // 2, (screen.get_height() - 340) // 2, 320, 120, 'Пауза', 'Arial', 100)
    # Цикл
    while True:
        # Проверяем нажата ли кнопка "Вернуться в меню"
        if return_to_menu_button.update():
            # Запускаем меню
            menu(screen, True)
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли клавиша esc или кнопка "Продолжить"
            if (event.type == pygame.KEYDOWN and event.scancode == 41) or resume_game_button.update():
                # Запускаем всю музыку
                pygame.mixer.unpause()
                return  # Продолжаем игру
        pygame.display.flip()
        clock.tick(FPS)


def lose(screen):  # Получаем экран
    # Останавливаем всю музыку
    pygame.mixer.stop()
    # Проигрываем музыку проигрыша
    lose_music.play()
    # Создаём кнопки
    restart_game_button = Button(screen, (screen.get_width() - 220) // 2, (screen.get_height() - 100) // 2, 220, 45,
                                 'Начать заново')
    return_to_menu_button = Button(screen, (screen.get_width() - 260) // 2, screen.get_height() // 2, 260, 45,
                                   'Вернутся в меню')
    # Создаём поверхность
    surface = pygame.Surface((screen.get_width(), screen.get_height()))
    # Изменяем alpha-канал, тем самым делая затемнение экрана
    surface.set_alpha(40)
    for _ in range(7):
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
    # Создаём текст
    Text(screen, (screen.get_width() - 450) // 2, (screen.get_height() - 340) // 2, 450, 120, 'Поражение', 'Arial', 100)
    # Цикл
    while True:
        # Проверяем нажата ли кнопка "Начать заново"
        if restart_game_button.update():
            # Перезапускаем программу
            runpy.run_module('game')
        # Проверяем нажата ли кнопка "Вернуться в меню"
        if return_to_menu_button.update():
            # Запускаем меню
            menu(screen)
        # Просто заглушка(без неё почему-то не работает =D)
        for _ in pygame.event.get():
            pass
        pygame.display.flip()
        clock.tick(FPS)


def win(screen):  # Получаем экран
    # Останавливаем всю музыку
    pygame.mixer.stop()
    # Проигрываем музыку победы
    win_music.play()
    # Создаём кнопки
    restart_game_button = Button(screen, (screen.get_width() - 220) // 2, (screen.get_height() - 100) // 2, 220, 45,
                                 'Начать заново')
    return_to_menu_button = Button(screen, (screen.get_width() - 260) // 2, screen.get_height() // 2, 260, 45,
                                   'Вернутся в меню')
    # Создаём поверхность
    surface = pygame.Surface((screen.get_width(), screen.get_height()))
    # Изменяем alpha-канал, тем самым делая затемнение экрана
    surface.set_alpha(40)
    for _ in range(7):
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
    # Создаём текст
    Text(screen, (screen.get_width() - 450) // 2, (screen.get_height() - 340) // 2, 450, 120, 'Победа', 'Arial', 100)
    # Цикл
    while True:
        # Проверяем нажата ли кнопка "Начать заново"
        if restart_game_button.update():
            # Перезапускаем программу
            runpy.run_module('game')
        # Проверяем нажата ли кнопка "Вернуться в меню"
        if return_to_menu_button.update():
            # Запускаем меню
            menu(screen)
        # Просто заглушка(без неё почему-то не работает =D)
        for _ in pygame.event.get():
            pass
        pygame.display.flip()
        clock.tick(FPS)
