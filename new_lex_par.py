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
            'ASSIGN', 'EQUAL', 'NOT_EQUAL', 'GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL',
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
    t_ASSIGN = r'='
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

# Se define clase Tokens
class Tokens:
  # Atributos
  tokens = []       # una lista de tokens
  pos = 0           # un indice para el token actual

  # Constructor de la clase...
  def __init__(self, lista):
    self.tokens = lista
    self.pos = 0

  # Devuelve el token actual
  def current(self):
    return self.tokens[self.pos]

  # Consume un token, avanzando al siguiente
  def avanza(self):
    if self.pos < len(self.tokens) - 1:
        self.pos += 1
    return self.tokens[self.pos]


# Guarda errores en una lista
def addError(errors, expected, token, index):
  #print(  f"ERROR index {index}: esperaba {expected}, recibio {token}"  )
  errors.append( f"ERROR en index {index}: esperaba {expected}, recibio {token}"  )

# F ->  ( E ) | const_int | ID
def factor(tokens, errors):
  # Obten el token actual
  if len(tokens.tokens) == 0:
    return
    
  token, content = tokens.current()  # <------ el tipo de token, y el valor  ej. 'const_int', 14

  if token == "LPAREN":
      # Si es un '('
      tokens.avanza()
      expr(tokens, errors)
      token, content = tokens.current()
      if token == "RPAREN":
          tokens.avanza()
      else:
          addError(errors, ")", content, tokens.pos)
  elif token == "CTE_INT" or token == "CTE_FLOAT":
      # Si es un número entero o flotante
      tokens.avanza()
  elif token == "ID":
      # Si es un identificador
      tokens.avanza()
  else:
      addError(errors, "( o CTE_INT o ID", content, tokens.pos)



# T' -> * F T' | epsilon
def termino_prime(tokens, errors):

  if(len(tokens.tokens) == 0):
        return
    
  # Obten el token actual
  token, content = tokens.current()

  # Si el token actual es un '*'
  if token == "OP_MUL" or token == "OP_DIV":
    # Avanza al siguiente token
    token, content = tokens.avanza()
    # Llama a factor
    factor(tokens, errors)
    # Llama a termino_prime
    termino_prime(tokens, errors)
  #Se va por epsilon

# rel_expr -> E (rel_op E)?
def rel_expr(tokens, errors):
    expr(tokens, errors)
    
    if tokens.pos < len(tokens.tokens):
        if(len(tokens.tokens) == 0):
            return
        token, content = tokens.current()
        if token in ["GREATER", "LESS", "EQUAL", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL"]:
            tokens.avanza()
            expr(tokens, errors)

# ASSIGN -> ID = rel_expr ;
def assign(tokens, errors):
    if(len(tokens.tokens) == 0):
        return

    token, content = tokens.current()
    if token == "ID":
        tokens.avanza()
        token = tokens.current()
        if token[0] == "ASSIGN":
            tokens.avanza()
            rel_expr(tokens, errors)   
            token = tokens.current()
            if token[0] == "SEMICOLON":
                tokens.avanza()
            else:
                addError(errors, ";" , token[1], tokens.pos)
        else:
            addError(errors, "=" , token[1], tokens.pos)
    else:
        addError(errors, "ID" , content, tokens.pos)

# T -> F T'
def termino(tokens, errors):
  # Llama a factor
  factor(tokens, errors)
  # Luego llama a termino_prime
  termino_prime(tokens, errors)



# E' -> + T E' | epsilon
# <expresion_prime> ::= + <termino> <expresion_prime> | <vacio>
def expr_prime(tokens, errors):
  if(len(tokens.tokens) == 0):
    return
  
  # Obten el token actual
  token, content = tokens.current()
  # Si el token actual es un '+'
  if token == "OP_SUM" or token == "OP_SUB":
    # Avanza al siguiente token
    token, content = tokens.avanza()
    # Llama a termino
    termino(tokens, errors)
    # Luego llama a expr_prime
    expr_prime(tokens, errors)

  # Si no, nada... se asume que es <vacio>



# E -> T E'
# <expresion> ::= <termino> <expresion_prime>
def expr(tokens, errors):
  # Llama a termino
  termino(tokens, errors)
  # Luego, llama a expresion prime...
  expr_prime(tokens, errors)

def statement(tokens, errors):
    if len(tokens.tokens) == 0:
        return
    
    token, content = tokens.current()

    if token == "ID":
        assign(tokens, errors)
    else:
        expr(tokens, errors)  # fallback to expression if it's not an assignment


# Código de prueba
test_code = """
x = 10.5;
y = 3.14 * x + 2.0;
z = y / 2.0 - 1.0;

cond = x > y;
cond = y <= z + 1.5;
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
  print("\n",linea)

  tokens = Tokens(linea)
  errors = []

  statement(tokens, errors)   # Detecta y procesa la línea según el tipo

  if tokens.pos < len(tokens.tokens)-1:       #   Si no se consumio toda la linea, hubo algun token inesperado
    addError( errors, "operador", tokens.current() , tokens.pos )

  if len(errors) == 0 :
    print("OKS\n")
  else:
    for e in errors:
      print(e)
    #print("NOPE\n", tokens.pos)