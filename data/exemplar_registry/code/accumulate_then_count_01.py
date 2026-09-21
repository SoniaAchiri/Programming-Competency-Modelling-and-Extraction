def is_only_occurrence(word, sentence_words):
    seen = ()
    for w in sentence_words:
        seen += (w,)
    return seen.count(word) == 1
