# Importamos librerias necesarias
import re
import ply.lex as lex


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