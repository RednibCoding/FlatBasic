# FlatBasic
Small statically typed, compiled basic language that has about the same abstraction level as c.
Flat basic compiles to c and can interface with c.

## Bootstrap
Python is just the first iteration implementation, it is planned to write FlatBasic in FlatBasic itself, which means it will be compiled to c. Then we can rid of the python implementation.

## Grammar in BNF Notation

```
<program>         ::= <statement_list>

<statement_list>  ::= <statement> | <statement> <statement_list>

<statement>       ::= <let_statement>
                    | <if_statement>
                    | <for_statement>
                    | <while_statement>
                    | <do_statement>
                    | <select_case_statement>
                    | <proc_statement>
                    | <dim_statement>
                    | <return_statement>
                    | <assignment_statement>
                    | <function_call>
                    | <type_definition>

<let_statement>   ::= "let" <identifier> ":" <pointer_opt> <datatype> "=" <expression>

<if_statement>    ::= "if" <expression> "then" <statement> ["else" <statement>] "endif"

<for_statement>   ::= "for" <identifier> "=" <expression> "to" <expression> ["step" <expression>] <statement> "next"

<while_statement> ::= "while" <expression> <statement> "wend"

<do_statement>    ::= "do" <statement> "loop" ["while" <expression> | "until" <expression>]

<select_case_statement> ::= "select" "case" <expression> <case_list> ["else" <statement>] "end" "select"

<case_list>       ::= <case_statement> | <case_statement> <case_list>

<case_statement>  ::= "case" <expression> <statement>

<proc_statement>  ::= "proc" <identifier> "(" <param_list> ")" ":" <pointer_opt> <datatype> <statement_list> "pend"

<param_list>      ::= <param> | <param> "," <param_list> | ""

<param>           ::= <identifier> ":" <pointer_opt> <datatype>

<dim_statement>   ::= "dim" <identifier> "[" <expression> "]" ":" <datatype>

<return_statement>::= "return" <expression>

<assignment_statement> ::= <identifier> "=" <expression> 
                         | <identifier> "[" <expression> "]" "=" <expression>
                         | <field_access> "=" <expression>

<function_call>   ::= <identifier> "(" <argument_list> ")" | <field_access> "(" <argument_list> ")"

<argument_list>   ::= <expression> | <expression> "," <argument_list> | ""

<expression>      ::= <logical_or>

<logical_or>      ::= <logical_and> | <logical_and> "or" <logical_or>

<logical_and>     ::= <equality> | <equality> "and" <logical_and>

<equality>        ::= <comparison> | <comparison> "==" <equality> | <comparison> "!=" <equality>

<comparison>      ::= <additive> 
                    | <additive> "<" <comparison>
                    | <additive> "<=" <comparison>
                    | <additive> ">" <comparison>
                    | <additive> ">=" <comparison>

<additive>        ::= <term> | <term> "+" <additive> | <term> "-" <additive>

<term>            ::= <factor> | <factor> "*" <term> | <factor> "/" <term>

<factor>          ::= <number> 
                    | <identifier> 
                    | <function_call> 
                    | <array_access> 
                    | <string>
                    | <field_access>
                    | "(" <expression> ")"
                    | <unary_op> <factor>

<unary_op>        ::= "-" | "+" | "!"

<array_access>    ::= <identifier> "[" <expression> "]"

<field_access>    ::= <identifier> "." <identifier> | <field_access> "." <identifier>

<type_definition> ::= "type" <identifier> <field_list> "tend"

<field_list>      ::= "field" <identifier> ":" <pointer_opt> <datatype> ["=" <expression>] <field_list> | ""

<pointer_opt>     ::= "ptr" | ""

<datatype>        ::= "void" | "char" | "uchar" | "short" | "ushort" | "int" | "uint" | "long" | "ulong" | "float" | "double" | "size" | "string" | <identifier>  ; where <identifier> could be a user-defined type

<number>          ::= <integer> | <float>

<integer>         ::= <digit> | <digit> <integer>

<float>           ::= <integer> "." <digit> <integer>

<digit>           ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<identifier>      ::= <letter> | <letter> <identifier>

<letter>          ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"

<string>          ::= '"' <character> '"'

<character>       ::= any printable character except '"' and '\n'

```