# Importamos librerias necesarias
import re
import ply.lex as lex
from collections import deque

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

        # palabras reservadas
        self.keywords = {
            'program': 'KEYWORD_PROGRAM',
            'Main': 'KEYWORD_MAIN',
            'var': 'KEYWORD_VAR',
            'int': 'KEYWORD_INT',
            'float': 'KEYWORD_FLOAT',
            'void': 'KEYWORD_VOID',
            'if': 'KEYWORD_IF',
            'else': 'KEYWORD_ELSE',
            'while': 'KEYWORD_WHILE',
            'do': 'KEYWORD_DO',
            'print': 'KEYWORD_PRINT',
            'end': 'KEYWORD_END'
        }

        # Lista de todos los tipos de tokens
        self.tokens = list(self.keywords.values()) + [
            'ID', 'CTE_INT', 'CTE_FLOAT', 'CTE_STRING', 'OP_SUM', 'OP_SUB', 'OP_MUL', 'OP_DIV', 'OP_MOD',
            'ASSIGN_SIGN', 'EQUAL', 'NOT_EQUAL', 'GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL',
            'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
            'LBRACKET', 'RBRACKET', 'COLON', 'COMMENT'
        ]

        self.lexer = lex.lex(module=self)

        
#----------------------FUNCIONES LEXER -----------------
    # Regex de Tokens Literales
    t_OP_SUM = r'\+'
    t_OP_SUB = r'-'
    t_OP_MUL = r'\*'
    t_OP_DIV = r'/'
    t_OP_MOD = r'%'
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
    
    # Imprime los tokens encontrados por linea
    def print_tokens(self):
        print("\n--- TOKEN STREAM POR LÍNEA ---")
        for line_num, code_line, tokens in self.tokens_by_line:
            print(f"\n{line_num:>3} | {code_line}")
            for tok_type, tok_value, tok_pos in tokens:
                print(f"      [{tok_pos:>2}] {tok_type:<15} --> {tok_value}")

    # Imprime la tabla de símbolos
    def print_symbol_table(self):
        print("\n--- TABLA DE SÍMBOLOS ---")
        for symbol, data in sorted(self.symbol_table.items()):
            print(f" {symbol:<15} -> líneas {data['lines']}")

    # Imprime los errores léxicos
    def print_errors(self):
        if self.errors:
            print("\n--- ERRORES LÉXICOS DETECTADOS ---")
            for line, pos, char in self.errors:
                print(f" Línea {line}, posición {pos}: Símbolo inválido '{char}'")
        else:
            print("\n--- NO SE DETECTARON ERRORES LÉXICOS ---")

#--------------------------END LEXER------------------------------------------------------------

#--------------------------FUNCIONES PARSER-------------------------------
parsing_table = {
    'ASSIGN': {
        'ID': ['ID', 'ASSIGN_SIGN', 'EXPRESION', 'SEMICOLON']
    },
    'EXPRESION': {
        'ID': ['EXP', 'OPCIONAL'],
        'CTE_INT': ['EXP', 'OPCIONAL'],
        'CTE_FLOAT': ['EXP', 'OPCIONAL'],
    },
    'OPCIONAL': {
        'LESS': ['OPREL', 'EXP'],
        'GREATER': ['OPREL', 'EXP'],
        'NOT_EQUAL': ['OPREL', 'EXP'],
        'EQUAL': ['OPREL', 'EXP'],
        'GREATER_EQUAL': ['OPREL', 'EXP'],
        'LESS_EQUAL': ['OPREL', 'EXP'],
        'RPAREN': [],
        'SEMICOLON': [],
    },
    'OPREL': {
        'LESS': ['LESS'],
        'GREATER': ['GREATER'],
        'NOT_EQUAL': ['NOT_EQUAL'],
        'EQUAL': ['EQUAL'],
        'GREATER_EQUAL': ['GREATER_EQUAL'],
        'LESS_EQUAL': ['LESS_EQUAL']
    },
    'EXP': {
        'ID': ['TERMINO', 'MASMENOS'],
        'CTE_INT': ['TERMINO', 'MASMENOS'],
        'CTE_FLOAT': ['TERMINO', 'MASMENOS'],
    },
    'MASMENOS': {
        'OP_SUM': ['OP_SUM', 'EXP'],
        'OP_SUB': ['OP_SUB', 'EXP'],
        'RPAREN': [],
        'SEMICOLON': [],
        'NOT_EQUAL': [],
        'EQUAL': [],
        'GREATER': [],
        'LESS': [],
        'GREATER_EQUAL': [],
        'LESS_EQUAL': [],
    },
    'TERMINO': {
        'ID': ['FACTOR', 'PORDIV'],
        'CTE_INT': ['FACTOR', 'PORDIV'],
        'CTE_FLOAT': ['FACTOR', 'PORDIV'],
    },
    'PORDIV': {
        'OP_MUL': ['OP_MUL', 'TERMINO'],
        'OP_DIV': ['OP_DIV', 'TERMINO'],
        'OP_SUM': [],
        'OP_SUB': [],
        'RPAREN': [],
        'SEMICOLON': [],
        'NOT_EQUAL': [],
        'EQUAL': [],
        'GREATER': [],
        'LESS': [],
        'GREATER_EQUAL': [],
        'LESS_EQUAL': [],
    },
    'FACTOR': {
        'ID': ['ID'],
        'CTE_INT': ['CTE_INT'],
        'CTE_FLOAT': ['CTE_FLOAT'],
    },
}

terminals = ['ID', 'ASSIGN_SIGN', 'CTE_FLOAT', 'CTE_INT', 'OP_SUM', 'OP_MUL', 'OP_DIV', 'OP_SUB', 'GREATER', 'LESS_EQUAL', 'EQUAL', 'NOT_EQUAL', 'SEMICOLON', '$']

def parse_tokens(tokens):
    stack = deque()
    stack.append('$') 
    stack.append('ASSIGN') #Después se tendrá que identificar con primer variable del lexer
    index = 0

    if not tokens:
        return True

    tokens.append(('$', '$'))

    while stack:
        top = stack.pop()
        current_token = tokens[index] if index < len(tokens) else ('$','')

        token_type, token_value = current_token

        #si es terminal no la tenemos que desplegar más
        if top in terminals:
            if top == token_type:
                index += 1
            else:
                print(f"Se esperaba'{top}' pero es '{token_type}'")
                return False

        #End of input
        elif top == '$':
            if token_type == '$':
                return True
            else:
                return False

        # No terminales se sacan de tabla de parse
        elif top in parsing_table:
            production = parsing_table[top].get(token_type)

            if not production:
                if token_type == 'ID':
                    production = parsing_table[top].get('ID') 
                elif token_type == 'CTE_FLOAT':
                    production = parsing_table[top].get('CTE_FLOAT') 
                elif token_type == 'CTE_INT':
                    production = parsing_table[top].get('CTE_INT')

            if production is None:
                print(f"No exsiste '{top}' en tabla de parsers")
                return False

            # Agregard componentes de nueva gramatica
            for symbol in reversed(production):
                if symbol != '':
                    stack.append(symbol)
        else:
            print(f"No se reconoce: '{top}'")
            return False

    #Si quedan tokens despues de EOF 
    if index < len(tokens) and tokens[index][0] != '$':
        print(f"Tokens que quedan después de EOF: {tokens[index:]}") 
        return False

    return True
#---------------------------------END PARSER---------------

# Código de prueba
test_code = """
x = 10.5;
y = 3.14 * x + 2.0;
z = y / 2.0 - 1.0;

cond = x > y;
cond = y <= z + 1;
exp = y==x;
ex2 = z!=y;
"""

# Crear archivo .ld
with open("code.ld", "w") as f:
    f.write(test_code)

# ----------------LEXER------------------
tokenizer = PlyTokenizer()
tokenizer.tokenize_file("code.ld")
tokenizer.print_tokens()
tokenizer.print_symbol_table()
tokenizer.print_errors()

#--------------PARSER-------------------
lineas = tokenizer.get_formatted_lines()
print(lineas)

for linea in lineas:
    print("\n", linea)

    token_line = linea

    result = parse_tokens(token_line)
    if(result == True):
        print("OK")


