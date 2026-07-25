import os


def read_file(filename, base_dir='.'):
    path = os.path.join(base_dir, filename)
    with open(path, 'r') as f:
        return f.read()
