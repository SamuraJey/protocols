import heapq


def read_data(filename: str):
    with open(filename, 'r') as file:
        n = int(file.readline())
        graph = [[] for _ in range(n+1)]
        for i in range(1, n+1):
            line = list(map(int, file.readline().split()))
            for j in range(0, len(line)-1, 2):
                graph[line[j]].append((i, line[j+1]))
        start = int(file.readline())
        end = int(file.readline())
    return graph, start, end


def dijkstra(graph: list, start: int, end: int):
    queue = [(1, start, [])]
    visited = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in visited:
            visited.add(node)
            path = path + [node]
            if node == end:
                return cost, path
            for dest, weight in graph[node]:
                if dest not in visited:
                    heapq.heappush(queue, (cost*weight, dest, path))
    return float('inf'), []


def write_data(cost: float, path: list):
    with open('contests/out.txt', 'w') as file:
        if cost == float('inf'):
            file.write('N\n')
        else:
            file.write('Y\n')
            file.write(' '.join(map(str, path)) + '\n')
            file.write(str(int(cost)) + '\n')


def main():
    graph, start, end = read_data('contests/in.txt')
    cost, path = dijkstra(graph, start, end)
    write_data(cost, path)


if __name__ == '__main__':
    main()


'''
Ограничение времени	1 секунда
Ограничение памяти	64.0 Мб
Ввод	in.txt
Вывод	out.txt
Найти v-w путь в сети с неотрицательными весами для задачи минимального пути.

Метод решения: алгоритм Дейкстры.

Формат ввода
Сеть, заданная списками ПРЕДШ[].

N - количество вершин. Далее последовательно расположены списки предшествующих для каждой вершины. В список заносится номер вершины и вес дуги. Список заканчивается 0 (не путать с нулевым весом). В конце файла записаны источник и цель.

Формат вывода
В случае отсутствия пути в файл результатов необходимо записать "N". При наличии пути - "Y" и далее с новой строки весь путь. Путь начинается источником и заканчивается целью. Узлы отделяются друг от друга пробелами, вес пути вычисляется как произведение весов всех дуг, входящих в него, и записывается в третьей строке.

Пример
Ввод
4
0
1 25 3 0 0
1 4 0
3 7 0
1
4
Вывод
Y
1 3 4
28
'''
