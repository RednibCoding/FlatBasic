from symbol import Symbol
import sys
from nodes import *
from syntax import Syntax

class Semanter:
    def __init__(self):
        self.global_scope = {}
        self.local_scope = None

    def error(self, message, node):
        print(f"[error] {node.srcpos.filename}:{node.srcpos.line}:{node.srcpos.column}:\n\t-> {message}")
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

        # Set up a new local scope with correct pointer information
        self.local_scope = {
            param_name: Symbol(var_type=param_type, is_pointer=is_pointer)
            for param_name, param_type, is_pointer in node.params
        }

        # Register the procedure in the global scope
        self.global_scope[node.name] = Symbol(
            var_type='size',
            is_pointer=True,  # Procedures are considered pointers
            callable=True,
            params=[Symbol(var_type=param_type, is_pointer=is_pointer) for _, param_type, is_pointer in node.params],
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
    
    def visit_UnaryOpNode(self, node):
        expr_symbol = self.visit(node.expr)
        # Handle the unary minus and plus (numeric)
        if node.op in ['-', '+']:
            if expr_symbol.is_pointer:
                self.error(f"Unary '{node.op}' operator cannot be applied to pointers", node)
            if expr_symbol.var_type not in Syntax.numeric_types:
                self.error(f"Unary '{node.op}' operator requires numeric operand, got {expr_symbol.var_type}", node)
            return Symbol(var_type=expr_symbol.var_type, is_pointer=False)

        # Handle logical negation
        if node.op == '!':
            if expr_symbol.var_type != 'int':
                self.error(f"Unary '!' operator requires an integer (boolean) operand, got {expr_symbol.var_type}", node)
            return Symbol(var_type='int', is_pointer=False)
        
        self.error(f"Unknown unary operator {node.op}", node)


    def visit_BinOpNode(self, node):
        left_symbol = self.visit(node.left)
        right_symbol = self.visit(node.right)

        # Arithmetic operations
        if node.op in ['+', '-', '*', '/']:
            # Handle pointer arithmetic
            if left_symbol.is_pointer or right_symbol.is_pointer:
                if node.op in ['+', '-']:
                    if (left_symbol.is_pointer and right_symbol.var_type not in Syntax.none_float_numeric_data_types) or \
                       (right_symbol.is_pointer and left_symbol.var_type not in Syntax.none_float_numeric_data_types):
                        self.error(f"Pointer arithmetic requires a pointer and a non-floating-point numeric type", node)
                    return Symbol(var_type=self.promote_type(left_symbol.var_type, right_symbol.var_type), is_pointer=True, return_type=left_symbol.var_type if left_symbol.is_pointer else right_symbol.var_type)
                else:
                    self.error(f"Operation '{node.op}' not allowed on pointers", node)
            
            # Regular numeric arithmetic
            if left_symbol.var_type not in Syntax.numeric_data_types or right_symbol.var_type not in Syntax.numeric_data_types:
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

    def visit_NumberNode(self, node, expected_type=None):
        value_str = str(node.value)
        
        if expected_type:
            # Check if the value is a floating-point number
            if '.' in value_str:
                # If the expected type is an integer type, raise an error
                if expected_type in Syntax.none_float_numeric_data_types:
                    self.error(f"Type mismatch: cannot assign a floating-point value '{node.value}' to '{expected_type}'", node)
                # Check if the expected type is float or double
                elif expected_type == "float":
                    if not self.is_value_in_range(node.value, "float"):
                        self.error(f"Value '{node.value}' out of range for type 'float'", node)
                elif expected_type == "double":
                    if not self.is_value_in_range(node.value, "double"):
                        self.error(f"Value '{node.value}' out of range for type 'double'", node)
                return Symbol(var_type=expected_type)
            else:
                # If the value is an integer, perform range check based on the expected type
                if not self.is_value_in_range(node.value, expected_type):
                    self.error(f"Value '{node.value}' out of range for type '{expected_type}'", node)
                return Symbol(var_type=expected_type)
    
        # If no expected type is provided, determine the type based on the value
        if '.' in value_str:
            return Symbol(var_type='double')
        else:
            return Symbol(var_type='int')



    def visit_StringNode(self, node):
        return Symbol(var_type='string')
    
    def is_compatible_type(self, var_symbol, value_symbol):
        # Exact type match
        if var_symbol.var_type == value_symbol.var_type and var_symbol.is_pointer == value_symbol.is_pointer:
            return True

        # Handle pointer arithmetic
        if var_symbol.is_pointer:
            # Allow assigning the result of pointer arithmetic to a pointer variable
            if value_symbol.is_pointer and var_symbol.var_type == value_symbol.var_type:
                return True
            # Allow pointer + integer or pointer - integer
            if not value_symbol.is_pointer and value_symbol.var_type in Syntax.none_float_numeric_data_types:
                return True
            return False

        # Handle numeric type promotion
        var_rank = Syntax.numeric_type_hierarchy.get(var_symbol.var_type)
        value_rank = Syntax.numeric_type_hierarchy.get(value_symbol.var_type)

        if var_rank is None or value_rank is None:
            # If either type is not a recognized numeric type, they must be an exact match to be compatible
            return False

        # Allow assigning smaller or equal integer types to larger integer types
        if var_rank >= value_rank:
            # Ensure that ulong/long cannot be assigned to float
            if var_symbol.var_type == "float" and value_symbol.var_type in ["long", "ulong"]:
                return False
            return True

        # Prevent assigning a floating-point type to an integer type
        if var_symbol.var_type in Syntax.none_float_numeric_data_types and \
                value_symbol.var_type in Syntax.float_numeric_data_types:
            return False

        # If the value rank is higher than the variable rank, it's not compatible
        return False


    
    def is_value_in_range(self, value, var_type):
        # Convert the string value to an integer or float
        try:
            if '.' in str(value):
                numeric_value = float(value)
            else:
                numeric_value = int(value)
        except ValueError:
            self.error(f"Invalid numeric value: {value}", None)

        if var_type not in Syntax.numeric_data_type_ranges:
            # No range checking for non-integer types like float, double, etc.
            return True
        
        min_value, max_value = Syntax.numeric_data_type_ranges[var_type]
        return min_value <= numeric_value <= max_value
    
    def get_variable_type(self, var_name_node):
        if isinstance(var_name_node, IdentifierNode):
            if self.local_scope is not None and var_name_node.name in self.local_scope:
                return self.local_scope[var_name_node.name].var_type
            elif var_name_node.name in self.global_scope:
                return self.global_scope[var_name_node.name].var_type
        elif isinstance(var_name_node, FieldAccessNode):
            var_symbol = self.visit(var_name_node)
            return var_symbol.var_type
        elif isinstance(var_name_node, ArrayAccessNode):
            var_symbol = self.visit(var_name_node)
            return var_symbol.var_type
        
        self.error(f"Variable '{var_name_node.name}' not defined", var_name_node)
        return None
    
    def visit_LetNode(self, node):
        # Determine the symbol for the variable being declared
        var_symbol = Symbol(var_type=node.var_type, is_pointer=node.is_pointer)

        # Handle NumberNode with expected type
        if isinstance(node.expr, NumberNode):
            expected_type = var_symbol.var_type

            value_symbol = self.visit_NumberNode(node.expr, expected_type=expected_type)

            # Check if the literal value fits within the expected type range
            if not self.is_value_in_range(node.expr.value, expected_type):
                self.error(f"Value {node.expr.value} out of range for type '{expected_type}'", node)

            # Disallow assigning a float to an integer type
            if expected_type in Syntax.none_float_numeric_data_types and \
            value_symbol.var_type in Syntax.float_numeric_data_types:
                self.error(f"Type mismatch: cannot assign a floating-point value to '{expected_type}'", node)
        else:
            value_symbol = self.visit(node.expr)

        # Type checking
        if not self.is_compatible_type(var_symbol, value_symbol):
            self.error(f"Type mismatch in declaration: cannot assign '{value_symbol.var_type}' to '{var_symbol.var_type}'", node)

        # Pointer type checking
        if var_symbol.is_pointer != value_symbol.is_pointer:
            self.error(f"Pointer mismatch in declaration: cannot assign {'a pointer' if value_symbol.is_pointer else 'a non-pointer'} to {'a pointer' if var_symbol.is_pointer else 'a non-pointer'}", node)

        # Store the variable symbol in the appropriate scope
        if self.local_scope is not None:
            self.local_scope[node.var_name] = value_symbol
        else:
            self.global_scope[node.var_name] = value_symbol



    def visit_AssignmentNode(self, node):
        if isinstance(node.value, NumberNode):
            expected_type = self.get_variable_type(node.var_name)
            value_symbol = self.visit_NumberNode(node.value, expected_type=expected_type)

            # Check if the literal value fits within the expected type range
            if not self.is_value_in_range(node.value.value, expected_type):
                self.error(f"Value {node.value.value} out of range for type '{expected_type}'", node)
        else:
            value_symbol = self.visit(node.value)
        
        if isinstance(node.var_name, IdentifierNode):
            if self.local_scope is not None and node.var_name.name in self.local_scope:
                var_symbol = self.local_scope[node.var_name.name]
            elif node.var_name.name in self.global_scope:
                var_symbol = self.global_scope[node.var_name.name]
            else:
                self.error(f"Variable '{node.var_name.name}' not defined", node)
        elif isinstance(node.var_name, FieldAccessNode):
            var_symbol = self.visit(node.var_name)
        elif isinstance(node.var_name, ArrayAccessNode):
            var_symbol = self.visit(node.var_name)
        else:
            self.error(f"Invalid assignment target", node)

        if not self.is_compatible_type(var_symbol, value_symbol):
            self.error(f"Type mismatch in assignment: cannot assign '{value_symbol.var_type}' to '{var_symbol.var_type}'", node)
        
        if var_symbol.is_pointer != value_symbol.is_pointer:
            self.error(f"Pointer mismatch in assignment: cannot assign {'a pointer' if value_symbol.is_pointer else 'a non-pointer'} to {'a pointer' if var_symbol.is_pointer else 'a non-pointer'}", node)
        
        if self.local_scope is not None:
            self.local_scope[node.var_name] = var_symbol
        else:
            self.global_scope[node.var_name] = var_symbol

    def visit_ArrayAssignmentNode(self, node):
        if node.array_name not in self.global_scope:
            self.error(f"array '{node.array_name}' not defined", node)

        # Check the index type
        index_symbol = self.visit(node.index)
        valid_index_types = Syntax.none_float_numeric_data_types
        if index_symbol.var_type not in valid_index_types:
            self.error(f"array index must be a non-floating-point numeric type, got {index_symbol.var_type}", node)

        # Retrieve the array's element type
        array_symbol = self.global_scope[node.array_name]
        
        # Handle NumberNode with expected type
        if isinstance(node.value, NumberNode):
            expected_type = array_symbol.var_type
            value_symbol = self.visit_NumberNode(node.value, expected_type=expected_type)

            # Check if the literal value fits within the expected type range
            if not self.is_value_in_range(node.value.value, expected_type):
                self.error(f"Value {node.value.value} out of range for type '{expected_type}'", node)
        else:
            value_symbol = self.visit(node.value)
        
        # Type compatibility check
        if value_symbol.var_type != array_symbol.var_type:
            self.error(f"array '{node.array_name}' expects elements of type {array_symbol.var_type}, got {value_symbol.var_type}", node)
        
        # Pointer type compatibility check
        if value_symbol.is_pointer != array_symbol.is_pointer:
            self.error(f"Pointer mismatch: cannot assign {'a pointer' if value_symbol.is_pointer else 'a non-pointer'} to array of {'pointers' if array_symbol.is_pointer else 'non-pointers'}", node)


    def visit_ArrayAccessNode(self, node):
        if node.name not in self.global_scope:
            self.error(f"array '{node.name}' not defined", node)

        index_symbol = self.visit(node.index)
        valid_index_types = Syntax.none_float_numeric_data_types
        if index_symbol.var_type not in valid_index_types:
            self.error(f"array index must be a non-floating-point numeric type, got {index_symbol.var_type}", node)

        array_symbol = self.global_scope[node.name]
        return Symbol(var_type=array_symbol.var_type, is_pointer=array_symbol.is_pointer)

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
        if node.name in self.global_scope:
            self.error(f"array '{node.name}' already defined", node)
        self.global_scope[node.name] = Symbol(var_type=node.array_type, is_pointer=False)

    def visit_TypeNode(self, node):
        self.global_scope[node.type_name] = node.fields

    def visit_NewInstanceNode(self, node):
        if node.type_name not in self.global_scope and node.type_name not in Syntax.data_types:
            self.error(f"Type '{node.type_name}' not defined", node)
        return Symbol(var_type=node.type_name, is_pointer=node.is_pointer)

    def visit_FieldAccessNode(self, node):
        instance_symbol = self.visit(node.instance)
        if instance_symbol.var_type not in self.global_scope:
            self.error(f"Type '{instance_symbol.var_type}' not defined", node)

        fields = self.global_scope[instance_symbol.var_type]
        if node.name not in fields:
            self.error(f"Field '{node.name}' not found in type '{instance_symbol.var_type}'", node)
        
        field_info = fields[node.name]
        return Symbol(var_type=field_info.var_type , is_pointer=field_info.is_pointer)

    def visit_FunctionCallNode(self, node):
        if node.name not in self.global_scope:
            self.error(f"Function '{node.name}' not defined", node)

        symbol = self.global_scope[node.name]

        if not symbol.callable:
            self.error(f"'{node.name}' is not callable", node)

        expected_params = symbol.params
        expected_return_type = symbol.return_type

        if len(node.arguments) != len(expected_params):
            self.error(f"function '{node.name}' expects {len(expected_params)} arguments, got {len(node.arguments)}", node)

        for i, (arg, expected_param) in enumerate(zip(node.arguments, expected_params)):
            arg_symbol = self.visit(arg)
            if arg_symbol.var_type != expected_param.var_type or arg_symbol.is_pointer != expected_param.is_pointer:
                expected_ptr = "ptr " if expected_param.is_pointer else ""
                got_ptr = "ptr " if arg_symbol.is_pointer else ""
                self.error(f"argument {i+1} of function '{node.name}' should be of type '{expected_ptr}{expected_param.var_type}', got '{got_ptr}{arg_symbol.var_type}'", node)

        return Symbol(var_type=expected_return_type, is_pointer=False)
