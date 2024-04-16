import heapq

def read_data(filename: str):
    with open('contests/in.txt', 'r') as file:
        n = int(file.readline())
        graph = [[] for _ in range(n+1)]
        for i in range(1, n+1):
            line = list(map(int, file.readline().split()))
            for j in range(0, len(line)-1, 2):
                graph[line[j]].append((i, line[j+1]))
        # start, end = map(int, file.readline().split())
        start = int(file.readline())
        end = int(file.readline())

    return graph, start, end

def dijkstra(graph, start, end):
    queue = [(1, start, [])]  # initialize cost as 1 for multiplication
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
                    heapq.heappush(queue, (cost*weight, dest, path))  # use multiplication
    return float('inf'), []

def write_data(cost, path):
    with open('contests/out.txt', 'w') as file:
        if cost == float('inf'):
            file.write('N\n')
        else:
            file.write('Y\n')
            file.write(' '.join(map(str, path)) + '\n')
            file.write(str(cost) + '\n')

graph, start, end = read_data()
cost, path = dijkstra(graph, start, end)
write_data(cost, path)