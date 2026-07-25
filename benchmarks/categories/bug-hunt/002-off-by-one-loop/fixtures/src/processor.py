def prefix_items(items, prefix):
    result = []
    for i in range(len(items) - 1):
        result.append(prefix + str(items[i]))
    return result
