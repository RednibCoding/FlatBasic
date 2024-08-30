import sys
from nodes import *

class Semanter:
    def __init__(self):
        self.global_scope = {}
        self.local_scope = None

    def error(self, message, node):
        print(f"error: {node.srcpos.filename}:{node.srcpos.line}:{node.srcpos.column}:\n\t-> {message}")
        sys.exit()
    
    def analyze(self, node):
        self.visit(node)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_UnaryOpNode(self, node):
        expr_type = self.visit(node.expr)
        
        # Handle the unary minus and plus (numeric)
        if node.op in ['-', '+']:
            if expr_type not in ['int', 'flt']:
                self.error(f"Unary '{node.op}' operator requires numeric operand, got {expr_type}", node)
            return expr_type  # The result type is the same as the operand
        
        # Handle logical negation
        if node.op == '!':
            if expr_type != 'int':
                self.error(f"Unary '!' operator requires an integer (boolean) operand, got {expr_type}", node)
            return 'int'  # Logical negation returns an integer (boolean)
        
        self.error(f"Unknown unary operator {node.op}", node)


    def visit_BinOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        # Arithmetic operations
        if node.op in ['+', '-', '*', '/']:
            if left_type not in ['int', 'flt'] or right_type not in ['int', 'flt']:
                self.error(f"Arithmetic operations require numeric operands, got {left_type} and {right_type}", node)
            
            # Promote to 'flt' if either operand is a float
            if left_type == 'flt' or right_type == 'flt':
                return 'flt'
            return 'int'
        
        # Comparison operations
        if node.op in ['<', '<=', '>', '>=', '==', '!=']:
            if left_type not in ['int', 'flt'] or right_type not in ['int', 'flt']:
                self.error(f"Comparison operations require numeric operands, got {left_type} and {right_type}", node)
            
            # Allow comparison between int and flt
            if left_type != right_type:
                if 'int' in [left_type, right_type] and 'flt' in [left_type, right_type]:
                    return 'int'  # Comparison result is always 'int'
                else:
                    self.error(f"Comparison operations require compatible numeric types, got {left_type} and {right_type}", node)
            
            # Comparisons return 'int' as a boolean type
            return 'int'
        
        # Logical operations
        if node.op in ['and', 'or']:
            if left_type != 'int' or right_type != 'int':
                self.error(f"Logical operations require integer (boolean) operands, got {left_type} and {right_type}", node)
            return 'int'
        
        self.error(f"Unknown binary operator {node.op}", node)


    def visit_NumberNode(self, node):
        return 'int' if '.' not in str(node.value) else 'flt'

    def visit_StringNode(self, node):
        return 'str'

    def visit_IdentifierNode(self, node):
        if self.local_scope is not None and node.value in self.local_scope:
            return self.local_scope[node.value]
        elif node.value in self.global_scope:
            return self.global_scope[node.value]
        else:
            self.error(f"variable '{node.value}' not defined", node)

    def visit_FunctionCallNode(self, node):
        if node.name not in self.global_scope:
            self.error(f"function '{node.name}' not defined", node)

        func_type = self.global_scope[node.name]
        expected_params = func_type['params']
        expected_return_type = func_type['return_type']

        if len(node.arguments) != len(expected_params):
            self.error(f"function '{node.name}' expects {len(expected_params)} arguments, got {len(node.arguments)}", node)

        for i, (arg, expected_type) in enumerate(zip(node.arguments, expected_params)):
            arg_type = self.visit(arg)
            if arg_type != expected_type:
                self.error(f"argument {i+1} of function '{node.name}' should be of type '{expected_type}', got '{arg_type}'", node)

        return expected_return_type

    def visit_AssignmentNode(self, node):
        value_type = self.visit(node.value)
        if self.local_scope is not None:
            self.local_scope[node.var_name] = value_type
        else:
            self.global_scope[node.var_name] = value_type

    def visit_ArrayAssignmentNode(self, node):
        if node.array_name not in self.global_scope:
            self.error(f"array '{node.array_name}' not defined", node)

        index_type = self.visit(node.index)
        if index_type != 'int':
            self.error(f"array index must be an integer, got {index_type}", node)

        array_type = self.global_scope[node.array_name]
        value_type = self.visit(node.value)
        if value_type != array_type:
            self.error(f"array '{node.array_name}' expects elements of type {array_type}, got {value_type}", node)

    def visit_ArrayAccessNode(self, node):
        if node.array_name not in self.global_scope:
            self.error(f"array '{node.array_name}' not defined", node)

        index_type = self.visit(node.index)
        if index_type != 'int':
            self.error(f"array index must be an integer, got {index_type}", node)

        return self.global_scope[node.array_name]

    def visit_ProcNode(self, node):
        # Save current local scope
        saved_local_scope = self.local_scope

        # Set up a new local scope
        self.local_scope = {param_name: param_type for param_name, param_type in node.params}

        # Register the procedure in the global scope
        self.global_scope[node.name] = {
            'params': [param_type for _, param_type in node.params],
            'return_type': node.return_type
        }

        for stmt in node.body_statements:
            self.visit(stmt)

        self.local_scope = saved_local_scope

    def visit_LetNode(self, node):
        var_type = self.visit(node.expr)
        if self.local_scope is not None:
            self.local_scope[node.var_name] = var_type
        else:
            self.global_scope[node.var_name] = var_type

    def visit_IfNode(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'int':  # Assuming conditions are integers (1 = true, 0 = false)
            self.error(f"condition expression must be an integer, got {condition_type}", node)
        
        self.visit(node.true_branch)
        if node.false_branch:
            self.visit(node.false_branch)

    def visit_ForNode(self, node):
        self.visit_LetNode(LetNode(node.srcpos, node.var_name, node.start_value))  # Initialize the loop variable
        start_type = self.visit(node.start_value)
        end_type = self.visit(node.end_value)
        step_type = self.visit(node.step_value)

        if start_type != 'int' or end_type != 'int' or step_type != 'int':
            self.error(f"for loop bounds and step must be integers", node)
        
        self.visit(node.loop_body)

    def visit_WhileNode(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'int':
            self.error(f"condition expression must be an integer, got {condition_type}", node)
        self.visit(node.body)

    def visit_DoWhileNode(self, node):
        self.visit(node.body)
        condition_type = self.visit(node.condition)
        if condition_type != 'int':
            self.error(f"condition expression must be an integer, got {condition_type}", node)

    def visit_DoUntilNode(self, node):
        self.visit(node.body)
        condition_type = self.visit(node.condition)
        if condition_type != 'int':
            self.error(f"condition expression must be an integer, got {condition_type}", node)

    def visit_SelectCaseNode(self, node):
        expr_type = self.visit(node.expr)
        for case_value, case_body in node.cases:
            case_value_type = self.visit(case_value)
            if case_value_type != expr_type:
                self.error(f"case value type {case_value_type} does not match select expression type {expr_type}", node)
            self.visit(case_body)

        if node.default_case:
            self.visit(node.default_case)

    def visit_ReturnNode(self, node):
        return_type = self.visit(node.value)
        return return_type

    def visit_DimNode(self, node):
        if node.array_name in self.global_scope:
            self.error(f"array '{node.array_name}' already defined", node)
        self.global_scope[node.array_name] = node.array_type
