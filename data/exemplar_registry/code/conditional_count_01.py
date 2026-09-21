def count_vowels(word):
    count = 0
    for ch in word:
        if ch in "aeiouAEIOU":
            count += 1
    return count
