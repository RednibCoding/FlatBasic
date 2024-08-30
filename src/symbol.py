class Symbol:
    def __init__(self, var_type, is_pointer=False, default_value = None, callable=False, params=None, return_type=None):
        self.var_type = var_type
        self.is_pointer = is_pointer
        self.default_value = default_value
        self.callable = callable
        self.params = params if params is not None else []
        self.return_type = return_type

    def __repr__(self):
        pointer_str = 'ptr ' if self.is_pointer else ''
        default_value = f'def. value: {self.default_value} ' if not self.callable else ''
        callable_str = ' (callable)' if self.callable else ''
        params_str = f"Params: {self.params}, " if self.callable else ''
        return_type_str = f"Returns: {self.return_type}" if self.callable else ''
        return f"Symbol({pointer_str}{self.var_type}{callable_str}, {params_str}{return_type_str})"