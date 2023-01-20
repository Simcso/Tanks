# Импорт библиотек
import wave_algoritm
from math import ceil

# Ширина клетки
TILE_WIDTH = 60


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
            tank.matrix, base_pos = wave_algoritm.matrix(level)
            tank.matrix[tank.get_pose()[1]][tank.get_pose()[0]] = 1
            wave_algoritm.wave(tank.matrix, base_pos)
            tank.trail = wave_algoritm.trail(tank.matrix, base_pos)
