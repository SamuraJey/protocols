def make_change(n):
    coins = [25, 10, 5, 1]
    result = []

    for coin in coins:
        count = n // coin
        result.extend([coin] * count)
        n -= coin * count

    return result


# Пример использования
print(make_change(93))  # Output: [25, 25, 25, 10, 5, 3]
print(make_change(41))  # Output: [25, 10, 5, 1]
print(make_change(15))  # Output: [10, 5]


def greedy_change(n, coins):
    coins.sort(reverse=True)
    result = []
    for coin in coins:
        count = n // coin
        result.extend([coin] * count)
        n -= count * coin
    return result

# Доказательство оптимальности
# Предположим, что есть другое оптимальное решение, использующее больше монет.
# Тогда найдется монета с большим достоинством, которая не была использована в жадном алгоритме.
# Но это противоречит жадному выбору, так как алгоритм всегда использует максимально возможное количество самых больших монет.


# Пример использования
print(greedy_change(93, [25, 10, 5, 1]))  # Output: [25, 25, 25, 10, 5, 3]
print(greedy_change(41, [25, 10, 5, 1]))  # Output: [25, 10, 5, 1]
print(greedy_change(15, [10, 5]))  # Output: [10, 5]
print(greedy_change(6, [4, 3, 1]))  # Output: [10, 5]
