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
# ---------------- PARSER ---------------- 
def p_programa(p):
    'Programa : KEYWORD_PROGRAM ID SEMICOLON vars_opt funcs_opt KEYWORD_MAIN body KEYWORD_END SEMICOLON'
    p[0] = ('Programa', [p[2], p[4], p[5], p[7], 'end', ';'])

def p_vars_opt(p):
    '''vars_opt : vars_opt VARS
                | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]  # Acumula la lista de VARS
    else:
        p[0] = []  # empty -> lista vacía

def p_VARS(p):
    'VARS : KEYWORD_VAR var_list SEMICOLON'
    p[0] = ('VARS', p[2])

def p_var_list(p):
    '''  : ID id_list COLON type'''
    hijos = [('ID', p[1])] + p[2:4]
    p[0] = hijos

def p_id_list(p):
    '''id_list : COMMA ID id_list
               | empty'''
    if len(p) == 4:
        p[0] = [('ID', p[2])] + p[3]
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
    p[0] = ('assign', [('ID', p[1]), p[3]])

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
    p[0] = ('cycle', [p[2], p[5]])

def p_condition(p):
    'condition : KEYWORD_IF LPAREN expresion RPAREN body else_opt SEMICOLON'
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
        p[0] = ('expresion', [p[1], p[2], p[3]])
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
        p[0] = ('exp', [p[1], p[2], p[3]])
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino OP_MUL factor
               | termino OP_DIV factor
               | factor'''
    if len(p) == 4:
        p[0] = ('termino', [p[1], p[2], p[3]])
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
    p[0] = ('varcte', [(p.slice[1].type, p[1])])

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
program mayor_numero;

var x, y, z, mayor : int;

main {
    x = 10;
    y = 25;
    z = 15;

    if(x > y) {
        if (x > z) {
            mayor = x;
        } else {
            mayor = z;
        };
    } else {
        if (y > z) {
            mayor = y;
        } else {
            mayor = z;
        };
    };
    print(mayor);
}
end;
"""

with open("fibonacci.ld", "w") as f:
    f.write(input_text)

# Leer el archivold 
with open("fibonacci.ld", "r") as f:
    test_code = f.read()

# ----------------LEXER------------------
tokenizer = PlyTokenizer()

# --------------PARSER-------------------
parser = yacc.yacc(debug=True)

syntax_errors = []

parse_tree = parser.parse(test_code, lexer=tokenizer.lexer)
print("\n--- PARSE TREE ---")
print_tree(parse_tree)

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
