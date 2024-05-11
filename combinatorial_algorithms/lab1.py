def dfs(graph, visited, node, component):
    visited[node] = True
    component.append(node)
    for neighbor in graph[node]:
        if not visited[neighbor]:
            dfs(graph, visited, neighbor, component)


def find_connected_components(graph):
    n = len(graph)
    visited = [False] * n
    components = []
    for node in range(1, n):
        if not visited[node]:
            component = []
            dfs(graph, visited, node, component)
            components.append(sorted(component))
    return components


with open('in.txt', 'r') as file:
    n = int(file.readline())
    graph = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        line = file.readline().split()
        if line[0] == '0':
            continue
        graph[i] = list(map(int, line[:-1]))

components = find_connected_components(graph)

with open('out.txt', 'w') as file:
    file.write(str(len(components)) + '\n')
    for component in components:
        file.write(' '.join(map(str, component)) + '\n')

'''
Ограничение времени	1 секунда
Ограничение памяти	64.0 Мб
Ввод	in.txt
Вывод	out.txt
В данном графе выделить все компоненты связности.

Метод решения: Поиск в глубину.

Формат ввода
Первая строка содержит единственное число N — количество вершин в графе. Далее последовательно расположены списки смежностей для каждой вершины. Каждый список заканчивается 0. Вершины нумеруются с единицы.

Формат вывода
В первой строке вывести количество компонент связности и далее вершины, входящие в них. Вершины в компонентах связности должны быть упорядочены по возрастанию номеров. Первой печатается компонента связности, в состав которой входит вершина с минимальным номером. Каждая компонента печатается с новой строки.


Пример
4
2 3 0
1 3 0
1 2 4 0
3 0
Вывод
1
1 2 3 4
'''
