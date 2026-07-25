def paginate(items, page, page_size):
    start = page * page_size
    end = start + page_size
    return items[start:end]


def total_pages(items, page_size):
    return len(items) // page_size
