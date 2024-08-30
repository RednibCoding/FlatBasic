## Grammar rules in BNF Notation

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

<let_statement>   ::= "let" <identifier> ":" <datatype> "=" <expression>

<if_statement>    ::= "if" <expression> "then" <statement> ["else" <statement>]

<for_statement>   ::= "for" <identifier> "=" <expression> "to" <expression> ["step" <expression>] <statement> "next"

<while_statement> ::= "while" <expression> <statement> "wend"

<do_statement>    ::= "do" <statement> "loop" ["while" <expression> | "until" <expression>]

<select_case_statement> ::= "select" "case" <expression> <case_list> ["else" <statement>] "end" "select"

<case_list>       ::= <case_statement> | <case_statement> <case_list>

<case_statement>  ::= "case" <expression> <statement>

<proc_statement>  ::= "proc" <identifier> "(" <param_list> ")" ":" <datatype> <statement_list> "pend"

<param_list>      ::= <param> | <param> "," <param_list> | ""

<param>           ::= <identifier> ":" <datatype>

<dim_statement>   ::= "dim" <identifier> "[" <expression> "]" ":" <datatype>

<return_statement>::= "return" <expression>

<assignment_statement> ::= <identifier> "=" <expression> | <identifier> "[" <expression> "]" "=" <expression>

<function_call>   ::= <identifier> "(" <argument_list> ")"

<argument_list>   ::= <expression> | <expression> "," <argument_list> | ""

<expression>      ::= <term> | <term> "+" <expression> | <term> "-" <expression>

<term>            ::= <factor> | <factor> "*" <term> | <factor> "/" <term>

<factor>          ::= <number> | <identifier> | <function_call> | <array_access> | <string>

<array_access>    ::= <identifier> "[" <expression> "]"

<datatype>        ::= "int" | "flt" | "str" | "chr" | "void"

<number>          ::= <integer> | <float>

<integer>         ::= <digit> | <digit> <integer>

<float>           ::= <integer> "." <digit> <integer>

<digit>           ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<identifier>      ::= <letter> | <letter> <identifier>

<letter>          ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"

<string>          ::= '"' <character> '"'
```