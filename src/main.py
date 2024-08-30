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
let z: float = calculate(x, y)

if x < y or z >= 15 then
    print("Condition met")
else
    print("Condition not met")
endif
"""

input_code2 = """
type Engine
    field speed: float = 10
tend

type Car
    field brand: string = "BMW"
    field engine: Engine
tend

let mycar: Car = new Car
let carSpeed: float = mycar.engine.speed
carSpeed = mycar.engine.speed
mycar.engine.speed = 20

proc changeBrand(car: Car, newBrand: string): void
    car.brand = newBrand
pend

changeBrand(mycar, mycar.brand)
"""

input_code3 = """
# Array example
dim myArray[10]: int
let index: int = 2
myArray[index] = 42

let invalidIndex: float = 2.5
myArray[invalidIndex] = 100  # This should trigger an error

let x: double = 5.5
let y: int = 10
let z: double = x + y  # This should promote y to double
"""

input_code4 = """

type Car
tend

let myIntPtr: ptr int = 20
let myCarPtr: ptr Car = new ptr Car

let x: int = myIntPtr + 5
let y: ptr int = myIntPtr + 1
let z: int = myIntPtr == y  # Comparison between pointers should be valid
"""

input_code5 = """
proc myProc(): void pend

let myProcPtr: ptr size = myProc
myProcPtr()
"""

# Set up the lexer, parser, and semantic analyzer
lexer = Lexer(input_code5, "test.mb")
parser = Parser(lexer)
ast = parser.parse()

# Print the AST for visual confirmation
print(ast)

# Perform semantic analysis
semanter = Semanter()
semanter.analyze(ast)

print("Semantic analysis completed successfully.")
