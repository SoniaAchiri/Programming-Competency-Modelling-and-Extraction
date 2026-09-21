def top_k(values, k):
    result = []
    remaining = list(values)
    for _ in range(k):
        best = remaining[0]
        for v in remaining:
            if v > best:
                best = v
        remaining.remove(best)
        result.append(best)
    return result
