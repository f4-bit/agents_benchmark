def read_records(path):
    f = open(path)
    for line in f:
        line = line.strip()
        if line:
            yield line
