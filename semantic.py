class Variable:
    def __init__(self, name, tipo, is_param):
        self.name = name
        self.tipo = tipo
        self.is_param = is_param

class VarTable:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, tipo, is_param=False):
        if name in self.variables:
            raise Exception(f"Variable '{name}' already declared.")
        self.variables[name] = Variable(name, tipo, is_param)

    def get_type(self, name):
        if name in self.variables:
            return self.variables[name].tipo
        return None

class Function:
    def __init__(self, name, start_quad):
        self.name = name
        self.var_table = VarTable()
        self.start_quad = start_quad

class FunctionDirectory:
    def __init__(self):
        self.functions = {}
        self.global_var_table = VarTable()

    def add_function(self, name, start_quad):
        if name in self.functions:
            raise Exception(f"Function '{name}' already declared.")
        self.functions[name] = Function(name, start_quad)

    def add_variable(self, name, tipo, function_name, is_param):
        if function_name != "global" and function_name not in self.functions:
            raise Exception(f"Function '{function_name}' not declared.")

        if function_name == "global":
            if name in self.global_var_table.variables:
                raise Exception(f"Variable '{name}' already declared in global scope.")
            self.global_var_table.add_variable(name, tipo)
        else:
            func = self.functions[function_name]
            if name in func.var_table.variables:
                raise Exception(f"Variable '{name}' already declared in function '{function_name}'.")
            func.var_table.add_variable(name, tipo, is_param)

    def get_variable_type(self, name, scope):
        if scope != "global":
            if scope in self.functions:
                tipo = self.functions[scope].var_table.get_type(name)
                if tipo:
                    return tipo
        return self.global_var_table.get_type(name)

    def has_variable(self, scope, name):
        if scope == 'global':
            if name in self.global_var_table.variables: 
                return True
            else: 
                return False
        else: 
            if scope in self.functions :
                if name in self.functions[scope].var_table.variables:
                    return True
            else: 
                return False

    def function_exsist(self, scope):
        if scope in self.functions :
            return True
        else: 
            return False

    def get_func_param(self, scope):
        if scope not in self.functions:
            raise Exception(f"Function '{scope}' not found.")
        
        var_table = self.functions[scope].var_table.variables
        params = [(name, var.tipo) for name, var in var_table.items() if var.is_param]
        return params

    def get_start_line(self, scope): 
        if scope not in self.functions:
            raise Exception(f"Function '{scope}' not found.")
        return self.functions[scope].start_quad


# Main structure holding state across parsing
class Estructura:
    def __init__(self):
        self.cubo = {
            ('int', 'int', '+'): 'int',
            ('int', 'int', '-'): 'int',
            ('int', 'int', '*'): 'int',
            ('int', 'int', '/'): 'int',
            ('int', 'int', '<'): 'bool',
            ('int', 'int', '>'): 'bool',
            ('int', 'int', '<='): 'bool',
            ('int', 'int', '>='): 'bool',
            ('int', 'int', '=='): 'bool',
            ('int', 'int', '!='): 'bool',

            ('float', 'float', '+'): 'float',
            ('float', 'float', '-'): 'float',
            ('float', 'float', '*'): 'float',
            ('float', 'float', '/'): 'float',
            ('float', 'float', '<'): 'bool',
            ('float', 'float', '>'): 'bool',
            ('float', 'float', '<='): 'bool',
            ('float', 'float', '>='): 'bool',
            ('float', 'float', '=='): 'bool',
            ('float', 'float', '!='): 'bool',

            ('int', 'float', '+'): 'float',
            ('int', 'float', '-'): 'float',
            ('int', 'float', '*'): 'float',
            ('int', 'float', '/'): 'float',
            ('int', 'float', '<'): 'bool',
            ('int', 'float', '>'): 'bool',
            ('int', 'float', '<='): 'bool',
            ('int', 'float', '>='): 'bool',
            ('int', 'float', '=='): 'bool',
            ('int', 'float', '!='): 'bool',

            ('float', 'int', '+'): 'float',
            ('float', 'int', '-'): 'float',
            ('float', 'int', '*'): 'float',
            ('float', 'int', '/'): 'float',
            ('float', 'int', '<'): 'bool',
            ('float', 'int', '>'): 'bool',
            ('float', 'int', '<='): 'bool',
            ('float', 'int', '>='): 'bool',
            ('float', 'int', '=='): 'bool',
            ('float', 'int', '!='): 'bool',
        }

        self.func_directory = FunctionDirectory()
        self.current_function = 'global'
        self.stack_operandos = []
        self.stack_tipos = []
        self.stack_scopes = ['global']
        self.stack_saltos = []
        self.cuadruplos = []
        self.semantic_errors = []
        self.counter_temporales = 0
        self.linea = 0

    def new_temp(self):
        self.counter_temporales += 1
        return f't{self.counter_temporales}'

estructura = Estructura()

def get_operand_and_type(operand):
    try:
        if operand[0] == 'factor':
            operand = operand[1][0] 
        elif operand[0] == 'varcte':
            id_tuple = operand[1][0][0] 
            if id_tuple == 'CTE_INT':
                return ['int', id_tuple[1]]
            elif id_tuple == 'CTE_FLOAT':
                return ['float', id_tuple[1]]

            var_name = operand[1][0][1]
            scope = estructura.current_function
            tipo = estructura.func_directory.get_variable_type(var_name, scope)
            if tipo is None:
                estructura.semantic_errors.append(f"Error semántico: Variable '{var_name}' no declarada.")
                return [None, var_name]
            return [tipo, var_name]

        elif operand[0].startswith('t'):  # temporal
            return [operand[1], operand[0]]
    except Exception as e:
        print(f"Error extrayendo tipo de operando: {operand}")
        raise e

def print_quadruples():
    print("\nCuádruplos generados:\n")
    print(f"{'No.':<4} {'Operador':<10} {'Arg1':<12} {'Arg2':<12} {'Resultado':<12} {'Tipo de Resultado'}")
    print("-" * 66)
    
    for quad in estructura.cuadruplos:
        if len(quad)==6:
            num, op, arg1, arg2, res, type = quad
        elif len(quad) ==5: 
            num, op, arg1, arg2, res = quad
            type = "-"
        
        print(f"{num:<4} {op:<10} {str(arg1):<12} {str(arg2):<12} {str(res):<12} {type}")

def print_symbol_table():
    print("\nTabla de símbolos globales:")
    print(f"{'Variable':<10} {'Tipo':<10}")
    for name, var in estructura.func_directory.global_var_table.variables.items():
        print(f"{name:<10} {var.tipo:<10}")

    print("\nVariables por función:")
    for func_name, func in estructura.func_directory.functions.items():
        print(f"\nFunción: {func_name}")
        for name, var in func.var_table.variables.items():
            print(f"  {name:<10} {var.tipo:<10}")