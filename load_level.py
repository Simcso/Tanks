# Импорт библиотек
import sys
import os


def load_level(filename):  # Получаем название уровня
    path = os.path.join('data', filename)
    fullname = os.path.join(sys._MEIPASS, path) if hasattr(sys, "_MEIPASS") else path
    lines = open(fullname).readlines()
    line, level_map,  = lines.pop(0).strip(), []
    while line:  # Пробегаемся по линиям уровня, пока не встретится пустая строка(разделитель карты уровня от констант)
        # Добавляем линию в карту уровня
        level_map.append(line)
        # Берём новую линию
        line = lines.pop(0).strip()
    # Возвращаем карту уровня и список всех констант
    return level_map,  {i[0]: int(i[1]) for i in [line.strip().split(' = ') for line in lines]}


def correct_level(filename, level_map):  # Получаем имя файла и карту уровня
    # Добавляем недостающие точки
    level_map = list(map(lambda x: x.ljust(max(map(len, level_map)), '.'), level_map))
    # Открываем файл
    with open(filename, 'w') as mapFile:
        for line in level_map:  # Пробегаемся по строчкам уровня
            # Сохраняем строку в файл
            mapFile.write(f'{line}\n')
    # Закрываем файл
    mapFile.close()
