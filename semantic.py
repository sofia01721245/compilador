class Variable:
    def __init__(self, name, tipo, is_param, address=None):
        self.name = name
        self.tipo = tipo
        self.is_param = is_param
        self.address = address

class VarTable:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, tipo, is_param=False, address=None):
        if name in self.variables:
            raise Exception(f"Variable '{name}' already declared.")
        self.variables[name] = Variable(name, tipo, is_param, address)

    def get_type(self, name):
        if name in self.variables:
            return self.variables[name].tipo
        return None
    
    def get_address(self, name):
        if name in self.variables:
            return self.variables[name].address
        return None

class Function:
    def __init__(self, name, start_quad, return_type='void', address=None):
        self.name = name
        self.var_table = VarTable()
        self.start_quad = start_quad
        self.return_type = return_type
        self.param_count = 0
        self.local_var_count = 0
        self.address = address  

class MemoryManager:
    def __init__(self):
        # Memory address ranges
        self.MEMORY_RANGES = {
            'global_int': (1000, 1999),
            'global_float': (2000, 2999),
            'global_str': (3000, 3999),
            'global_void': (4000, 6999),
            'local_int': (7000, 7999),
            'local_float': (8000, 8999),
            'local_str': (9000, 11999),
            'temp_int': (12000, 12999),
            'temp_float': (13000, 13999),
            'temp_bool': (14000, 16999),
            'cte_int': (17000, 17999),
            'cte_float': (18000, 18999),
            'cte_str': (19000, 19999)
        }
        
        # Current allocation counters
        self.counters = {
            'global_int': 1000,
            'global_float': 2000,
            'global_str': 3000,
            'global_void': 4000,        # Count of void functions (not addresses)
            'local_int': 7000,
            'local_float': 8000,
            'local_str': 9000,
            'temp_int': 12000,
            'temp_float': 13000,
            'temp_bool': 14000,
            'cte_int': 17000,
            'cte_float': 18000,
            'cte_str': 19000
        }
        
        # Constants table
        self.constants = {}
    
    def get_memory_type(self, var_type, scope):
        """Determine memory category based on variable type and scope"""
        if scope == 'global':
            if var_type == 'int':
                return 'global_int'
            elif var_type == 'float':
                return 'global_float'
            elif var_type == 'string':
                return 'global_str'
        else:  # local scope
            if var_type == 'int':
                return 'local_int'
            elif var_type == 'float':
                return 'local_float'
            elif var_type == 'string':
                return 'local_str'
        return None
    
    def allocate_variable(self, var_type, scope):
        """Allocate memory address for a variable"""
        memory_type = self.get_memory_type(var_type, scope)
        if memory_type and memory_type in self.counters:
            address = self.counters[memory_type]
            self.counters[memory_type] += 1
            return address
        return None
    
    def allocate_temp(self, result_type):
        """Allocate temporary variable"""
        if result_type == 'int':
            memory_type = 'temp_int'
        elif result_type == 'float':
            memory_type = 'temp_float'
        elif result_type == 'bool':
            memory_type = 'temp_bool'
        else:
            memory_type = 'temp_int'  # default
            
        address = self.counters[memory_type]
        self.counters[memory_type] += 1
        return address
    
    def get_constant_address(self, value, value_type):
        """Get or create address for constant"""
        const_key = str(value)
        if const_key in self.constants:
            return self.constants[const_key]
        
        if value_type == 'int':
            memory_type = 'cte_int'
        elif value_type == 'float':
            memory_type = 'cte_float'
        elif value_type == 'string':
            memory_type = 'cte_str'
        else:
            memory_type = 'cte_int'
            
        address = self.counters[memory_type]
        self.counters[memory_type] += 1
        self.constants[const_key] = address
        return address
    
    def allocate_function(self):
        address = self.counters['global_void']
        self.counters['global_void'] += 1
        return address

class FunctionDirectory:
    def __init__(self):
        self.functions = {}
        self.global_var_table = VarTable()
        self.memory_manager = MemoryManager()

    def add_function(self, name, start_quad):
        if name in self.functions:
            raise Exception(f"Function '{name}' already declared.")
        
        func_address = self.memory_manager.allocate_function()
        self.functions[name] = Function(name, start_quad, address=func_address)

    def add_variable(self, name, tipo, function_name, is_param):
        if function_name != "global" and function_name not in self.functions:
            raise Exception(f"Function '{function_name}' not declared.")

        # Allocate memory address
        address = self.memory_manager.allocate_variable(tipo, 'global' if function_name == 'global' else 'local')

        if function_name == "global":
            if name in self.global_var_table.variables:
                raise Exception(f"Variable '{name}' already declared in global scope.")
            self.global_var_table.add_variable(name, tipo, is_param, address)
        else:
            func = self.functions[function_name]
            if name in func.var_table.variables:
                raise Exception(f"Variable '{name}' already declared in function '{function_name}'.")
            func.var_table.add_variable(name, tipo, is_param, address)
            
            if is_param:
                func.param_count += 1
            else:
                func.local_var_count += 1

    def get_variable_type(self, name, scope):
        if scope != "global":
            if scope in self.functions:
                tipo = self.functions[scope].var_table.get_type(name)
                if tipo:
                    return tipo
        return self.global_var_table.get_type(name)
    
    def get_variable_address(self, name, scope):
        if scope != "global":
            if scope in self.functions:
                address = self.functions[scope].var_table.get_address(name)
                if address:
                    return address
        return self.global_var_table.get_address(name)

    def has_variable(self, scope, name):
        if scope == 'global':
            return name in self.global_var_table.variables
        else:
            if scope in self.functions:
                return name in self.functions[scope].var_table.variables
            return False

    def function_exsist(self, scope):
        return scope in self.functions

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
            ('int', 'int', '/'): 'float',    # ← Division always produces float
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

            # Mixed type operations (float + int = float)
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
        self.call_stack = []  # For function call management
        self.cuadruplos = []
        self.semantic_errors = []
        self.counter_temporales = 0
        self.linea = 0
        self.main_start_line = 0

    def new_temp(self, result_type='int'):
        self.counter_temporales += 1
        temp_name = f't{self.counter_temporales}'
        address = self.func_directory.memory_manager.allocate_temp(result_type)
        return temp_name, address
    
    def get_operand_address(self, operand):
        if isinstance(operand, str):
            if operand.startswith('t'):  # temporary variable
                # For temp variables, we'll use the temp name as identifier
                # The VM will handle address mapping
                return operand
            else:  # regular variable
                address = self.func_directory.get_variable_address(operand, self.current_function)
                return address if address else operand
        else:  # constant value
            # Determine constant type
            if isinstance(operand, int):
                const_type = 'int'
            elif isinstance(operand, float):
                const_type = 'float'
            else:
                const_type = 'string'
            
            address = self.func_directory.memory_manager.get_constant_address(operand, const_type)
            return address

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
    print(f"{'No.':<4} {'Operador':<10} {'Arg1':<12} {'Arg2':<12} {'Resultado':<12}")
    print("-" * 60)
    
    for quad in estructura.cuadruplos:
        if len(quad) >= 5:
            num, op, arg1, arg2, res = quad[:5]
            print(f"{num:<4} {op:<10} {str(arg1):<12} {str(arg2):<12} {str(res):<12}")

def print_symbol_table():
    print("\nTabla de símbolos globales:")
    print(f"{'Variable':<10} {'Tipo':<10} {'Dirección':<10}")
    for name, var in estructura.func_directory.global_var_table.variables.items():
        print(f"{name:<10} {var.tipo:<10} {var.address:<10}")

    print("\nVariables por función:")
    for func_name, func in estructura.func_directory.functions.items():
        print(f"\nFunción: {func_name}")
        print(f"{'Variable':<10} {'Tipo':<10} {'Param':<6} {'Dirección':<10}")
        for name, var in func.var_table.variables.items():
            param_str = "Sí" if var.is_param else "No"
            print(f"  {name:<10} {var.tipo:<10} {param_str:<6} {var.address:<10}")
    
    print("\nConstantes:")
    print(f"{'Valor':<15} {'Dirección':<10}")
    for const_val, address in estructura.func_directory.memory_manager.constants.items():
        print(f"{const_val:<15} {address:<10}")

def print_function_table():
    print("\n=== Tabla de funciones===")
    print(f"{'Función':<15} {'Registro':<10} {'Parámetros':<12} {'Locales':<30}")
    print("-" * 80)
    
    for func_name, func in estructura.func_directory.functions.items():
        # Count parameters by type
        param_counts = {'int': 0, 'float': 0, 'string': 0}
        local_counts = {'int': 0, 'float': 0, 'string': 0}
        
        for var_name, var in func.var_table.variables.items():
            if var.is_param:
                param_counts[var.tipo] += 1
            else:
                local_counts[var.tipo] += 1
        
        # Format parameter info
        params_str = f"{sum(param_counts.values())} total"
        if any(param_counts.values()):
            param_details = []
            for tipo, count in param_counts.items():
                if count > 0:
                    param_details.append(f"{count} {tipo}")
            params_str += f" ({', '.join(param_details)})"
        
        # Format local variables info
        locals_str = f"{sum(local_counts.values())} total"
        if any(local_counts.values()):
            local_details = []
            for tipo, count in local_counts.items():
                if count > 0:
                    local_details.append(f"{count} {tipo}")
            locals_str += f" ({', '.join(local_details)})"
        
        print(f"{func_name:<15} {func.start_quad:<10} {params_str:<12} {locals_str:<30}")

def print_function_memory_layout():
    print("\n=== Memoria por funcion ===")
    
    for func_name, func in estructura.func_directory.functions.items():
        print(f"\nFunción: {func_name}")
        print(f"Registro de inicio: {func.start_quad}")
        
        # Separate parameters and locals
        parameters = []
        locals_vars = []
        
        for var_name, var in func.var_table.variables.items():
            var_info = f"{var_name} ({var.tipo}) @ {var.address}"
            if var.is_param:
                parameters.append(var_info)
            else:
                locals_vars.append(var_info)
        
        if parameters:
            print("  Parámetros:")
            for param in parameters:
                print(f"    {param}")
        
        if locals_vars:
            print("  Variables locales:")
            for local_var in locals_vars:
                print(f"    {local_var}")
        
        # Count by type for summary
        param_counts = {'int': 0, 'float': 0, 'string': 0}
        local_counts = {'int': 0, 'float': 0, 'string': 0}
        
        for var_name, var in func.var_table.variables.items():
            if var.is_param:
                param_counts[var.tipo] += 1
            else:
                local_counts[var.tipo] += 1
        
        print(f"  Resumen: {sum(param_counts.values())} parámetros, {sum(local_counts.values())} locales")
        
        # Memory requirements
        total_params = sum(param_counts.values())
        total_locals = sum(local_counts.values())
        print(f"  Memoria requerida: {total_params + total_locals} variables")

def generate_function_data():
    print("\n-------------- Datos de Functiones ------")
    
    for func_name, func in estructura.func_directory.functions.items():
        print(f"\nFuncion g_void ({func_name}), en el registro {func.address}")  # ← Use function's memory address
        
        # Count parameters and locals by type
        param_counts = {'int': 0, 'float': 0, 'string': 0}
        local_counts = {'int': 0, 'float': 0, 'string': 0}
        param_names = []
        local_names = []
        
        for var_name, var in func.var_table.variables.items():
            if var.is_param:
                param_counts[var.tipo] += 1
                param_names.append(f"{var_name} ({var.tipo})")
            else:
                local_counts[var.tipo] += 1
                local_names.append(f"{var_name} ({var.tipo})")
        
        # Show parameters
        total_params = sum(param_counts.values())
        print(f"{total_params} parámetros ({', '.join(param_names)})")
        
        # Show locals by type
        print(f"Locales:")
        for tipo in ['int', 'float', 'string']:
            if local_counts[tipo] > 0:
                tipo_locals = [name for name in local_names if f'({tipo})' in name]
                print(f"  - {local_counts[tipo]} {tipo}: {', '.join([name.split(' (')[0] for name in tipo_locals])}")
        
        # Memory layout
        print(f"Código inicia en quad: {func.start_quad}")
        print(f"Dirección de función: {func.address}")
        print(f"Memoria de : {total_params + sum(local_counts.values())} variables")

def print_memory_allocation():
    print("\nAsignación de memoria:")
    mm = estructura.func_directory.memory_manager
    for mem_type, counter in mm.counters.items():
        start_addr = mm.MEMORY_RANGES[mem_type][0]
        used = counter - start_addr
        if used > 0:
            print(f"{mem_type}: {used} variables (direcciones {start_addr}-{counter-1})")