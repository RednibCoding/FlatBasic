from lexer import Lexer
from parser import Parser
from semanter import Semanter

input_code = """
proc print(msg: str): void
pend

proc myproc(a: int, b: int): flt
    let c: flt = a + b
    return c
pend

proc printmessage(msg: str): void
    print(msg)
pend

dim arr[10]: int

for i = 1 to 10
    arr[i] = i * 2
next

printmessage("The value is: ")
print(myproc(5, 3))
"""
lexer = Lexer(input_code, "test.mb")
parser = Parser(lexer)
ast = parser.parse()

semanter = Semanter()
semanter.analyze(ast)