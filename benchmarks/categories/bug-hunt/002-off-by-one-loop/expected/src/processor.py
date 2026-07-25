def prefix_items(items, prefix):
    result = []
    for i in range(len(items)):
        result.append(prefix + str(items[i]))
    return result
