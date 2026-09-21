def index_of_min(values):
    best = 0
    for i in range(1, len(values)):
        if values[i] < values[best]:
            best = i
    return best
