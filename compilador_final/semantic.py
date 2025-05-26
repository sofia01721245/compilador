
class Estructura:
    def __init__(self):
        self.stack_operandos = []
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

        self.func_directory = {
            'global': {
                'type': 'void',
                'vars': {},         # variables globales
                'params': [],
                'start_quad': 0
            }
        }
        self.current_function = 'global'
        self.current_scope = 'global'


        self.counter_temporales = 0
        self.symbol_table = {}  # variable name -> type
        self.linea = 0
        self.cuadruplos = []
        self.stack_saltos = [] 
        self.semantic_errors = []

        self.stack_tipos = []          # Tipos de los operandos
        self.stack_operadores = []     # Operadores para generar cuádruplos
        self.stack_dimensiones = []    # Para manejo de arreglos
        self.stack_llamadas = []       # Para llamadas a funciones
        self.stack_parametros = []     # Para validación de parámetros
        self.contador_cuadruplos = 0       # Para llevar el número actual de cuadruplo
        self.contador_variables = 0        # Para generar direcciones de variables
        self.contador_parametros = 0       # Parámetros por función
        self.func_dir = {}          # Directorio de funciones
        self.current_function = None
        self.local_var_table = {}   # Tabla de variables locales por función


    def new_temp(self):
        self.counter_temporales += 1
        return f't{self.counter_temporales}'

estructura = Estructura()



def get_operand_and_type(operand):
    try:
        if operand[0] == 'factor':
            varcte = operand[1][0] 
            if varcte[0] == 'varcte':
                id_tuple = varcte[1][0][0] 
                if id_tuple == 'CTE_INT':
                    return ['int', id_tuple[1]]
                elif id_tuple == 'CTE_FLOAT':
                    return ['float', id_tuple[1]]

                var_name = varcte[1][0][1]
                if var_name not in estructura.symbol_table:
                    estructura.semantic_errors.append(f"Error de semántica: Variable '{var_name}' no declarada.")
                    return [None, var_name]
                return [estructura.symbol_table.get(var_name), var_name]
        
        elif operand[0].startswith('t'):  # Temporary variable
            return [operand[1], operand[0]] 
    except Exception as e:
        print(f"Failed to extract type from operand: {operand}")
        raise e

def print_quadruples():
    print("\nCuádruplos generados:\n")
    print(f"{'No.':<4} {'Operador':<10} {'Arg1':<12} {'Arg2':<12} {'Resultado':<12} {'Tipo de Resultado'}")
    print("-" * 66)
    
    for quad in estructura.cuadruplos:
        num, op, arg1, arg2, res = quad

        tipo_res = next((t for (v, t) in estructura.stack_operandos if v == res), '-')
        
        print(f"{num:<4} {op:<10} {str(arg1):<12} {str(arg2):<12} {str(res):<12} {tipo_res}")

def print_symbol_table():
    print("\nTabla de símbolos:")
    print(f"{'Variable':<10} {'Tipo':<10}")
    for name, tipo in estructura.symbol_table.items():
        print(f"{name:<10} {tipo:<10}")

