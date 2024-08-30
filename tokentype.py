from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INT = auto()
    FLT = auto() 
    STRING = auto()
    OPERATOR = auto()
    SEPARATOR = auto()
    DATATYPE = auto()
    EOF = auto()

class Token:
    def __init__(self, type, value, srcpos):
        self.type = type
        self.value = value
        self.srcpos = srcpos
    
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, {self.srcpos.filename}, {self.srcpos.line}, {self.srcpos.column}, {self.srcpos.length})'
