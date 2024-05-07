# Импорт библиотек
import os
import sys
import runpy
import pygame
import sqlite3


# Основные константы
FPS = 60
TILE_WIDTH = TILE_HEIGHT = 60
VECTORS = {0: [0, 1], 1: [1, 0], 2: [0, -1], 3: [-1, 0]}
clock = pygame.time.Clock()

# Запускаем pygame
pygame.init()
# Создание группы спрайтов
all_tiles = pygame.sprite.Group()


def load_level(filename):  # Получаем название уровня
    lines = open(os.path.join('./levels', filename)).readlines()
    line, level_map,  = lines.pop(0).strip(), []
    while line:  # Пробегаемся по линиям уровня, пока не встретится пустая строка(разделитель карты уровня от констант)
        # Добавляем линию в карту уровня
        level_map.append(line)
        # Берём новую линию
        line = lines.pop(0).strip()
    # Возвращаем карту уровня и список всех констант
    return level_map,  {i[0]: int(i[1]) for i in [line.strip().split(' = ') for line in lines]}


def load_image(name, color_key=None):  # Получаем имя и ключ
    # Получаем путь
    path = os.path.join('data/sprites', name)
    # Получаем путь(конструкция для запуска как exe-файл)
    fullname = os.path.join(sys._MEIPASS, path) if hasattr(sys, "_MEIPASS") else path
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
    path = os.path.join('data/music', name)
    # Возвращаем музыку(конструкция для запуска как exe-файл)
    return pygame.mixer.Sound(os.path.join(sys._MEIPASS, path) if hasattr(sys, "_MEIPASS") else path)


# Загрузка музыки
menu_music = load_music('menu_music.wav')
win_music = load_music('win_music.wav')
lose_music = load_music('lose_music.wav')


class Text:  # Класс текста
    # Получаем экран для добавления текста, x, y, ширину, высоту, текст, название шрифта и размер шрифта
    def __init__(self, screen, x, y, width, height, text='Текст', font_name='Arial', font_size=40):
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

    def show(self):
        # Накладываем поверхность поверх экрана
        self.screen.blit(self.Surface, self.Rect)


class Button:  # Класс кнопки
    # Получаем экран для добавления кнопки, x, y, ширину, высоту, текст, название шрифта и размер шрифта
    def __init__(self, screen, x, y, width, height, text='Кнопка', font_name='Arial', font_size=40):
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


class SpriteButton(pygame.sprite.Sprite):  # Класс спрайта-кнопки
    # Получаем лист спрайтов, x, y, ширину, высоту, группу спрайтов и вектор(для поворота изображения)
    def __init__(self, sheet, x, y, width, height, group, vector=0):
        super().__init__(group)
        # Задаём переменные
        self.sheet, self.x, self.y, self.width, self.height, self.vector = sheet, x, y, width, height, vector
        # Нарезаем лист спрайтов на отдельные спрайты
        self.cut_sheet()
        # Задаём область листа спрайтов и передвигаем на координаты
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height()).move(self.x, self.y)

    def cut_sheet(self):
        # Создаём список спрайтов
        self.frames = [pygame.transform.scale(pygame.transform.rotate(self.sheet.subsurface(pygame.Rect((
                self.sheet.get_width() // 3 * i, 0), (self.sheet.get_width() // 3, self.sheet.get_height()))),
                90 * self.vector), (self.width, self.height)) for i in range(3)]

    def update(self):
        # Проверяем находиться ли курсор на кнопке
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # Выбираем нужный спрайт из списка
            self.image = self.frames[1]
            # Проверяем нажата ли кнопка
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                # Выбираем нужный спрайт из списка
                self.image = self.frames[2]
                return True
        else:
            # Выбираем нужный спрайт из списка
            self.image = self.frames[0]


class KeyAssignmentButton(pygame.sprite.Sprite):
    # Получаем экран для добавления кнопки, x, y, ширину, высоту, текст, название шрифта и размер шрифта
    def __init__(self, screen, sprites_group, key, x, y, text='Кнопка'):
        super().__init__(sprites_group)
        # Задаём переменные
        self.screen, self.group, self.key, self.x, self.y = screen, sprites_group, key, x, y
        self.width, self.height, self.text, self.db = len(text) * 20, 50, text, sqlite3.connect('Configs.db')
        # Создаём поверхность
        self.Surface = pygame.Surface((self.width, self.height))
        self.Surface.set_colorkey(0)
        self.Surface.set_alpha(20)
        self.Rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        # Создаём шрифт нужно цвета
        self.Text = pygame.font.SysFont('Arial', 40).render(self.text, True, '#ffffff')
        # Проверяем находиться ли курсор на кнопке
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            # Создаём шрифт нужно цвета
            self.Text = pygame.font.SysFont('Arial', 40).render(self.text, True, '#666666')
            # Проверяем нажата ли кнопка
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                while True:
                    event = pygame.event.wait()
                    # Проверяем нажал ли игрок на клавиши
                    if event.type == pygame.KEYDOWN:
                        # Подключаем базу данных
                        cur, key = self.db.cursor(), pygame.key.name(event.key).upper()
                        cur.execute(f'''UPDATE Key_assignment SET btn_name = "{key}" WHERE doing = 
                                        "{self.text.split('-')[0].strip()}" AND id_type = (SELECT id FROM 
                                        Types_of_key_assignment WHERE type = "{self.key}")''')
                        self.db.commit()
                        self.__init__(self.screen, self.group, self.key, self.x, self.y,
                                      f'{self.text.split("-")[0].strip()}   -   {key}')
                        key_assignment_menu()
                        return
        # Добавляем текст на поверхность
        self.Surface.blit(self.Text, [self.Rect.width / 2 - self.Text.get_rect().width / 2,
                                      self.Rect.height / 2 - self.Text.get_rect().height / 2])
        # Накладываем поверхность поверх экрана
        self.screen.blit(self.Surface, self.Rect)


class Tile(pygame.sprite.Sprite):  # Класс объекта
    def __init__(self, tile_type, pos_x, pos_y):
        # Инициализация класса и добавления его в нужные группы спрайтов
        super().__init__(all_tiles)
        # Добавляем текстуру спрайта
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


def menu(restart=False):
    # Создание экрана
    screen = pygame.display.set_mode()
    # Останавливаем всю музыку
    pygame.mixer.stop()
    # Проигрываем музыку меню
    menu_music.play()
    # Создаём фон нужного размера
    fon = pygame.transform.scale(load_image('fon.png'), (screen.get_width(), screen.get_height()))
    # Накладываем фон на экран
    screen.blit(fon, (0, 0))
    # Создаём текст
    name_text = Text(screen, (screen.get_width() - 320) // 2, (screen.get_height() - 300) // 2, 320, 80, 'Танки',
                     'Arial', 100)
    # Создаём кнопки
    start_game_button = Button(screen, (screen.get_width() - 100) // 2, (screen.get_height() - 100) // 2, 120, 45,
                               'Играть')
    key_assignment_button = Button(screen, (screen.get_width() - 310) // 2, (screen.get_height() - 20) // 2, 300, 45,
                                   'Назначения клавиш')
    exit_button = Button(screen, (screen.get_width() - 225) // 2, (screen.get_height() + 70) // 2, 220, 45,
                         'Выход из игры')
    # Цикл
    while True:
        # Проверяем нажата ли кнопка "Играть"
        if start_game_button.update():
            # Проверяем нужно ли перезапустить программу
            if restart:
                # Перезапускаем программу
                runpy.run_module('game')
            return  # начинаем игру
        # Проверяем нажата ли кнопка "Назначения клавиш"
        if key_assignment_button.update():
            key_assignment_menu()
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли клавиша esc или кнопка "Вернуться в меню"
            if (event.type == pygame.KEYDOWN and event.key == 27) or exit_button.update():
                # Завершаем программу
                pygame.quit()
                sys.exit()
        name_text.show()
        pygame.display.flip()
        clock.tick(FPS)


def key_assignment_menu():
    # Создание экрана
    screen = pygame.display.set_mode()
    # Создаём группу для кнопок
    buttons = pygame.sprite.Group()
    # Создаём фон нужного размера
    fon = pygame.transform.scale(load_image('fon.png'), (screen.get_width(), screen.get_height()))
    # Накладываем фон на экран
    screen.blit(fon, (0, 0))
    # Получаем настройки из базы данных
    cur = sqlite3.connect('Configs.db').cursor()
    res = cur.execute('''SELECT Types_of_key_assignment.type, doing, btn_name FROM Key_assignment 
                            INNER JOIN Types_of_key_assignment ON Types_of_key_assignment.id = 
                            Key_assignment.id_type''').fetchall()
    # Парсим ответ
    configs = {key: list(i[1:] for i in res if i[0] == key) for key in set(i[0] for i in res)}

    text_dist, i, last_dist = (screen.get_width() - sum([len(key) * 25 for key in configs])) // (len(configs) + 1), 1, 0
    for key in sorted(configs, reverse=True):
        Text(screen, i * text_dist + last_dist, (screen.get_height() - 550) // 2, len(key) * 25, 80, key, font_size=50)
        for keys in configs[key]:
            KeyAssignmentButton(screen, buttons, key, i * text_dist + last_dist, (screen.get_height() - 550)
                                // 2 + 50 * configs[key].index(keys) + 100, f'{keys[0]}   -   {keys[1]}')
        last_dist, i = len(key) * 20, i + 1
    # Цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == 27:
                # Запускаем меню
                menu(True)
                return
        try:
            buttons.update()
        except:
            pass
        # Проверяем закрыто ли меню назначения клавиш
        try:
            pygame.display.flip()
        except:
            return
        clock.tick(FPS)


def select_level_menu():
    # Создание экрана
    screen = pygame.display.set_mode()
    # Создаём группу для кнопок
    buttons = pygame.sprite.Group()
    # Создаём фон нужного размера
    fon = pygame.transform.scale(load_image('fon.png'), (screen.get_width(), screen.get_height()))
    # Накладываем фон на экран
    screen.blit(fon, (0, 0))
    # Получаем все уровни
    levels, current_level = os.listdir('./levels'), 0
    # Создаём кнопки
    right_arrow = SpriteButton(load_image('arrow.png', -1), 1000, 300, 100, 30, buttons, 3)
    left_arrow = SpriteButton(load_image('arrow.png', -1), 300, 300, 100, 30, buttons, 1)
    start_game_button = Button(screen, (screen.get_width() - 190) // 2, screen.get_height() // 2 + 100, 190, 45,
                               'Начать')
    return_to_menu_button = Button(screen, (screen.get_width() - 260) // 2, screen.get_height() // 2 + 150, 260, 45,
                                   'Вернутся в меню')
    # Создаём текст
    Text(screen, (screen.get_width() - 370) // 2, screen.get_height() // 2 - 350, 370, 120, 'Выбор уровня',
         'Arial', 70)
    Text(screen, (screen.get_width() - 1000) // 2, screen.get_height() // 2 - 260, 1000, 120,
         f'"{levels[current_level].split(".")[0]}"', 'Arial', 50)
    # Цикл
    while True:
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли кнопка "Вернуться в меню" или "Esc"
            if (event.type == pygame.KEYDOWN and event.key == 27) or return_to_menu_button.update():
                menu(True)
            # Проверяем нажата ли клавиша "Начать"
            if start_game_button.update():
                # Пытаемся загрузить уровень
                try:
                    return load_level(levels[current_level % len(levels)])
                except:
                    # Выводим ошибку
                    Text(screen, (screen.get_width() - 1000) // 2, screen.get_height() // 2 + 250, 1000, 120,
                         'Ошибка при загрузке уровня', 'Arial', 50)
            # Проверяем нажата ли одна из стрелок
            if right_arrow.update() or left_arrow.update():
                # Изменяем выбранный уровень
                if right_arrow.update():
                    current_level += 1
                if left_arrow.update():
                    current_level -= 1
                # Накладываем фон на экран
                screen.blit(fon, (0, 0))
                # Создаём текст
                Text(screen, (screen.get_width() - 370) // 2, screen.get_height() // 2 - 350, 370, 120,
                     'Выбор уровня', 'Arial', 70)
                Text(screen, (screen.get_width() - 1000) // 2, screen.get_height() // 2 - 260, 1000, 120,
                     f'"{levels[current_level % len(levels)].split(".")[0]}"', 'Arial', 50)
        buttons.update()
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def level_editor_menu():
    # Создание экрана
    screen = pygame.display.set_mode()
    # Создаём группу для кнопок
    buttons = pygame.sprite.Group()
    # Создаём фон нужного размера
    fon = pygame.transform.scale(load_image('fon.png'), (screen.get_width(), screen.get_height()))
    # Накладываем фон на экран
    screen.blit(fon, (0, 0))

    # Цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == 27:
                # Запускаем меню
                menu(True)
                return
        pygame.display.flip()
        clock.tick(FPS)
    

def pause(screen):
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
            menu(True)
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли клавиша "Esc" или кнопка "Продолжить"
            if (event.type == pygame.KEYDOWN and event.key == 27) or resume_game_button.update():
                # Запускаем всю музыку
                pygame.mixer.unpause()
                return  # Продолжаем игру
        pygame.display.flip()
        clock.tick(FPS)


def lose(screen):
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
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли кнопка "Начать заново"
            if restart_game_button.update():
                # Перезапускаем программу
                runpy.run_module('game')
            # Проверяем нажата ли кнопка "Вернуться в меню" или "Esc"
            if (event.type == pygame.KEYDOWN and event.key == 27) or return_to_menu_button.update():
                # Запускаем меню
                menu()
            pygame.display.flip()
            clock.tick(FPS)


def win(screen):
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
        # Проверяем все ивенты
        for event in pygame.event.get():
            # Проверяем нажата ли кнопка "Начать заново"
            if restart_game_button.update():
                # Перезапускаем программу
                runpy.run_module('game')
            # Проверяем нажата ли кнопка "Вернуться в меню" или "Esc"
            if (event.type == pygame.KEYDOWN and event.key == 27) or return_to_menu_button.update():
                # Запускаем меню
                menu()
            pygame.display.flip()
            clock.tick(FPS)
