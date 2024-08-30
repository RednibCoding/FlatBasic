from lexer import Lexer
from parser import Parser
from semanter import Semanter

# Example test program
input_code = """
proc calculate(a: int, b: int): flt
    let result: flt = (a + b)
    return result
pend

proc check_conditions(x: int, y: int): int
    if !(x > y) and y != 0 then
        return 1
    else
        return 0
    endif
pend

let x: int = 10
let y: int = 20
let z: flt = calculate(x, y)

if x < y or z >= 15 then
    print("Condition met")
else
    print("Condition not met")
endif
"""

input_code2 = """
type Engine
    field speed: flt = 10
tend

type Car
    field brand: str = "BMW"
    field engine: Engine
tend

let mycar: Car = new Car
let carSpeed: flt = mycar.engine.speed
carSpeed = mycar.engine.speed
mycar.engine.speed = 20

proc changeBrand(car: Car, newBrand: str): void
    car.brand = newBrand
pend

changeBrand(mycar, mycar.brand)
"""

# Set up the lexer, parser, and semantic analyzer
lexer = Lexer(input_code2, "test.mb")
parser = Parser(lexer)
ast = parser.parse()

# Print the AST for visual confirmation
print(ast)

# Perform semantic analysis
semanter = Semanter()
semanter.analyze(ast)

print("Semantic analysis completed successfully.")
