import sys
from nodes import *

class Symbol:
    def __init__(self, var_type, is_pointer=False, callable=False, params=None, return_type=None):
        self.var_type = var_type
        self.is_pointer = is_pointer
        self.callable = callable
        self.params = params if params is not None else []
        self.return_type = return_type

    def __repr__(self):
        pointer_str = 'ptr ' if self.is_pointer else ''
        callable_str = ' (callable)' if self.callable else ''
        params_str = f"Params: {self.params}, " if self.callable else ''
        return_type_str = f"Returns: {self.return_type}" if self.callable else ''
        return f"Symbol({pointer_str}{self.var_type}{callable_str}, {params_str}{return_type_str})"

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
    
    def visit_ProcNode(self, node):
        # Save current local scope
        saved_local_scope = self.local_scope

        # Set up a new local scope
        self.local_scope = {param_name: Symbol(var_type=param_type, is_pointer=False) for param_name, param_type in node.params}

        # Register the procedure in the global scope
        self.global_scope[node.name] = Symbol(
            var_type='proc',
            is_pointer=True,
            callable=True,
            params=[Symbol(var_type=param_type, is_pointer=False) for _, param_type in node.params],
            return_type=node.return_type
        )

        for stmt in node.body_statements:
            self.visit(stmt)

        # Restore the previous local scope
        self.local_scope = saved_local_scope

    def visit_IdentifierNode(self, node):
        if self.local_scope is not None and node.name in self.local_scope:
            symbol = self.local_scope[node.name]
        elif node.name in self.global_scope:
            symbol = self.global_scope[node.name]
        else:
            self.error(f"Variable or procedure '{node.name}' not defined", node)

        node.var_type = symbol.var_type
        node.is_pointer = symbol.is_pointer
        
        return symbol

    def visit_BinOpNode(self, node):
        left_symbol = self.visit(node.left)
        right_symbol = self.visit(node.right)

        numeric_types = ["char", "uchar", "short", "ushort", "int", "uint", "long", "ulong", "size"]

        # Arithmetic operations
        if node.op in ['+', '-', '*', '/']:
            # Handle pointer arithmetic
            if left_symbol.is_pointer or right_symbol.is_pointer:
                if node.op in ['+', '-']:
                    if (left_symbol.is_pointer and right_symbol.var_type not in numeric_types) or \
                       (right_symbol.is_pointer and left_symbol.var_type not in numeric_types):
                        self.error(f"Pointer arithmetic requires a pointer and a non-floating-point numeric type", node)
                    return Symbol(var_type='ptr', is_pointer=True, return_type=left_symbol.var_type if left_symbol.is_pointer else right_symbol.var_type)
                else:
                    self.error(f"Operation '{node.op}' not allowed on pointers", node)
            
            # Regular numeric arithmetic
            if left_symbol.var_type not in numeric_types or right_symbol.var_type not in numeric_types:
                self.error(f"Arithmetic operations require numeric operands", node)
            
            return Symbol(var_type=self.promote_type(left_symbol.var_type, right_symbol.var_type))
        
        # Comparison operations
        if node.op in ['<', '<=', '>', '>=', '==', '!=']:
            if left_symbol.is_pointer != right_symbol.is_pointer:
                self.error(f"Comparison operations require both operands to be either pointers or the same numeric type", node)
            return Symbol(var_type='int')
        
        # Logical operations
        if node.op in ['and', 'or']:
            if left_symbol.var_type != 'int' or right_symbol.var_type != 'int':
                self.error(f"Logical operations require integer (boolean) operands", node)
            return Symbol(var_type='int')

        self.error(f"Unknown binary operator {node.op}", node)

    def promote_type(self, left_type, right_type):
        # Define a type hierarchy
        type_hierarchy = {
            "char": 1,
            "uchar": 2,
            "short": 3,
            "ushort": 4,
            "int": 5,
            "uint": 6,
            "size": 7,
            "long": 8,
            "ulong": 9,
            "float": 10,
            "double": 11
        }

        # Promote to the type with the highest rank
        if type_hierarchy[left_type] > type_hierarchy[right_type]:
            return left_type
        else:
            return right_type

    def visit_NumberNode(self, node):
        value_str = str(node.value)
        if '.' in value_str:
            return Symbol(var_type='double')
        else:
            return Symbol(var_type='int')

    def visit_StringNode(self, node):
        return Symbol(var_type='string')

    def visit_AssignmentNode(self, node):
        value_symbol = self.visit(node.value)
        if self.local_scope is not None:
            self.local_scope[node.var_name] = value_symbol
        else:
            self.global_scope[node.var_name] = value_symbol

    def visit_ArrayAssignmentNode(self, node):
        if node.array_name not in self.global_scope:
            self.error(f"array '{node.array_name}' not defined", node)

        index_symbol = self.visit(node.index)
        valid_index_types = ["char", "uchar", "short", "ushort", "int", "uint", "long", "ulong", "size"]
        if index_symbol.var_type not in valid_index_types:
            self.error(f"array index must be a non-floating-point numeric type, got {index_symbol.var_type}", node)

        array_symbol = self.global_scope[node.array_name]
        value_symbol = self.visit(node.value)
        if value_symbol.var_type != array_symbol.var_type:
            self.error(f"array '{node.array_name}' expects elements of type {array_symbol.var_type}, got {value_symbol.var_type}", node)

    def visit_ArrayAccessNode(self, node):
        if node.array_name not in self.global_scope:
            self.error(f"array '{node.array_name}' not defined", node)

        index_symbol = self.visit(node.index)
        valid_index_types = ["char", "uchar", "short", "ushort", "int", "uint", "long", "ulong", "size"]
        if index_symbol.var_type not in valid_index_types:
            self.error(f"array index must be a non-floating-point numeric type, got {index_symbol.var_type}", node)

        array_symbol = self.global_scope[node.array_name]
        return Symbol(var_type=array_symbol.var_type, is_pointer=array_symbol.is_pointer)

    def visit_LetNode(self, node):
        value_symbol = self.visit(node.expr)
        if self.local_scope is not None:
            self.local_scope[node.var_name] = value_symbol
        else:
            self.global_scope[node.var_name] = value_symbol

    def visit_IfNode(self, node):
        condition_symbol = self.visit(node.condition)
        if condition_symbol.var_type != "int":
            self.error(f"condition expression must be an integer, got {condition_symbol.var_type}", node)
        
        self.visit(node.true_branch)
        if node.false_branch:
            self.visit(node.false_branch)

    def visit_ForNode(self, node):
        self.visit_LetNode(LetNode(node.srcpos, node.var_name, node.start_value))  # Initialize the loop variable
        start_symbol = self.visit(node.start_value)
        end_symbol = self.visit(node.end_value)
        step_symbol = self.visit(node.step_value)

        if start_symbol.var_type != "int" or end_symbol.var_type != "int" or step_symbol.var_type != "int":
            self.error(f"for loop bounds and step must be integers", node)
        
        self.visit(node.loop_body)

    def visit_WhileNode(self, node):
        condition_symbol = self.visit(node.condition)
        if condition_symbol.var_type != "int":
            self.error(f"condition expression must be an integer, got {condition_symbol.var_type}", node)
        self.visit(node.body)

    def visit_DoWhileNode(self, node):
        self.visit(node.body)
        condition_symbol = self.visit(node.condition)
        if condition_symbol.var_type != "int":
            self.error(f"condition expression must be an integer, got {condition_symbol.var_type}", node)

    def visit_DoUntilNode(self, node):
        self.visit(node.body)
        condition_symbol = self.visit(node.condition)
        if condition_symbol.var_type != "int":
            self.error(f"condition expression must be an integer, got {condition_symbol.var_type}", node)

    def visit_SelectCaseNode(self, node):
        expr_symbol = self.visit(node.expr)
        for case_value, case_body in node.cases:
            case_value_symbol = self.visit(case_value)
            if case_value_symbol.var_type != expr_symbol.var_type:
                self.error(f"case value type {case_value_symbol.var_type} does not match select expression type {expr_symbol.var_type}", node)
            self.visit(case_body)

        if node.default_case:
            self.visit(node.default_case)

    def visit_ReturnNode(self, node):
        return_symbol = self.visit(node.value)
        return return_symbol

    def visit_DimNode(self, node):
        if node.array_name in self.global_scope:
            self.error(f"array '{node.array_name}' already defined", node)
        self.global_scope[node.array_name] = Symbol(var_type=node.array_type, is_pointer=False)

    def visit_TypeNode(self, node):
        self.global_scope[node.type_name] = node.fields

    def visit_NewInstanceNode(self, node):
        if node.type_name not in self.global_scope:
            self.error(f"Type '{node.type_name}' not defined", node)
        return Symbol(var_type=node.type_name, is_pointer=True)

    def visit_FieldAccessNode(self, node):
        instance_symbol = self.visit(node.instance)
        if instance_symbol.var_type not in self.global_scope:
            self.error(f"Type '{instance_symbol.var_type}' not defined", node)

        fields = self.global_scope[instance_symbol.var_type]
        if node.field_name not in fields:
            self.error(f"Field '{node.field_name}' not found in type '{instance_symbol.var_type}'", node)
        
        field_info = fields[node.field_name]
        return Symbol(var_type=field_info['type'], is_pointer=field_info.get('is_pointer', False))

    def visit_FunctionCallNode(self, node):
        if node.name not in self.global_scope:
            self.error(f"Function '{node.name}' not defined", node)

        symbol = self.global_scope[node.name]

        if not symbol.callable:
            self.error(f"'{node.name}' is not a function or procedure", node)

        expected_params = symbol.params
        expected_return_type = symbol.return_type

        if len(node.arguments) != len(expected_params):
            self.error(f"Function '{node.name}' expects {len(expected_params)} arguments, got {len(node.arguments)}", node)

        for i, (arg, expected_param) in enumerate(zip(node.arguments, expected_params)):
            arg_symbol = self.visit(arg)
            if arg_symbol.var_type != expected_param.var_type or arg_symbol.is_pointer != expected_param.is_pointer:
                self.error(f"Argument {i+1} of function '{node.name}' should be of type '{expected_param.var_type}', got '{arg_symbol.var_type}'", node)

        return Symbol(var_type=expected_return_type, is_pointer=False)
