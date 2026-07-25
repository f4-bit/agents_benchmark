import os


def read_file(filename, base_dir='.'):
    base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base, filename))

    if os.path.commonpath([base, target]) != base:
        raise ValueError('Path traversal detected')

    with open(target, 'r') as f:
        return f.read()
