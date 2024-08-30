class ASTNode:
    pass

class BinOpNode(ASTNode):
    def __init__(self, srcpos, left, op, right):
        self.node_name = "BinOpNode"
        self.srcpos = srcpos
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{self.left.__repr__(indent + 1)},\n"
                f"{ind}  '{self.op}',\n"
                f"{self.right.__repr__(indent + 1)}\n"
                f"{ind})")

class NumberNode(ASTNode):
    def __init__(self, srcpos, value):
        self.node_name = "NumberNode"
        self.srcpos = srcpos
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return f"{ind}{self.node_name}({self.value})"

class IdentifierNode(ASTNode):
    def __init__(self, srcpos, value):
        self.node_name = "IdentifierNode"
        self.srcpos = srcpos
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return f"{ind}{self.node_name}({self.value})"

class StringNode(ASTNode):
    def __init__(self, srcpos, value):
        self.node_name = "StringNode"
        self.srcpos = srcpos
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return f"{ind}{self.node_name}(\"{self.value}\")"

class FunctionCallNode(ASTNode):
    def __init__(self, srcpos, name, arguments):
        self.node_name = "FunctionCallNode"
        self.srcpos = srcpos
        self.name = name
        self.arguments = arguments
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        args = ',\n'.join(arg.__repr__(indent + 1) for arg in self.arguments)
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.name}',\n"
                f"{ind}  [\n{args}\n{ind}  ]\n"
                f"{ind})")

class AssignmentNode(ASTNode):
    def __init__(self, srcpos, var_name, value):
        self.node_name = "AssignmentNode"
        self.srcpos = srcpos
        self.var_name = var_name
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.var_name}',\n"
                f"{self.value.__repr__(indent + 1)}\n"
                f"{ind})")

class ArrayAssignmentNode(ASTNode):
    def __init__(self, srcpos, array_name, index, value):
        self.node_name = "ArrayAssignmentNode"
        self.srcpos = srcpos
        self.array_name = array_name
        self.index = index
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.array_name}',\n"
                f"{self.index.__repr__(indent + 1)},\n"
                f"{self.value.__repr__(indent + 1)}\n"
                f"{ind})")

class LetNode(ASTNode):
    def __init__(self, srcpos, var_name, expr):
        self.node_name = "LetNode"
        self.srcpos = srcpos
        self.var_name = var_name
        self.expr = expr
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.var_name}',\n"
                f"{self.expr.__repr__(indent + 1)}\n"
                f"{ind})")

class IfNode(ASTNode):
    def __init__(self, srcpos, condition, true_branch, false_branch=None):
        self.node_name = "IfNode"
        self.srcpos = srcpos
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        result = f"{ind}{self.node_name}(\n{self.condition.__repr__(indent + 1)},\n{self.true_branch.__repr__(indent + 1)}"
        if self.false_branch:
            result += f",\n{self.false_branch.__repr__(indent + 1)}"
        result += f"\n{ind})"
        return result

class ForNode(ASTNode):
    def __init__(self, srcpos, var_name, start_value, end_value, step_value, loop_body):
        self.node_name = "ForNode"
        self.srcpos = srcpos
        self.var_name = var_name
        self.start_value = start_value
        self.end_value = end_value
        self.step_value = step_value
        self.loop_body = loop_body
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.var_name}',\n"
                f"{self.start_value.__repr__(indent + 1)},\n"
                f"{self.end_value.__repr__(indent + 1)},\n"
                f"{self.step_value.__repr__(indent + 1)},\n"
                f"{self.loop_body.__repr__(indent + 1)}\n"
                f"{ind})")

class WhileNode(ASTNode):
    def __init__(self, srcpos, condition, body):
        self.node_name = "WhileNode"
        self.srcpos = srcpos
        self.condition = condition
        self.body = body
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{self.condition.__repr__(indent + 1)},\n"
                f"{self.body.__repr__(indent + 1)}\n"
                f"{ind})")

class DoWhileNode(ASTNode):
    def __init__(self, srcpos, body, condition):
        self.node_name = "DoWhileNode"
        self.srcpos = srcpos
        self.body = body
        self.condition = condition
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{self.body.__repr__(indent + 1)},\n"
                f"{self.condition.__repr__(indent + 1)}\n"
                f"{ind})")

class DoUntilNode(ASTNode):
    def __init__(self, srcpos, body, condition):
        self.node_name = "DoUntilNode"
        self.srcpos = srcpos
        self.body = body
        self.condition = condition
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{self.body.__repr__(indent + 1)},\n"
                f"{self.condition.__repr__(indent + 1)}\n"
                f"{ind})")

class SelectCaseNode(ASTNode):
    def __init__(self, srcpos, expr, cases, default_case=None):
        self.node_name = "SelectCaseNode"
        self.srcpos = srcpos
        self.expr = expr
        self.cases = cases
        self.default_case = default_case
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        case_repr = '\n'.join(f"{ind}  Case({case[0].__repr__(indent + 1)}):\n{case[1].__repr__(indent + 1)}" for case in self.cases)
        default_repr = f"{ind}  Default:\n{self.default_case.__repr__(indent + 1)}" if self.default_case else ""
        return (f"{ind}{self.node_name}(\n"
                f"{self.expr.__repr__(indent + 1)},\n"
                f"{case_repr}\n"
                f"{default_repr}\n"
                f"{ind})")

class ProcNode(ASTNode):
    def __init__(self, srcpos, name, params, body_statements, return_type):
        self.node_name = "ProcNode"
        self.srcpos = srcpos
        self.name = name
        self.params = params
        self.body_statements = body_statements
        self.return_type = return_type
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        params = ', '.join(f"{name}: {type}" for name, type in self.params)
        body = '\n'.join(stmt.__repr__(indent + 1) for stmt in self.body_statements)
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.name}',\n"
                f"{ind}  Params: [{params}],\n"
                f"{ind}  ReturnType: {self.return_type},\n"
                f"{ind}  Body:\n{body}\n"
                f"{ind})")

class ReturnNode(ASTNode):
    def __init__(self, srcpos, value):
        self.node_name = "ReturnNode"
        self.srcpos = srcpos
        self.value = value
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return f"{ind}{self.node_name}(\n{self.value.__repr__(indent + 1)}\n{ind})"

class DimNode(ASTNode):
    def __init__(self, srcpos, array_name, size, array_type):
        self.node_name = "DimNode"
        self.srcpos = srcpos
        self.array_name = array_name
        self.size = size
        self.array_type = array_type
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return (f"{ind}{self.node_name}(\n"
                f"{ind}  '{self.array_name}',\n"
                f"{self.size.__repr__(indent + 1)},\n"
                f"{ind}  Type: {self.array_type}\n"
                f"{ind})")

class ArrayAccessNode(ASTNode):
    def __init__(self, srcpos, array_name, index):
        self.node_name = "ArrayAccessNode"
        self.srcpos = srcpos
        self.array_name = array_name
        self.index = index
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        return f"{ind}{self.node_name}(\n{ind}  '{self.array_name}',\n{self.index.__repr__(indent + 1)}\n{ind})"

class ProgramNode(ASTNode):
    def __init__(self, srcpos, statements):
        self.node_name = "ProgramNode"
        self.srcpos = srcpos
        self.statements = statements
    
    def __repr__(self, indent=0):
        ind = '    ' * indent
        stmts = '\n'.join(stmt.__repr__(indent + 1) for stmt in self.statements)
        return f"{ind}{self.node_name}(\n{stmts}\n{ind})"
