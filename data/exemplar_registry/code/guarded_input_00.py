def get_positive():
    n = int(input("Enter a positive number: "))
    valid = False
    while not valid:
        if n > 0:
            valid = True
        else:
            n = int(input("Enter a positive number: "))
    return n
