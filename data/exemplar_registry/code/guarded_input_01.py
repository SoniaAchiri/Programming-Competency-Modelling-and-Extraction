def get_yes_no():
    answer = input("yes or no? ")
    while True:
        if answer in ("yes", "no"):
            break
        answer = input("yes or no? ")
    return answer == "yes"
