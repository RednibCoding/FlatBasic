from symbol import Symbol
import sys
from nodes import *
from tokentype import TokenType

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.global_symbol_table = {}  # Global scope
        self.local_symbol_table = None  # Local scope, set within procedures
        self.user_type_table = {} # Table for user-defined types
    
    def error(self, message="Syntax error"):
        print(f"[error] {self.current_token.srcpos.filename}:{self.current_token.srcpos.line}:{self.current_token.srcpos.column}:\n\t-> {message}")
        sys.exit()

    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f"Expected token {token_type}, got '{self.current_token.value}' {self.current_token.type}")
    
    def expect(self, token_value):
        if self.current_token.value == token_value:
            self.advance()
        else:
            self.error(f"Expected token '{token_value}', got '{self.current_token.value}'")
    
    def declare_variable(self, var_name, var_type, is_pointer=False, scope='global'):
        symbol_table = self.global_symbol_table if scope == 'global' else self.local_symbol_table
        if var_name in symbol_table:
            self.error(f"Variable '{var_name}' already declared in this scope")
        # Store the variable as a Symbol object
        symbol_table[var_name] = Symbol(var_type=var_type, is_pointer=is_pointer)

    
    def parse_field_access(self, instance_name):
        token = self.current_token
        instance = IdentifierNode(token.srcpos, instance_name)

        # Determine the type of the initial instance from the local or global scope
        if self.local_symbol_table is not None and instance_name in self.local_symbol_table:
            current_symbol = self.local_symbol_table[instance_name]
        elif instance_name in self.global_symbol_table:
            current_symbol = self.global_symbol_table[instance_name]
        else:
            self.error(f"Variable '{instance_name}' not declared", token)

        current_type = current_symbol.var_type

        while self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '.':
            self.eat(TokenType.SEPARATOR)  # Eat '.'
            field_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)

            # Check if the current_type is a user-defined type and exists in the user_type_table
            if current_type not in self.user_type_table:
                self.error(f"Type '{current_type}' is not a user-defined type", token)

            fields = self.user_type_table[current_type]
            if field_name not in fields:
                self.error(f"Field '{field_name}' does not exist on type '{current_type}'", token)

            # Update the current type to the type of the field
            current_type = fields[field_name].var_type  # Get the type of the field

            # Update the instance to the new FieldAccessNode
            instance = FieldAccessNode(token.srcpos, instance, field_name, current_type)

        return instance
    
    def factor(self):
        token = self.current_token

        # Handle unary operators
        if token.type == TokenType.OPERATOR and token.value in ['-', '+', '!']:
            self.eat(TokenType.OPERATOR)
            node = self.factor()
            return UnaryOpNode(token.srcpos, token.value, node)
    
        if token.type == TokenType.SEPARATOR and token.value == '(':
            self.expect('(')  # Eat '('
            node = self.expr()
            self.expect(')')
            return node
        elif token.type == TokenType.INT or token.type == TokenType.FLT:
            self.eat(token.type)
            return NumberNode(token.srcpos, token.value)
        elif token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '.':
                return self.parse_field_access(token.value)
            if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '(':
                return self.parse_function_call(token.value)
            if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '[':
                self.expect("[")
                index = self.expr()
                self.expect("]")
                return ArrayAccessNode(token.srcpos, token.value, index)
            return IdentifierNode(token.srcpos, token.value)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token.srcpos, token.value)
        else:
            self.error(f"Unexpected token '{token.value}'")


    def term(self):
        node = self.factor()
        
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in '*/':
            token = self.current_token
            self.eat(TokenType.OPERATOR)
            node = BinOpNode(token.srcpos, node, token.value, self.factor())
        
        return node
    
    def expr(self):
        return self.logical_or()

    def additive(self):
        node = self.term()
        
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in '+-':
            token = self.current_token
            self.eat(TokenType.OPERATOR)
            node = BinOpNode(token.srcpos, node, token.value, self.term())
        
        return node
    
    def comparison(self):
        node = self.additive()
        
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['<', '<=', '>', '>=']:
            token = self.current_token
            self.eat(TokenType.OPERATOR)
            node = BinOpNode(token.srcpos, node, token.value, self.additive())
        
        return node
    
    def equality(self):
        node = self.comparison()
        
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['==', '!=']:
            token = self.current_token
            self.eat(TokenType.OPERATOR)
            node = BinOpNode(token.srcpos, node, token.value, self.comparison())
        
        return node
    
    def logical_and(self):
        node = self.equality()
        
        while self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'and':
            token = self.current_token
            self.eat(TokenType.KEYWORD)
            node = BinOpNode(token.srcpos, node, token.value, self.equality())
        
        return node

    def logical_or(self):
        node = self.logical_and()
        
        while self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'or':
            token = self.current_token
            self.eat(TokenType.KEYWORD)
            node = BinOpNode(token.srcpos, node, token.value, self.logical_and())
        
        return node
    
    def parse_if(self):
        token = self.current_token
        self.expect("if")  # Eat IF
        condition = self.expr()
        self.expect("then")  # Eat THEN
        true_branch = self.statement()
        false_branch = None
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'else':
            self.expect("else")  # Eat ELSE
            false_branch = self.statement()
        self.expect("endif")
        return IfNode(token.srcpos, condition, true_branch, false_branch)
    
    def parse_for(self):
        token = self.current_token
        self.expect("for")  # Eat FOR
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect("=")  # Eat '='
        start_value = self.expr()
        self.expect("to")  # Eat TO
        end_value = self.expr()
        step_value = NumberNode(token.srcpos, "1")
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'step':
            self.expect("step")  # Eat STEP
            step_value = self.expr()
        loop_body = self.statement()
        self.expect("next")  # Eat NEXT
        return ForNode(token.srcpos, var_name, start_value, end_value, step_value, loop_body)

    
    def parse_while(self):
        token = self.current_token
        self.expect("while")  # Eat WHILE
        condition = self.expr()
        body = self.statement()
        self.expect("wend")  # Eat WEND
        return WhileNode(token.srcpos, condition, body)
    
    def parse_do_loop(self):
        token = self.current_token
        self.expect("do")  # Eat DO
        body = self.statement()
        self.expect("loop")  # Eat LOOP
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'while':
            self.expect("while")  # Eat WHILE
            condition = self.expr()
            return DoWhileNode(token.srcpos, body, condition)
        elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'until':
            self.expect("until")  # Eat UNTIL
            condition = self.expr()
            return DoUntilNode(token.srcpos, body, condition)
        return body  # Infinite loop if no condition
    
    def parse_select_case(self):
        token = self.current_token
        self.expect("select")  # Eat SELECT
        self.expect("case")  # Eat CASE
        expr = self.expr()
        cases = []
        default_case = None
        while self.current_token.type != TokenType.KEYWORD or self.current_token.value != 'end':
            if self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'case':
                self.expect("case")  # Eat CASE
                case_value = self.expr()
                case_body = self.statement()
                cases.append((case_value, case_body))
            elif self.current_token.type == TokenType.KEYWORD and self.current_token.value == 'else':
                self.expect("else")  # Eat ELSE
                default_case = self.statement()
        self.expect("end")  # Eat END
        self.expect("select")  # Eat SELECT
        return SelectCaseNode(token.srcpos, expr, cases, default_case)
    
    def parse_proc(self):
        token = self.current_token
        self.expect("proc")
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect("(")
        
        # Local symbol table
        self.local_symbol_table = {}
        
        params = []
        while self.current_token.type != TokenType.SEPARATOR or self.current_token.value != ')':
            param_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.expect(":")
            
            is_pointer = False
            if self.current_token.value == "ptr":
                is_pointer = True
                self.eat(TokenType.KEYWORD) # skip ptr keyword
            
            # Check if the type is built-in or user-defined
            if self.current_token.type == TokenType.DATATYPE or self.current_token.value in self.user_type_table:
                param_type = self.current_token.value
                self.eat(self.current_token.type)
            else:
                self.error(f"Expected a valid type for parameter '{param_name}', got '{self.current_token.value}'")
            
            params.append((param_name, param_type, is_pointer))
            self.declare_variable(param_name, param_type, is_pointer, scope='local')
            if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == ',':
                self.expect(",")
        self.expect(")")
        self.expect(":")

        is_pointer = False
        if self.current_token.value == "ptr":
            is_pointer = True
            self.eat(TokenType.KEYWORD) # skip ptr keyword, this will be resolved in semant step
        
        # Check if the return type is built-in or user-defined
        if self.current_token.type == TokenType.DATATYPE or self.current_token.value in self.user_type_table:
            return_type = self.current_token.value
            self.eat(self.current_token.type)
        else:
            self.error(f"Expected a valid return type, got '{self.current_token.value}'")
        
        body_statements = []
        while self.current_token.value != 'pend':
            body_statements.append(self.statement())
        
        self.expect("pend")
        
        # Clear the local scope after the procedure is parsed
        self.local_symbol_table = None
        
        return ProcNode(token.srcpos, name, params, body_statements, return_type)

    def parse_return(self):
        token = self.current_token
        self.expect("return")  # Eat 'return'
        value = self.expr()  # The return value expression
        return ReturnNode(token.srcpos, value)
    
    def parse_dim(self):
        token = self.current_token
        self.expect("dim")  # Eat DIM
        array_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect("[")  # Eat '['
        size = self.expr()
        self.expect("]")  # Eat ']'
        self.expect(":")  # Eat ':'
        array_type = self.current_token.value
        self.eat(TokenType.DATATYPE)
        return DimNode(token.srcpos, array_name, size, array_type)
    
    def parse_function_call(self, name):
        token = self.current_token
        self.expect("(")  # Eat '('
        
        arguments = []
        if self.current_token.type != TokenType.SEPARATOR or self.current_token.value != ')':
            while True:
                arguments.append(self.expr())
                if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == ',':
                    self.expect(",")  # Eat ','
                else:
                    break
        
        self.expect(")")  # Eat ')'
        
        return FunctionCallNode(token.srcpos, name, arguments)
    
    def parse_let(self):
        token = self.current_token
        self.expect("let")
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect(":")

        # Check for pointer type
        is_pointer = False
        if self.current_token.value == "ptr":
            is_pointer = True
            self.eat(TokenType.KEYWORD)
        
        # Check if the type is built-in or user-defined
        if self.current_token.type == TokenType.DATATYPE or self.current_token.value in self.user_type_table:
            var_type = self.current_token.value
            self.eat(self.current_token.type)
        else:
            self.error(f"Expected a valid type for variable '{var_name}', got '{self.current_token.value}'")

        self.expect("=")
        
        # Handle new instance creation
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == "new":
            value = self.parse_new_instance()
        else:
            value = self.expr()
        
        # Declare the variable in the appropriate scope with pointer flag
        if self.local_symbol_table is not None:
            self.declare_variable(var_name, var_type, is_pointer, scope='local')
        else:
            self.declare_variable(var_name, var_type, is_pointer, scope='global')
        
        return LetNode(token.srcpos, var_name, value, var_type, is_pointer)

    def parse_assignment(self):
        token = self.current_token
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Start with an identifier node
        node = IdentifierNode(token.srcpos, var_name)

        # Handle array access
        if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '[':
            self.eat(TokenType.SEPARATOR)  # Eat the '['
            index_expr = self.expr()  # Parse the index expression
            self.expect(']')  # Expect and consume the ']'
            node = ArrayAccessNode(token.srcpos, var_name, index_expr)

        # Handle field access
        while self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '.':
            self.eat(TokenType.SEPARATOR)
            field_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            node = FieldAccessNode(token.srcpos, node, field_name, None)
        
        self.expect("=")
        
        # Handle new instance creation
        if self.current_token.type == TokenType.KEYWORD and self.current_token.value == "new":
            value = self.parse_new_instance()
        else:
            value = self.expr()
        
        return AssignmentNode(token.srcpos, node, value)

    def parse_type_definition(self):
        self.expect("type")
        type_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        fields = {}
        while self.current_token.value != "tend":
            self.expect("field")
            field_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.expect(":")
            
            # Check for pointer type
            is_pointer = False
            if self.current_token.value == "ptr":
                is_pointer = True
                self.eat(TokenType.KEYWORD)
            
            # Check if the type is built-in or user-defined
            if self.current_token.type == TokenType.DATATYPE or self.current_token.value in self.user_type_table:
                field_type = self.current_token.value
                self.eat(self.current_token.type)
            else:
                self.error(f"Expected a valid type for field '{field_name}', got '{self.current_token.value}'")
            
            # Handle default values (currently stored for future use)
            default_value = None
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '=':
                self.eat(TokenType.OPERATOR)
                default_value = self.expr()
            
            # Store the field as a Symbol object in the fields dictionary
            fields[field_name] = Symbol(var_type=field_type, is_pointer=is_pointer, default_value=default_value)
        
        self.expect("tend")
        
        # Store the type definition in the user_type_table
        self.user_type_table[type_name] = fields
        
        return TypeNode(type_name, fields)


    def parse_new_instance(self):
        self.expect("new")

        # Check for pointer type
        is_pointer = False
        if self.current_token.value == "ptr":
            is_pointer = True
            self.eat(TokenType.KEYWORD)

        type_name = self.current_token.value

        # Check if the type is a user-defined type or a built-in primitive type
        if type_name not in self.user_type_table and type_name not in self.lexer.data_types:
            self.error(f"Type '{type_name}' is not defined")
        
        self.advance()
        # self.eat(TokenType.IDENTIFIER)

        return NewInstanceNode(type_name, is_pointer)



    
    def statement(self):
        if self.current_token.type == TokenType.KEYWORD:
            if self.current_token.value == 'let':
                return self.parse_let()
            elif self.current_token.value == 'if':
                return self.parse_if()
            elif self.current_token.value == 'for':
                return self.parse_for()
            elif self.current_token.value == 'while':
                return self.parse_while()
            elif self.current_token.value == 'do':
                return self.parse_do_loop()
            elif self.current_token.value == 'select':
                return self.parse_select_case()
            elif self.current_token.value == 'proc':
                return self.parse_proc()
            elif self.current_token.value == 'dim':
                return self.parse_dim()
            elif self.current_token.value == 'return':
                return self.parse_return()
            elif self.current_token.value == 'type':
                return self.parse_type_definition()
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            if self.lexer.input_code[self.lexer.position] == '(':
                self.eat(TokenType.IDENTIFIER) # name
                return self.parse_function_call(name)
            else:
                return self.parse_assignment()
        self.error(f"Unexpected statement '{self.current_token.value}'")


    def parse(self):
        token = self.current_token
        statements = []
        while self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        return ProgramNode(token.srcpos, statements)

