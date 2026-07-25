def read_records(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line
