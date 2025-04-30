# Importamos librerias necesarias
import re
import ply.lex as lex

# Se define clase Lexer
class PlyTokenizer:

    def __init__(self):
        # Tabla de símbolos para guardar identificadores y las líneas en un diccionario
        self.symbol_table = {}
        # Guarda todos los tokens encontrados por linea
        self.tokens_by_line = []
        # Guarda errores lexicos
        self.errors = []

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
            'ASSIGN', 'EQUAL', 'NOT_EQUAL', 'GREATER', 'LESS',
            'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
            'LBRACKET', 'RBRACKET', 'COLON', 'COMMENT'
        ]

        self.lexer = lex.lex(module=self)

    # Regex de Tokens Literales
    t_OP_SUM = r'\+'
    t_OP_SUB = r'-'
    t_OP_MUL = r'\*'
    t_OP_DIV = r'/'
    t_OP_MOD = r'%'
    t_ASSIGN = r'='
    t_EQUAL = r'=='
    t_NOT_EQUAL = r'!='
    t_GREATER = r'>'
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
            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                line_tokens.append((tok.type, tok.value, tok.lexpos))
            self.tokens_by_line.append((line_number, line.rstrip(), line_tokens))

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


# Código de prueba
test_code = """
program mayor_numero;

var x, y, z, mayor : int;

Main {
    x = 10;
    y = 25;
    z = 15;

    if (x > y) {
        if (x > z) {
            mayor = x;
        } else {
            mayor = z;
        }
    } else {
        if (y > z) {
            mayor = y;
        } else {
            mayor = z;
        }
    }
    print(mayor)
}
end
"""

# Crear archivo .ld
with open("mayor.ld", "w") as f:
    f.write(test_code)


tokenizer = PlyTokenizer()
tokenizer.tokenize_file("mayor.ld")
tokenizer.print_tokens()
tokenizer.print_symbol_table()
tokenizer.print_errors()
