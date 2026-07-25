import os
import tempfile

import pytest

import reader


_TRACKER = {"opened": [], "closed_count": 0}


class _TrackedFile:
    def __init__(self, path, mode='r'):
        self._file = open(path, mode)
        self._closed = False
        _TRACKER["opened"].append(self)

    def __iter__(self):
        return iter(self._file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def close(self):
        if not self._closed:
            self._closed = True
            _TRACKER["closed_count"] += 1
            self._file.close()


def _tracking_open(path, mode='r'):
    return _TrackedFile(path, mode)


@pytest.fixture(autouse=True)
def _reset_tracker(monkeypatch):
    _TRACKER["opened"].clear()
    _TRACKER["closed_count"] = 0
    monkeypatch.setattr(reader, 'open', _tracking_open, raising=False)


def test_read_records_returns_lines_and_closes_file():
    lines = ['first', 'second', 'third', 'fourth']
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write('\n'.join(lines))
        tmp.write('\n')
        path = tmp.name

    try:
        gen = reader.read_records(path)
        records = list(gen)
        assert records == lines
        assert _TRACKER["closed_count"] == 1
        for tracked in _TRACKER["opened"]:
            assert tracked._closed
        gen.close()
    finally:
        for tracked in _TRACKER["opened"]:
            tracked.close()
        os.unlink(path)
