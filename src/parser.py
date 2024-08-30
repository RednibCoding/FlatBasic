import sys
from nodes import *
from tokentype import TokenType

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.global_symbol_table = {}  # Global scope
        self.local_symbol_table = None  # Local scope, set within procedures
    
    def error(self, message="Syntax error"):
        print(f"error at {self.current_token.srcpos.filename}:{self.current_token.srcpos.line}:{self.current_token.srcpos.column} : {message}")
        sys.exit()
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected token {token_type}, got '{self.current_token.value}' {self.current_token.type}")
    
    def expect(self, token_value):
        if self.current_token.value == token_value:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected token '{token_value}', got '{self.current_token.value}'")
    
    def declare_variable(self, var_name, var_type, scope='global'):
        symbol_table = self.global_symbol_table if scope == 'global' else self.local_symbol_table
        if var_name in symbol_table:
            self.error(f"Variable '{var_name}' already declared in this scope")
        symbol_table[var_name] = var_type
    
    def factor(self):
        token = self.current_token
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
    
    def parse_let(self):
        token = self.current_token
        self.expect("let")  # Eat LET
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect(":")  # Eat ':'
        var_type = self.current_token.value
        self.eat(TokenType.DATATYPE)
        self.expect("=")  # Eat '='
        expr = self.expr()
        
        # Ensure the variable is declared in the correct scope
        if self.local_symbol_table is not None:
            self.declare_variable(var_name, var_type, scope='local')
        else:
            self.declare_variable(var_name, var_type, scope='global')
        
        return LetNode(token.srcpos, var_name, expr)
    
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
        self.expect("proc")  # Eat PROC
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.expect("(")  # Eat '('
        
        # Local symbol table
        self.local_symbol_table = {}
        
        params = []
        while self.current_token.type != TokenType.SEPARATOR or self.current_token.value != ')':
            param_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.expect(":")  # Eat ':'
            param_type = self.current_token.value
            self.eat(TokenType.DATATYPE)
            params.append((param_name, param_type))
            self.declare_variable(param_name, param_type, scope='local')
            if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == ',':
                self.expect(",")  # Eat ','
        self.expect(")")  # Eat ')'
        self.expect(":")  # Eat ':'
        return_type = self.current_token.value
        self.eat(TokenType.DATATYPE)
        
        body_statements = []
        while self.current_token.value != 'pend':  # Parse until we find 'pend'
            if self.current_token.value == "proc":
                self.error("Unexpected token 'proc'")
            body_statements.append(self.statement())
        
        # Ensure the procedure ends with 'pend'
        if self.current_token.value != 'pend':
            self.error("Expected 'pend' to close procedure")
        self.expect("pend")  # Eat 'pend'
        
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

    
    def parse_assignment(self):
        token = self.current_token
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        if self.current_token.type == TokenType.SEPARATOR and self.current_token.value == '[':
            self.expect("[")  # Eat '['
            index = self.expr()
            self.expect("]")  # Eat ']'
            self.expect("=")  # Eat '='
            value = self.expr()
            return ArrayAssignmentNode(token.srcpos, var_name, index, value)
        
        self.expect("=")  # Eat '='
        value = self.expr()
        return AssignmentNode(token.srcpos, var_name, value)


    
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

