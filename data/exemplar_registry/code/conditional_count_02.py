def count_negatives(values):
    count = 0
    for v in values:
        if v < 0:
            count += 1
    return count
