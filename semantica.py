# Importamos librerias necesarias
import re
import ply.lex as lex
import ply.yacc as yacc

# palabras reservadas
keywords = {
    'program': 'KEYWORD_PROGRAM',
    'main': 'KEYWORD_MAIN',
    'var': 'KEYWORD_VAR',
    'int': 'KEYWORD_INT',
    'float': 'KEYWORD_FLOAT',
    'void': 'KEYWORD_VOID',
    'if': 'KEYWORD_IF',
    'else': 'KEYWORD_ELSE',
    'while': 'KEYWORD_WHILE',
    'do': 'KEYWORD_DO',
    'print': 'KEYWORD_PRINT',
    'end': 'KEYWORD_END',
    'string': 'KEYWORD_STRING',
}

# Lista de todos los tipos de tokens
tokens = list(keywords.values()) + [
    'ID', 'CTE_INT', 'CTE_FLOAT', 'CTE_STRING', 'OP_SUM', 'OP_SUB', 'OP_MUL', 'OP_DIV',
    'ASSIGN_SIGN', 'EQUAL', 'NOT_EQUAL', 'GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL',
    'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET', 'COLON'
    #OP_MOD
]

# Se define clase Lexer
class PlyTokenizer:
    def __init__(self):
        # Tabla de símbolos para guardar identificadores y las líneas en un diccionario
        self.symbol_table = {}
        # Guarda todos los tokens encontrados por linea
        self.tokens_by_line = []
        # Guarda errores lexicos
        self.errors = []
        #guardar lineas formateadas para parser
        self.formatted_lines = []
        self.keywords = keywords
        self.tokens = tokens

        self.lexer = lex.lex(module=self)

        
#----------------------FUNCIONES LEXER -----------------
    # Regex de Tokens Literales
    t_OP_SUM = r'\+'
    t_OP_SUB = r'-'
    t_OP_MUL = r'\*'
    t_OP_DIV = r'/'
    #t_OP_MOD = r'%'
    t_ASSIGN_SIGN= r'='
    t_EQUAL = r'=='
    t_NOT_EQUAL = r'!='
    t_GREATER = r'>'
    t_GREATER_EQUAL = r'>='
    t_LESS_EQUAL = r'<='  
    t_LESS = r'<'
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COLON = r':'

    # Ignorar espacios, comentarios y tabulares
    t_ignore = ' \t'
    t_ignore_COMMENT = r'\#.*'

    # Tokens con procesamiento especial: 
    # Constante tipo flotante
    def t_CTE_FLOAT(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    # Constante tipo entero
    def t_CTE_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Constante tipo string
    def t_CTE_STRING(self, t):
        r'\".*?\"'
        t.value = t.value[1:-1] #quitar comillas
        return t

    # Identificadores
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.keywords:
            t.type = self.keywords[t.value]  # Si es palabra clave cambiar tipo
        else:
            if t.value not in self.symbol_table: #si no se ha encontrado antes
                self.symbol_table[t.value] = {'lines': [t.lineno]}
            else:
                self.symbol_table[t.value]['lines'].append(t.lineno)
        return t

    # Actualizar el número de línea en cambio de linea
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Manejo de errores léxicos
    def t_error(self, t):
        error_substring = t.value[0]
        self.errors.append((t.lineno, t.lexpos, error_substring))
        t.lexer.skip(1)   

    # Función para tokenizar el contenido de un archivo
    def tokenize_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line_number, line in enumerate(lines, 1):
            self.lexer.input(line)
            line_tokens = []
            formatted_tokens = []

            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                line_tokens.append((tok.type, tok.value, tok.lexpos))
                formatted_tokens.append([tok.type, tok.value])

            self.tokens_by_line.append((line_number, line.rstrip(), line_tokens))
            self.formatted_lines.append(formatted_tokens)

    #getter para informacion dentro del constructor
    def get_formatted_lines(self):
        return self.formatted_lines

#--------------------------END LEXER------------------------

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

        self.counter_temporales = 0
        self.symbol_table = {}  # variable name -> type
        self.linea = 0
        self.cuadruplos = []
        self.stack_saltos = [] 
        self.semantic_errors = []

    def new_temp(self):
        self.counter_temporales += 1
        return f't{self.counter_temporales}'

estructura = Estructura()



def get_operand_and_type(operand):
    """
    Extracts the variable name from the operand and returns its type using the symbol table.
    Supports nested tuples like:
    ('factor', [('varcte', [('ID', 'A')])])
    """
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


# ---------------- PARSER ---------------- 
def p_programa(p):
    'Programa : KEYWORD_PROGRAM ID SEMICOLON vars_opt funcs_opt KEYWORD_MAIN body KEYWORD_END SEMICOLON'
    p[0] = ('Programa', [p[2], p[4], p[5], p[7], 'end', ';'])

def p_vars_opt(p):
    '''vars_opt : vars_opt VARS
                | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_VARS(p):
    'VARS : KEYWORD_VAR var_list SEMICOLON'
    ids = p[2][1]['ids']
    var_type = p[2][1]['type'][1][0]
    
    for var_id in ids:
        if var_id in estructura.symbol_table:
            print(f"Error de semantica: Variable '{var_id}' ya declarada.")
        else:
            estructura.symbol_table[var_id] = var_type
    
    p[0] = ('VARS', p[2])


def p_var_list(p):
    '''var_list : ID id_list COLON type'''
    ids = [p[1]] + p[2]  # Include the first ID
    p[0] = ('var_list', {'ids': ids, 'type': p[4]})

def p_id_list(p):
    '''id_list : COMMA ID id_list
               | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_type(p):
    '''type : KEYWORD_INT
            | KEYWORD_FLOAT
            | KEYWORD_STRING'''
    p[0] = ('type', [p[1]])

def p_funcs_opt(p):
    '''funcs_opt : FUNCS
                 | empty'''
    p[0] = ('funcs_opt', [p[1]])

def p_FUNCS(p):
    'FUNCS : KEYWORD_VOID ID LPAREN parametros_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOLON'
    p[0] = ('FUNCS', [p[2], p[4], p[7], p[8]])

def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | empty'''
    p[0] = ('parametros_opt', [p[1]])

def p_parametros(p):
    '''parametros : ID COLON type param_list'''
    p[0] = ('parametros', [('ID', p[1]), p[3]] + p[4])

def p_param_list(p):
    '''param_list : COMMA ID COLON type param_list
                  | empty'''
    if len(p) == 6:
        p[0] = [('ID', p[2]), p[4]] + p[5]
    else:
        p[0] = []

def p_body(p):
    'body : LBRACE statement_list RBRACE'
    p[0] = ('body', [p[2]])

def p_statement_list(p):
    '''statement_list : statement_list statement
                       | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : assign
                 | condition
                 | cycle
                 | f_call
                 | print'''
    p[0] = ('statement', [p[1]])

def p_assign(p):
    'assign : ID ASSIGN_SIGN expresion SEMICOLON'
    valor, tipo = estructura.stack_operandos.pop()

    var_name = p[1]
    if var_name not in estructura.symbol_table:
        estructura.semantic_errors.append(f"Error de semantica: Variable '{var_name}' no declarada.")
        return

    #Checar compatibilidad tipo
    tipo_variable = estructura.symbol_table[var_name]
    if tipo != tipo_variable:
        estructura.semantic_errors.append(f"Error de Mismatch: No se puede asignar tipo {tipo} a variable '{var_name}' de tipo {tipo_variable}.")
        return
    
    #añadir a cuadruplos y stack
    estructura.cuadruplos.append((len(estructura.cuadruplos)+1, '=', valor, None, var_name))
    estructura.stack_operandos.append((var_name, tipo_variable))

    p[0] = ('assign', [('ID', var_name), p[3]])

def p_print(p):
    'print : KEYWORD_PRINT LPAREN print_items RPAREN SEMICOLON'
    p[0] = ('print', [p[3]])

def p_print_items(p):
    '''print_items : print_items COMMA print_item
                   | print_item'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_print_item(p):
    '''print_item : expresion
                  | CTE_STRING'''
    if isinstance(p[1], tuple):
        p[0] = ('print_item', [p[1]])
    else:
        p[0] = ('print_item', [('CTE_STRING', p[1])])

def p_cycle(p):
    'cycle : KEYWORD_DO body KEYWORD_WHILE LPAREN expresion RPAREN SEMICOLON'
    start_line = estructura.linea + 1
    tipo, valor = get_operand_and_type(p[5])
    if tipo != 'bool':
        estructura.semantic_errors.append(f"La condición del ciclo debe ser booleana en línea {start_line}")

    # Genera GOTOT (si la condición es verdadera, repite)
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOT', valor, None, start_line))

    p[0] = ('cycle', [p[2], p[5]])
    p[0] = ('cycle', [p[2], p[5]])

def p_condition(p):
    'condition : KEYWORD_IF LPAREN expresion RPAREN body else_opt SEMICOLON'
    tipo, valor = get_operand_and_type(p[3])
    if tipo != 'bool':
        estructura.semantic_errors.append(f"La condición del if debe ser booleana en línea {estructura.linea}")

    # Salta if si falso
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOF', valor, None, '-'))
    estructura.stack_saltos.append(estructura.linea)

    if p[6][0] == 'else':
        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, 'GOTO', None, None, '-'))
        falso = estructura.stack_saltos.pop()
        estructura.stack_saltos.append(estructura.linea)  # nuevo salto pendiente (al final)
        
        # Rellenar GOTOF con la línea del bloque else
        estructura.cuadruplos[falso - 1] = (falso, 'GOTOF', valor, None, estructura.linea + 1)
        
        fin = estructura.stack_saltos.pop()
        estructura.cuadruplos[fin - 1] = (fin, 'GOTO', None, None, estructura.linea + 1)
    else:
        falso = estructura.stack_saltos.pop()
        estructura.cuadruplos[falso - 1] = (falso, 'GOTOF', valor, None, estructura.linea + 1)

    p[0] = ('condition', [p[3], p[5], p[6]])

def p_else_opt(p):
    '''else_opt : KEYWORD_ELSE body
                | empty'''
    if len(p) == 3:
        p[0] = ('else', [p[2]])
    else:
        p[0] = ('else', [])

def p_f_call(p):
    'f_call : ID LPAREN expresion_list_opt RPAREN SEMICOLON'
    p[0] = ('f_call', [('ID', p[1]), p[3]])

def p_expresion_list_opt(p):
    '''expresion_list_opt : expresion_list
                          | empty'''
    p[0] = ('expresion_list_opt', p[1] if isinstance(p[1], list) else [])

def p_expresion_list(p):
    '''expresion_list : expresion_list COMMA expresion
                      | expresion'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expresion(p):
    '''expresion : exp comparador exp
                 | exp'''
    if len(p) == 4:
        left = p[1]
        op = p[2][1][0]  # p[2] = ('comparador', [<operator>])
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)

        if tipo1 is None or tipo2 is None:
         estructura.cuadruplos.append(f"Unknown tipos: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.cuadruplos.append(f"No se puede hacer operación de comparación {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, value1, value2, temp_var))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]

def p_comparador(p):
    '''comparador : LESS
                  | GREATER
                  | NOT_EQUAL
                  | EQUAL
                  | GREATER_EQUAL
                  | LESS_EQUAL'''
    p[0] = ('comparador', [p[1]])

def p_exp(p):
    '''exp : exp OP_SUM termino
           | exp OP_SUB termino
           | termino'''
    if len(p) == 4:
        left = p[1]
        op = p[2]
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)
        if tipo1 is None or tipo2 is None:
            estructura.cuadruplos.append(f"Unknown operand types: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.cuadruplos.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea,op,value1,value2,temp_var))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino OP_MUL factor
               | termino OP_DIV factor
               | factor'''
    if len(p) == 4:
        left = p[1]
        op = p[2]
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)
        if tipo1 is None or tipo2 is None:
            estructura.cuadruplos.append(f"Unknown types: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.cuadruplos.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, value1, value2, temp_var))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]


def p_factor(p):
    '''factor : LPAREN expresion RPAREN
              | OP_SUM varcte
              | OP_SUB varcte
              | varcte'''
    if len(p) == 4:
        p[0] = ('factor', [p[2]])
    elif len(p) == 3:
        p[0] = ('factor', [p[1], p[2]])
    else:
        p[0] = ('factor', [p[1]])

def p_varcte(p):
    '''varcte : ID
              | CTE_INT
              | CTE_FLOAT'''
    if p.slice[1].type == 'ID':
        p[0] = ('varcte', [('ID', p[1])])

        # Para semántica, el tipo se consulta en la tabla de símbolos
    elif p.slice[1].type == 'CTE_INT':
        estructura.stack_operandos.append([p[1], 'int'])
        p[0] = ('varcte', [('CTE_INT', p[1])])
    elif p.slice[1].type == 'CTE_FLOAT':
        estructura.stack_operandos.append([p[1], 'float'])
        p[0] = ('varcte', [('CTE_FLOAT', p[1])])

#agregar cte int y float separado
'''def p_CTE_INT(p): 
    'CTE: CTE_INT'
    estructura.stack_operandos.append([p[1],'int'])

def p_CTE_FLOAT(p): 
    'CTE: CTE_FLOAT'
    estructura.stack_operandos.append([p[1],'float'])
'''

def p_empty(p):
    'empty :'
    p[0] = ('empty', [])

def p_error(p):
    if p:
        # If the unexpected token is not a semicolon, maybe missing a semicolon before?
        msg = f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)

        # Skip tokens until next semicolon or EOF to try to recover
        while True:
            tok = parser.token()
            if not tok or tok.type == 'SEMICOLON':
                break
        parser.errok()
    else:
        syntax_errors.append("Error de sintaxis: fin de archivo inesperado")

def print_tree(node, indent="", last=True):
    branch = "└── " if last else "├── "
    
    # Si es un terminal 
    if isinstance(node, (str, int, float)):
        print(indent + branch + str(node))
        return
    
    # Si es un no terminal
    if isinstance(node, tuple):
        label, children = node
        print(indent + branch + str(label))
        indent += "    " if last else "│   "
        if isinstance(children, list):
            for i, child in enumerate(children):
                print_tree(child, indent, i == len(children) - 1)
        else:
            print_tree(children, indent, True)
        return
    
    # Si es una lista
    if isinstance(node, list):
        for i, child in enumerate(node):
            print_tree(child, indent, i == len(node) - 1)
        return
    
    # Si llega algo inesperado, error
    print(indent + branch + f"<{type(node).__name__}> {node}")

#---------------------------------END PARSER---------------

# Crear archivo ld
input_text = """
program prueba3;

var A, B : int;

main {
    A = 3;
    B = 5;

    do {
        A = A + 1;
        B = B - 1;
    } while (A < B);

    do {
        A = A + 1;
    } while (A + B);
} end;

"""

with open("semantica.ld", "w") as f:
    f.write(input_text)

# Leer el archivold 
with open("semantica.ld", "r") as f:
    test_code = f.read()

# ----------------LEXER------------------
tokenizer = PlyTokenizer()

# --------------PARSER-------------------
parser = yacc.yacc(debug=True)

syntax_errors = []

parse_tree = parser.parse(test_code, lexer=tokenizer.lexer)
print("\n--- PARSE TREE ---")
print_tree(parse_tree)


print(estructura.stack_operandos)
print_quadruples()
print_symbol_table()

if tokenizer.errors:
    print("\n--- ERRORES DE LEXICO DETECTADOS ---")
    for err in tokenizer.errors:
        lineno, lexpos, char = err
        print(f"Lexer error: Unrecognized character '{char}' at line {lineno}, position {lexpos}")
else:
    print("\n---NO SE DETECTARON ERRORES LÉXICOS ---")


# Imprimir errores de sintaxis
if syntax_errors:
    print("\n--- ERRORES DE SINTAXIS DETECTADOS ---")
    for err in syntax_errors:
        print(err)
else:
    print("\n---NO SE DETECTARON ERRORES SINTÁCTICOS ---")

# Imprimir errores semánticos
if estructura.semantic_errors:
    print("\n--- ERRORES SEMÁNTICOS DETECTADOS ---")
    for err in estructura.semantic_errors:
        print(err)
else:
    print("\n---NO SE DETECTARON ERRORES SEMÁNTICOS ---")

