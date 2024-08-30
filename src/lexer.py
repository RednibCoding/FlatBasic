import sys
from sourcepos import SrcPos
from syntax import Syntax
from tokentype import Token, TokenType

class Lexer:
    def __init__(self, input_code, filename):
        self.input_code = input_code
        self.filename = filename
        self.position = 0
        self.line = 1   # Lines start at 1
        self.column = 1 # Columns start at 1
        self.current_char = self.input_code[self.position] if self.input_code else None
    
    def error(self, srcpos, message="Syntax error"):
        print(f"error at {srcpos.filename}:{srcpos.line}:{srcpos.column} : {message}")
        sys.exit()
    
    def advance(self):
        if self.current_char == "\n":
            self.line += 1
            self.column = 1  # Reset column to 1 at the start of a new line
        else:
            self.column += 1
        
        self.position += 1
        if self.position < len(self.input_code):
            self.current_char = self.input_code[self.position]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def get_identifier(self):
        start_column = self.column
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
            result += self.current_char
            self.advance()
        return result, start_column

    def get_number(self):
        result = ""
        is_float = False
        start_column = self.column
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
            if self.current_char == ".":
                if is_float:  # If we"ve already encountered a dot, this is an error
                    break
                is_float = True
            result += self.current_char
            self.advance()
        
        token_type = TokenType.FLT if is_float else TokenType.INT
        return result, start_column, token_type
    
    def get_string(self):
        start_column = self.column
        self.advance()  # Skip the opening quote
        result = ""
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # Skip the closing quote
        return result, start_column
    
    def skip_comment(self):
        while self.current_char is not None and self.current_char != "\n":
            self.advance()
        self.advance()
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "#":
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == "_":
                value, start_column = self.get_identifier()
                token_length = self.column - start_column
                if value in Syntax.data_types:
                    return Token(TokenType.DATATYPE, value, SrcPos(self.filename, self.line, start_column, token_length))
                if value in Syntax.keywords:
                    return Token(TokenType.KEYWORD, value, SrcPos(self.filename, self.line, start_column, token_length))
                else:
                    return Token(TokenType.IDENTIFIER, value, SrcPos(self.filename, self.line, start_column, token_length))
            
            # Recognize operators
            if self.current_char == "<":
                start_column = self.column
                self.advance()
                token_length = start_column - self.column
                if self.current_char == "=":
                    self.advance()
                    token_length = start_column - self.column
                    return Token(TokenType.OPERATOR, "<=", SrcPos(self.filename, self.line, start_column, token_length))
                return Token(TokenType.OPERATOR, "<", SrcPos(self.filename, self.line, start_column, token_length))
            
            if self.current_char == ">":
                start_column = self.column
                self.advance()
                token_length = start_column - self.column
                if self.current_char == "=":
                    self.advance()
                    token_length = start_column - self.column
                    return Token(TokenType.OPERATOR, ">=", SrcPos(self.filename, self.line, start_column, token_length))
                return Token(TokenType.OPERATOR, ">", SrcPos(self.filename, self.line, start_column, token_length))
            
            if self.current_char == "=":
                start_column = self.column
                self.advance()
                token_length = start_column - self.column
                if self.current_char == "=":
                    self.advance()
                    token_length = start_column - self.column
                    return Token(TokenType.OPERATOR, "==", SrcPos(self.filename, self.line, start_column, token_length))
                return Token(TokenType.OPERATOR, "=", SrcPos(self.filename, self.line, start_column, token_length))  # For assignments
            
            if self.current_char == "!":
                start_column = self.column
                self.advance()
                token_length = start_column - self.column
                if self.current_char == "=":
                    self.advance()
                    token_length = start_column - self.column
                    return Token(TokenType.OPERATOR, "!=", SrcPos(self.filename, self.line, start_column, token_length))
                return Token(TokenType.OPERATOR, "!", SrcPos(self.filename, self.line, start_column, token_length))  # For assignments
                    
            
            # Recognize "and" and "or"
            if self.current_char.isalpha():
                identifier, start_column = self.get_identifier()
                token_length = self.column - start_column
                if identifier in ["and", "or"]:
                    return Token(TokenType.KEYWORD, identifier, SrcPos(self.filename, self.line, start_column, token_length))
    
            if self.current_char.isdigit():
                value, start_column, token_type = self.get_number()
                token_length = self.column - start_column
                return Token(token_type, value, SrcPos(self.filename, self.line, start_column, token_length))
            
            if self.current_char == '"':
                value, start_column = self.get_string()
                token_length = self.column - start_column + 1  # Include the closing quote
                return Token(TokenType.STRING, value, SrcPos(self.filename, self.line, start_column, token_length))
            
            if self.current_char in "+-*/=<>:":
                start_column = self.column
                char = self.current_char
                self.advance()
                return Token(TokenType.OPERATOR, char, SrcPos(self.filename, self.line, start_column, 1))
            
            if self.current_char in ".(),[]":
                start_column = self.column
                char = self.current_char
                self.advance()
                return Token(TokenType.SEPARATOR, char, SrcPos(self.filename, self.line, start_column, 1))

            self.error(SrcPos(self.filename, self.line, self.column, 1), f"unexpected token {self.current_char}")
        
        return Token(TokenType.EOF, None, SrcPos(self.filename, self.line, self.column, 0))
