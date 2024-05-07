# Импорт библиотек
from math import ceil

# Ширина клетки
TILE_WIDTH = 60


# Функции для стрельбы танка
def object_matrix(level_map):  # Получаем карту уровня
    # Список значений для замены
    tiles = {'#': -1, '/': 1}
    # Возвращаем полученную матрицу препятствий
    return [[tiles[i] if i in tiles else 0 for i in line] for line in level_map]


def try_shoot(tank, enemy, matrix, level):  # Получаем класс танка(стрелка), класс танка(мишени),
    # матрицу препятствий и карту уровня
    # получаем координаты(индексы для матрицы препятствий) танков
    tank_x, tank_y = ceil(tank.rect.x / TILE_WIDTH), ceil(tank.rect.y / TILE_WIDTH)
    enemy_x, enemy_y = ceil(enemy.rect.x / TILE_WIDTH), ceil(enemy.rect.y / TILE_WIDTH)
    # Проверяем находится ли танк "мишень" в кустах и пересекаются ли танки на уровне
    if matrix[enemy_y][enemy_x] != 1 and (tank.rect.x == enemy.rect.x or tank.rect.y == enemy.rect.y):
        # Проверяем есть ли на пути стрельбы препятствия в виде металлических стен
        if not ([0 for y in range(tank_y, enemy_y, 1 if tank_y < enemy_y else -1) if matrix[y][tank_x] == -1] if
                tank_x == enemy_x else [0 for x in range(tank_x, enemy_x, 1 if tank_x < enemy_x else -1)
                                        if matrix[tank_y][x] == -1]):
            # Определяем вектор стрельбы
            vector = (0 if tank_y > enemy_y else 2) if tank_x == enemy_x else (1 if tank_x > enemy_x else 3)
            # Поворачиваемся по нужному вектору
            for _ in range(abs(vector - tank.vector)):
                tank.not_moves = True
                tank.move(('Влево' if vector - tank.vector < 0 else 'Вправо') if abs(vector - tank.vector) == 3 else (
                    'Влево' if vector - tank.vector > 0 else 'Вправо'))
            # Выстрел!
            tank.shoot()
            # Заново просчитываем путь танка до базы
            tank.create_matrix, base_pos = create_matrix(level)
            tank.create_matrix[tank.get_pose()[1]][tank.get_pose()[0]] = 1
            wave(tank.create_matrix, base_pos)
            tank.trail = trail(tank.create_matrix, base_pos)
            return True
    return False


# Функции для передвижения танка
def create_matrix(level_map):  # Получаем карту уровня
    # Получаем линию с базой из карты уровня
    line = [line for line in level_map if 'B' in line]
    # Возвращаем полученную матрицу препятствий и координаты базы(индексы базы в матрице)
    return [[-1 if i in '#=' else 0 for i in line] for line in level_map], \
        (level_map.index(*line), str(line).index('B') - 2)


def wave(matrix, base_pos):  # Получаем матрицу препятствий и координаты базы(индексы базы в матрице)
    number = 1 # Задаём число
    # Пробегаемся по всем ячейкам матрицы
    for i in range(len(matrix) * len(matrix[0])):
        number += 1
        # Пробегаемся по всем строкам
        for y in range(len(matrix)):
            # Пробегаемся по всем ячейкам строки
            for x in range(len(matrix[y])):
                if matrix[y][x] == (number - 1):
                    # Проверяем все соседние ячейки и выставляем новые значения
                    if y > 0 and matrix[y - 1][x] == 0:
                        matrix[y - 1][x] = number
                    if y < (len(matrix) - 1) and matrix[y + 1][x] == 0:
                        matrix[y + 1][x] = number
                    if x > 0 and matrix[y][x - 1] == 0:
                        matrix[y][x - 1] = number
                    if x < (len(matrix[y]) - 1) and matrix[y][x + 1] == 0:
                        matrix[y][x + 1] = number
                    # Волна дошла до базы
                    if (abs(y - base_pos[0]) + abs(x - base_pos[1])) == 1:
                        # Добавляем финальное значение в матрицу
                        matrix[base_pos[0]][base_pos[1]] = number
                        return True # Матрица волны составлена
    return False # Волна не дошла до базы


def trail(matrix, base_pos):  # Получаем матрицу препятствий и координаты базы(индексы базы в матрице)
    # Задаём переменные
    x, y = base_pos[1], base_pos[0]
    number, res = matrix[y][x], []
    # Бегаем по циклу пока не дойдём от базы до танка
    while number:
        # Уменьшаем число
        number -= 1
        # Проверяем все соседние ячейки и добавляем действие в путь
        if matrix[y - 1][x] == number:
            y -= 1
            res.append('Назад')
        elif matrix[y + 1][x] == number:
            res.append('Вперёд')
            y += 1
        elif matrix[y][x - 1] == number:
            res.append('Вправо')
            x -= 1
        elif matrix[y][x + 1] == number:
            res.append('Влево')
            x += 1
    # Возвращаем путь
    return res[::-1]