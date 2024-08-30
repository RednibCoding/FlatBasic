class SrcPos:
    def __init__(self, filename, line, column, length):
        self.filename = filename
        self.line = line
        self.column = column
        self.length = length