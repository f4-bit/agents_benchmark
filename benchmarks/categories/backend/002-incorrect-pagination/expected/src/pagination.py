import math


def paginate(items, page, page_size):
    if not isinstance(page, int) or page < 1:
        raise ValueError("page must be a positive integer")
    if not isinstance(page_size, int) or page_size < 1:
        raise ValueError("page_size must be a positive integer")

    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]


def total_pages(items, page_size):
    if not isinstance(page_size, int) or page_size < 1:
        raise ValueError("page_size must be a positive integer")
    if not items:
        return 0
    return math.ceil(len(items) / page_size)
