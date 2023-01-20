# Импорт библиотек
import pygame
from load_level import load_level
from wave_algoritm import wave, matrix, trail
from shoot_algoritm import try_shoot, object_matrix
from interface import load_image, menu, pause, lose, win
# Основные константы
FPS = 60
TILE_WIDTH = TILE_HEIGHT = 60
VECTORS = {0: [0, 1], 1: [1, 0], 2: [0, -1], 3: [-1, 0]}

# Назначения клавиш
TANKS = {'G': {'Вперёд': 26, 'Влево': 4, 'Назад': 22, 'Вправо': 7, 'Выстрел': 8},
         'Y': {'Вперёд': 82, 'Влево': 80, 'Назад': 81, 'Вправо': 79, 'Выстрел': 44},
         'W': {'Вперёд': 'Вперёд', 'Влево': 'Влево', 'Назад': 'Назад', 'Вправо': 'Вправо', 'Выстрел': 'Выстрел'}}

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
all_animated_sprites = pygame.sprite.Group()
all_booms = pygame.sprite.Group()
cant_move_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
friendly_tanks_group = pygame.sprite.Group()
enemy_tanks_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()

# Создание экрана
screen = pygame.display.set_mode()

# Загрузка спрайтов
tile_images = {'unbreakable_wall': load_image('unbreakable_wall.png'),
               'empty': load_image('flor.png'),
               'water': load_image('water.png'),
               'base': load_image('crown.png', -1),
               'grass': load_image('grass.png', -1),
               'wall': [load_image('wall_6.png', -1), load_image('wall_5.png', -1), load_image('wall_4.png', -1),
                        load_image('wall_3.png', -1), load_image('wall_2.png', -1), load_image('wall_1.png', -1),
                        load_image('wall.png', -1)]}
fire_image = load_image("fire.png", -1)
boom_image = load_image("booms.png", -1)
spawn_image = load_image("spawn.png", -1)
tanks = {'G': load_image('green_tank.png', -1), 'Y': load_image('yellow_tank.png', -1),
         'W': load_image('white_tank.png', -1)}
bullets = {'G': load_image('green_bullet.png', -1), 'Y': load_image('yellow_bullet.png', -1),
           'W': load_image('white_bullet.png', -1)}

# Загрузка уровня
level_map, CONSTANTS = load_level('level')

# Создание матрицы карты(пустые клетки / металлические стены)
object_matrix = object_matrix(level_map)


def generate_level(level):  # Создание спрайтов по полученному уровню
    green_tank, yellow_tank, base, x, y = None, None, None, None, None
    # Перебираем каждый символ уровня и создаём нужный объект
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('unbreakable_wall', x, y)
            elif level[y][x] == '=':
                Tile('water', x, y)
            elif level[y][x] == 'S':
                EnemySpawn(x, y)
            elif level[y][x] == '/':
                Tile('empty', x, y)
                Tile('grass', x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                Wall(x, y)
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                base = Base(x, y)
            elif level[y][x] == 'G':
                Tile('empty', x, y)
                green_tank = Tank(x, y, CONSTANTS['GREEN_TANK_VECTOR'], 'G')
            elif level[y][x] == 'Y':
                Tile('empty', x, y)
                yellow_tank = Tank(x, y, CONSTANTS['YELLOW_TANK_VECTOR'], 'Y')
    # Возвращаем танки и базу
    return green_tank, yellow_tank, base


class Tile(pygame.sprite.Sprite):  # Класс объекта
    def __init__(self, tile_type, pos_x, pos_y):
        # Список типов спрайтов и их групп
        types = {'grass': grass_group, 'water': cant_move_sprites, 'empty': all_sprites,
                 'unbreakable_wall': [cant_move_sprites, walls_group]}
        # Инициализация класса и добавления его в нужные группы спрайтов
        super().__init__(all_sprites, types[tile_type] if tile_type in types else '')
        # Добавляем текстуру спрайта
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


class Wall(pygame.sprite.Sprite):  # Класс объекта кирпичной стены
    def __init__(self, pos_x, pos_y):
        # Инициализация класса и добавления его в нужные группы спрайтов
        super().__init__(all_sprites, cant_move_sprites, walls_group)
        # Прочность стены
        self.durability = 6
        # Добавляем текстуру спрайта по его прочности
        self.image = tile_images['wall'][self.durability]
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def update(self):
        # Проверяем столкнулась ли пуля со стеной
        if pygame.sprite.spritecollideany(self, bullets_group):
            # Отнимаем прочность
            self.durability -= 1
            # Меняем текстуру спрайта по прочности
            self.image = tile_images['wall'][self.durability]
            # Проверяем сломали ли мы стену
            if self.durability == -1:
                # Создаём анимацию взрыва
                AnimatedSprite(boom_image, 15, 1, self.rect.x, self.rect.y, 2, all_booms)
                # Удаляем спрайт
                self.kill()


class Base(pygame.sprite.Sprite):  # Класс базы(короны)
    def __init__(self, pos_x, pos_y):
        # Инициализация класса и добавления его в нужные группы спрайтов
        super().__init__(all_sprites, cant_move_sprites)
        # Добавляем текстуру спрайта
        self.image = tile_images['base']
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def update(self):
        # Проверяем попали ли в базу вражеские пули
        if pygame.sprite.spritecollideany(self, pygame.sprite.Group([i for i in bullets_group.sprites()
                                                                     if i.color in 'W'])):
            # Создаём анимацию взрыва
            AnimatedSprite(boom_image, 15, 1, self.rect.x, self.rect.y, 2, all_booms)
            # Поражение
            lose(screen)


class EnemySpawn(pygame.sprite.Sprite):  # Класс места появления вражеских танков
    def __init__(self, pos_x, pos_y):
        # Инициализация класса и добавления его в нужную группу спрайтов
        super().__init__(all_sprites)
        # Добавляем текстуру спрайта и задаём переменные
        self.image, self.time, self.can_spawn = tile_images['empty'], 0, True
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def update(self):
        # Проверяем можем ли создать танк
        if not self.can_spawn:
            # Добавляем время к таймеру
            self.time += 1
            # Проверяем прошёл ли откат создания танка
            if self.time > CONSTANTS['CD_FOR_SPAWN']:
                # Записываем, что можем создать танк и обнуляем таймер
                self.can_spawn, self.time = True, 0
        # Проверяем можем ли создать танк и не превышает ли количество танков ограничения
        if self.can_spawn and CONSTANTS['MAX_ENEMY_TANKS'] and len(enemy_tanks_group) + \
                len([0 for i in all_animated_sprites if i.sheet == spawn_image]) \
                < CONSTANTS['MAX_ENEMY_TANKS_ON_SCREEN']:
            # Создаём анимацию появления танка
            AnimatedSprite(spawn_image, 9, 1, self.rect.x, self.rect.y, 7, '')
            # Уменьшаем количество оставшихся танков
            CONSTANTS['MAX_ENEMY_TANKS'] -= 1
            # Записываем, что не можем создать танк
            self.can_spawn = False


class Tank(pygame.sprite.Sprite):  # Класс танка(игрока)
    def __init__(self, pos_x, pos_y, vector, color):
        # Инициализация класса и добавления его в нужную группу спрайтов
        super().__init__(friendly_tanks_group, all_sprites)
        # Добавляем текстуру спрайта с нужным вектором и задаём переменные
        self.color, self.x_list, self.y_list = color, [], []
        self.image, self.reload, self.hp = pygame.transform.rotate(tanks[self.color], 90 * vector), 0, 3
        self.vector, self.can_shoot, self.not_moves = vector, True, True
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def shoot(self):  # Функция выстрела
        # Проверяем перезарядилось ли орудие
        if self.can_shoot:
            # Создаём пулю
            Bullet(self.rect.x, self.rect.y, self.vector, self.color)
            # Список сдвигов по вектору
            vectors = {0: [0, -60], 1: [-60, -12.5], 2: [-12.5, 60], 3: [60, 0]}
            # Создаём анимацию выстрела
            AnimatedSprite(fire_image, 3, 1, self.rect.x + vectors[self.vector][0],
                           self.rect.y + vectors[self.vector][1], 10, '', self.vector)
            # Орудие перезаряжается
            self.can_shoot = False

    def update(self):
        # Проверяем идёт ли анимация движения танка
        if self.x_list and self.y_list:
            # Получаем координаты во время анимации движения
            x = self.x_list.pop(0) if len(self.x_list) > 1 else self.x_list[0]
            y = self.y_list.pop(0) if len(self.y_list) > 1 else self.y_list[0]
            # Перемещаем танк
            self.rect = self.image.get_rect().move(x, y)
            # Проверяем закончилась ли анимация
            if len(self.x_list) == 1 and len(self.y_list) == 1:
                # Танк полностью перемещён
                self.rect = self.image.get_rect().move(self.x_list[0], self.y_list[0])
                # Очищаем списки с координатами для анимации
                self.x_list, self.y_list = [], []
                # Танк закончил движение
                self.not_moves = True
        # Проверяем не попала ли в танк вражеская пуля
        if pygame.sprite.spritecollideany(self, pygame.sprite.Group([i for i in bullets_group.sprites()
                                                                     if i.color == 'W'])):
            # Создаём анимацию взрыва
            AnimatedSprite(boom_image, 15, 1, self.rect.x, self.rect.y, 2, all_booms)
            # Удаляем спрайт
            self.kill()
        # Проверяем перезарядилось ли орудие
        if not self.can_shoot:
            # Добавляем время к таймеру
            self.reload += 1
            # Проверяем перезарядилось ли орудие
            if self.reload > CONSTANTS['RELOAD']:
                # Записываем, что орудие перезаряжено и обнуляем таймер
                self.can_shoot, self.reload = True, 0

    def do(self, code):
        # Стреляем или двигаемся в зависимости от команды
        self.shoot() if code == TANKS[self.color]['Выстрел'] else self.step(code)

    def step(self, code):
        # Проверяем двигается ли танк в данный момент
        if self.not_moves:
            # Список векторов для поворота танка
            vectors = {TANKS[self.color]['Вправо']: -1, TANKS[self.color]['Влево']: 1}
            # Проверяем является ли команда поворотом
            if code in vectors:
                # Получаем новый вектор после поворота
                self.vector = (self.vector + vectors[code]) % 4
                # Переворачиваем спрайт в зависимости от вектора
                self.image = pygame.transform.rotate(self.image, 90 * vectors[code])
            else:
                # Получаем координаты танка
                pos_x, pos_y = self.rect.x, self.rect.y
                # Список векторов для передвижения танка
                steps = {TANKS[self.color]['Вперёд']: -1, TANKS[self.color]['Назад']: 1}
                # Получаем конечные координаты после хода
                x, y = pos_x + (TILE_WIDTH * VECTORS[self.vector][0]) * steps[code], \
                       pos_y + (TILE_WIDTH * VECTORS[self.vector][1]) * steps[code]
                # Передвигаем танк
                self.rect = self.image.get_rect().move(x, y)
                # Проверяем пересекается ли танк с препятствиями или другими танками
                cross = pygame.sprite.spritecollideany(self, cant_move_sprites) or pygame.sprite.spritecollideany(
                    self, pygame.sprite.Group(green_tank if self.color == 'Y' else yellow_tank))
                # Передвигаем танк обратно
                self.rect = self.image.get_rect().move(pos_x, pos_y)
                # Проверяем пересечётся ли танк при ходе
                if not cross:
                    # Создаём списки координат для анимации движения
                    self.x_list = list(range(pos_x, x + (-1 if pos_x > x else 1), -1 if pos_x > x else 1))
                    self.y_list = list(range(pos_y, y + (-1 if pos_y > y else 1), -1 if pos_y > y else 1))
                    # Танк начал движение
                    self.not_moves = False
                # Возвращаем True если танк переместился, False в обратном случае
                return not cross


class Enemy(pygame.sprite.Sprite):  # Класс танка(противника)
    def __init__(self, pos_x, pos_y, vector, color):
        # Инициализация класса и добавления его в нужную группу спрайтов
        super().__init__(enemy_tanks_group, all_sprites)
        # Добавляем текстуру спрайта с нужным вектором и задаём переменные
        self.color, self.x_list, self.y_list = color, [], []
        self.image, self.reload = tanks[self.color], 0
        self.vector, self.can_shoot, self.not_moves = vector, True, True
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

        # Просчитываем путь танка до базы
        self.matrix, base_pos = matrix(level_map)
        self.matrix[self.get_pose()[1]][self.get_pose()[0]] = 1
        wave(self.matrix, base_pos)
        self.trail = trail(self.matrix, base_pos)

    def get_pose(self):
        # Возвращаем координаты(индексы для матрицы препятствий) танка
        return self.rect.x // TILE_WIDTH, self.rect.y // TILE_WIDTH

    def shoot(self):  # Функция выстрела
        # Проверяем перезарядилось ли орудие
        if self.can_shoot:
            # Создаём пулю
            Bullet(self.rect.x, self.rect.y, self.vector, self.color)
            # Список сдвигов по вектору
            vectors = {0: [0, -60], 1: [-60, -12.5], 2: [-12.5, 60], 3: [60, 0]}
            # Создаём анимацию выстрела
            AnimatedSprite(fire_image, 3, 1, self.rect.x + vectors[self.vector][0],
                           self.rect.y + vectors[self.vector][1], 10, '', self.vector)
            # Орудие перезаряжается
            self.can_shoot = False

    def update(self):
        # Пытаемся выстрелить по игрокам
        for tank in friendly_tanks_group.sprites():
            try_shoot(self, tank, object_matrix, level_map)
        # Проверяем идёт ли анимация движения танка
        if self.x_list and self.y_list:
            # Получаем координаты во время анимации движения
            x = self.x_list.pop(0) if len(self.x_list) > 1 else self.x_list[0]
            y = self.y_list.pop(0) if len(self.y_list) > 1 else self.y_list[0]
            # Перемещаем танк
            self.rect = self.image.get_rect().move(x, y)
            # Проверяем закончилась ли анимация
            if len(self.x_list) == 1 and len(self.y_list) == 1:
                # Танк полностью перемещён
                self.rect = self.image.get_rect().move(self.x_list[0], self.y_list[0])
                # Очищаем списки с координатами для анимации
                self.x_list, self.y_list = [], []
                # Танк закончил движение
                self.not_moves = True
        # Проверяем не попала ли в танк вражеская пуля
        if pygame.sprite.spritecollideany(self, pygame.sprite.Group([i for i in bullets_group.sprites()
                                                                     if i.color in 'GY'])):
            # Создаём анимацию взрыва
            AnimatedSprite(boom_image, 15, 1, self.rect.x, self.rect.y, 2, all_booms)
            # Удаляем спрайт
            self.kill()
        # Проверяем перезарядилось ли орудие
        if not self.can_shoot:
            # Добавляем время к таймеру
            self.reload += 1
            # Проверяем перезарядилось ли орудие
            if self.reload > CONSTANTS['RELOAD']:
                # Записываем, что орудие перезаряжено и обнуляем таймер
                self.can_shoot, self.reload = True, 0
        # Проверяем нашёл ли танк путь до базы
        if self.trail:
            # Берём одну команду из пути
            do = self.trail[0]
            # Список команд и их векторов
            vectors = {'Вперёд': 0, 'Влево': 1, 'Назад': 2, 'Вправо': 3}
            # Поворачиваем на нужный вектор в зависимости от команды
            for _ in range(abs(vectors[do] - self.vector)):
                self.move(('Влево' if vectors[do] - self.vector < 0 else 'Вправо') if
                          abs(vectors[do] - self.vector) == 3 else ('Влево' if vectors[do] - self.vector > 0 else
                                                                    'Вправо'))
            # Проверяем переместился ли танк, ведь ему могут помешать другие танки или препятствия
            if self.move('Вперёд'):
                # Удаляем выполненную команду
                self.trail.pop(0)

    def move(self, code):
        # Проверяем двигается ли танк в данный момент
        if self.not_moves:
            # Список векторов для поворота танка
            vectors = {TANKS[self.color]['Вправо']: -1, TANKS[self.color]['Влево']: 1}
            # Проверяем является ли команда поворотом
            if code in vectors:
                # Получаем новый вектор после поворота
                self.vector = (self.vector + vectors[code]) % 4
                # Переворачиваем спрайт в зависимости от вектора
                self.image = pygame.transform.rotate(self.image, 90 * vectors[code])
            else:
                # Получаем координаты танка
                pos_x, pos_y = self.rect.x, self.rect.y
                # Список векторов для передвижения танка
                steps = {TANKS[self.color]['Вперёд']: -1, TANKS[self.color]['Назад']: 1}
                # Получаем конечные координаты после хода
                x, y = pos_x + (TILE_WIDTH * VECTORS[self.vector][0]) * steps[code], \
                       pos_y + (TILE_WIDTH * VECTORS[self.vector][1]) * steps[code]
                # Передвигаем танк
                self.rect = self.image.get_rect().move(x, y)
                # Проверяем пересекается ли танк с препятствиями или другими танками
                cross = pygame.sprite.spritecollideany(self, cant_move_sprites) or pygame.sprite.spritecollideany(
                    self, friendly_tanks_group) or pygame.sprite.spritecollideany(
                    self, pygame.sprite.Group([i for i in enemy_tanks_group.sprites() if i != self]))
                # Передвигаем танк обратно
                self.rect = self.image.get_rect().move(pos_x, pos_y)
                # Проверяем пересечётся ли танк при ходе
                if not cross:
                    # Создаём списки координат для анимации движения
                    self.x_list = list(range(pos_x, x + (-1 if pos_x > x else 1), -1 if pos_x > x else 1))
                    self.y_list = list(range(pos_y, y + (-1 if pos_y > y else 1), -1 if pos_y > y else 1))
                    # Танк начал движение
                    self.not_moves = False
                    return True
                # Если танк не шагнул - значит перед ним препятствие, смело открываем огонь
                self.shoot()
                return False


class AnimatedSprite(pygame.sprite.Sprite):  # Класс анимированного спрайта
    # Получаем лист спрайтов, кол-во столбцов, кол-во строк, x, y, время анимации
    # (чем больше тем дольше будет длиться анимация), группа спрайтов и вектор(для поворота изображения)
    def __init__(self, sheet, columns, rows, x, y, timing, group, vector=0):
        # Инициализация класса и добавления его в нужную группу спрайтов
        super().__init__(all_animated_sprites, all_sprites, group)
        # Задаём переменные
        self.frames, self.vector, self.timing = [], vector, timing
        # Нарезаем лист спрайтов на отдельные спрайты
        self.cut_sheet(sheet, columns, rows)
        # Задаём переменные
        self.cur_frame, self.time, self.sheet = 0, 0, sheet
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        # Задаём область листа спрайтов
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        # Пробегаем по строкам и столбцам
        for j in range(rows):
            for i in range(columns):
                # Задаём область спрайта
                frame_location = (self.rect.w * i, self.rect.h * j)
                # Добавляем спрайт в список
                self.frames.append(pygame.transform.rotate(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)), 90 * self.vector))

    def update(self):
        # Добавляем время к таймеру
        self.time += 1
        # Проверяем прошло ли время обновления спрайта
        if self.time > self.timing:
            # Обнуляем таймер
            self.time = 0
            self.cur_frame += 1
            # Проверяем закончилась ли анимация
            if self.cur_frame == len(self.frames):
                # Проверяем была ли это анимация появления танка
                if self.sheet == spawn_image:
                    # Создаём танк
                    Enemy(self.rect.x // TILE_WIDTH, self.rect.y // TILE_WIDTH, 0, 'W')
                # Удаляем спрайт
                self.kill()
                # Конец
                return
            # Выбираем нужный спрайт из списка
            self.image = self.frames[self.cur_frame]


class Bullet(pygame.sprite.Sprite):  # Класс пули
    # Получаем x, y, вектор движения и цвет
    def __init__(self, pos_x, pos_y, vector, color):
        # Инициализация класса и добавления его в нужную группу спрайтов
        super().__init__(bullets_group, all_sprites)
        # Добавляем текстуру спрайта с нужным вектором и задаём переменные
        self.vector, self.color = vector, color
        self.image = pygame.transform.rotate(bullets[self.color], 90 * self.vector)
        self.cords = {0: [26, -7], 1: [-7, 26], 2: [26, 60], 3: [60, 26]}
        self.rect = self.image.get_rect().move(pos_x + self.cords[self.vector][0], pos_y + self.cords[self.vector][1])

    def update(self):
        # Проверяем врезалась ли пуля в стены, вражеские пули или танки
        if pygame.sprite.spritecollideany(self, walls_group) or (self.color in 'GY' and pygame.sprite.spritecollideany(
                self, pygame.sprite.Group([i for i in bullets_group.sprites() if i.color == 'W']))) or \
                (self.color == 'W' and pygame.sprite.spritecollideany(self, pygame.sprite.Group(
                [i for i in bullets_group.sprites() if i.color in 'GY']))):
            # Создаём анимацию взрыва
            AnimatedSprite(boom_image, 15, 1, self.rect.x - 26, self.rect.y - 26, 2, all_booms)
            # Удаляем спрайт
            self.kill()
        # Проверяем попала ли пуля в зону взрыва
        if pygame.sprite.spritecollideany(self, all_booms):
            # Удаляем спрайт
            self.kill()
        # Перемещаем пулю
        self.rect = self.image.get_rect().move(self.rect.x - VECTORS[self.vector][0] * CONSTANTS['VELOCITY'],
                                               self.rect.y - VECTORS[self.vector][1] * CONSTANTS['VELOCITY'])


# Запускаем pygame
pygame.init()
# Генерируем уровень
green_tank, yellow_tank, base = generate_level(level_map)
# Заполняем экран белым цветом
screen.fill('white')
# Запускаем меню(конструкция для правильной работы интерфейса)
menu(screen) if __name__ == '__main__' else None
# Игра идёт
game_running = True
# Запускаем часы
clock = pygame.time.Clock()
# Начинаем игру
while game_running:
    # Проверяем живы ли игроки
    if not friendly_tanks_group:
        # Поражение
        lose(screen)
    # Проверяем остались ли вражеские танки
    if not CONSTANTS['MAX_ENEMY_TANKS'] and not enemy_tanks_group and not \
            [0 for i in all_animated_sprites if i.sheet == spawn_image]:
        # Победа
        win(screen)
    # Проверяем все ивенты
    for event in pygame.event.get():
        # Проверяем нажал ли игрок на клавиши
        if event.type == pygame.KEYDOWN:
            # Проверяем ходят ли игроки
            if event.scancode in TANKS['G'].values():
                green_tank.do(event.scancode)
            if event.scancode in TANKS['Y'].values():
                yellow_tank.do(event.scancode)
            # Проверяем нажата ли клавиша esc
            if event.type == pygame.KEYDOWN and event.scancode == 41:
                # Пауза
                pause(screen)
    # Обновляем все спрайты
    all_sprites.update()
    # Прорисовываем все группы спрайтов
    all_sprites.draw(screen)
    friendly_tanks_group.draw(screen)
    enemy_tanks_group.draw(screen)
    bullets_group.draw(screen)
    all_animated_sprites.draw(screen)
    grass_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
