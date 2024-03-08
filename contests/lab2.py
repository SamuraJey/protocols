from collections import deque

# Создаем словарь для преобразования буквенных координат в числовые
letter_to_number = {'a': 1, 'b': 2, 'c': 3,
                    'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
number_to_letter = {1: 'a', 2: 'b', 3: 'c',
                    4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}


# Функция для проверки допустимости координат на шахматной доске
def is_valid_coordinate(x, y):
    return 1 <= x <= 8 and 1 <= y <= 8


# Функция для получения списка возможных ходов коня
def get_possible_moves(x, y):
    moves = []
    possible_offsets = [(-2, -1),
                        (-2, 1),
                        (-1, -2),
                        (-1, 2),
                        (1, -2),
                        (1, 2),
                        (2, -1),
                        (2, 1)]
    for dx, dy in possible_offsets[::-1]:
        new_x = x + dx
        new_y = y + dy
        if is_valid_coordinate(new_x, new_y):
            moves.append((new_x, new_y))
    return moves


# Функция для поиска маршрута коня до пешки
def find_route(knight, pawn):
    knight_x, knight_y = knight
    pawn_x, pawn_y = pawn

    # Создаем словарь для хранения предыдущих ходов
    previous_moves = {}

    # Создаем очередь для поиска в ширину
    queue = deque()
    queue.append(knight)

    while queue:
        current_pos = queue.popleft()
        if current_pos == pawn:
            break

        for move in get_possible_moves(*current_pos):
            move_x, move_y = move
            if move not in previous_moves:
                queue.append(move)
                previous_moves[move] = current_pos

    # Восстанавливаем маршрут
    route = []
    pos = pawn
    while pos != knight:
        route.append(pos)
        pos = previous_moves[pos]
    route.append(knight)

    # Преобразуем координаты в шахматную нотацию
    route = [(number_to_letter[x], y) for x, y in route[::-1]]

    return route


with open('in.txt', 'r') as file:
    knight_pos = file.readline().strip()
    pawn_pos = file.readline().strip()

knight_x, knight_y = letter_to_number[knight_pos[0]], int(knight_pos[1])
pawn_x, pawn_y = letter_to_number[pawn_pos[0]], int(pawn_pos[1])

route = find_route((knight_x, knight_y), (pawn_x, pawn_y))

with open('out.txt', 'w') as file:
    for move in route:
        file.write(''.join(map(str, move)) + '\n')
