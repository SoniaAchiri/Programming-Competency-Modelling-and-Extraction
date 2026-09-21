def find_index(values, target):
    found = -1
    for i, v in enumerate(values):
        if v == target:
            found = i
    return found
