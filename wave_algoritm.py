def matrix(level_map):  # Получаем карту уровня
    # Получаем линию с базой из карты уровня
    line = [line for line in level_map if 'B' in line]
    # Возвращаем полученную матрицу препятствий и координаты базы(индексы базы в матрице)
    return [[-1 if i in '#=' else 0 for i in line] for line in level_map], \
        (level_map.index(*line), str(line).index('B') - 2)


def wave(matrix, base_pos):  # Получаем матрицу препятствий и координаты базы(индексы базы в матрице)
    # Задаём число
    number = 1
    # Пробегаемся по все ячейкам матрицы
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
                        # Матрица волны составлена
                        return True
    # Волна не дошла до базы
    return False


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
