def is_unique_tag(tag, tagged_items):
    matches = ()
    for item in tagged_items:
        matches += (item,)
    return matches.count(tag) == 1
