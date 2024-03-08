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
