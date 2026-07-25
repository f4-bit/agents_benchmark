import pytest
from files import read_file


def test_valid_file_is_read(tmp_path):
    file_path = tmp_path / 'data.txt'
    file_path.write_text('hello world')
    assert read_file('data.txt', base_dir=str(tmp_path)) == 'hello world'


def test_path_traversal_is_blocked(tmp_path):
    outside_file = tmp_path.parent / 'outside.txt'
    outside_file.write_text('secret')
    with pytest.raises(ValueError):
        read_file('../outside.txt', base_dir=str(tmp_path))
