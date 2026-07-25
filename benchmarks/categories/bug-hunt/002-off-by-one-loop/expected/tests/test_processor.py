import processor


def test_prefix_items_returns_all_elements():
    items = ['a', 'b', 'c', 'd']
    assert processor.prefix_items(items, 'x-') == [
        'x-a', 'x-b', 'x-c', 'x-d',
    ]


def test_prefix_items_empty_list():
    assert processor.prefix_items([], 'x-') == []


def test_prefix_items_single_element():
    assert processor.prefix_items(['z'], 'x-') == ['x-z']
