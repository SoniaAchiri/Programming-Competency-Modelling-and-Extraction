def bottom_k(values, k):
    pool = list(values)
    result = []
    for _ in range(k):
        idx = 0
        for i in range(1, len(pool)):
            if pool[i] < pool[idx]:
                idx = i
        result.append(pool.pop(idx))
    return result
