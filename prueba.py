import ply.lex as lex
from collections import defaultdict

# Palabras reservadas
reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'print' : 'PRINT',
    'main' : 'MAIN',
    'program' : 'PROGRAM',
    'var' : 'VAR',
    'int' : 'INT',
    'float' : 'FLOAT',
    'do' : 'DO',
    'void' : 'VOID',
    'string' : 'STRING',
    'end' : 'END',
} 

# Tokens
tokens = [
    'CONST_INT',
    'IDENTIFIER',
    'OP_ASIGNA',
    'EQUALS',
    'SEMICOL',
    'OP_ARITH',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'LSQBRACKET',
    'RSQBRACKET',
    'LBRACKET',
    'RBRACKET',
    'GREATER',
    'LESS',
    'NOT_EQUAL',
    'LESS_EQUAL',
    'GREATER_EQUAL',
    'COMMENT',
    'COLON',
    'CONST_FLOAT',
    'CONST_STRING',
] + list(reserved.values())

# Expresiones regulares
t_OP_ASIGNA = r'='
t_EQUALS = r'=='
t_SEMICOL = r';'
t_OP_ARITH = r'[-+*/]'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQBRACKET = r'\['
t_RSQBRACKET = r'\]'
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_GREATER = r'>'
t_LESS = r'<'
t_NOT_EQUAL = r'!='
t_LESS_EQUAL = r'<='
t_GREATER_EQUAL = r'>='
t_COLON = r':'

#Funciones de expresiones regulares
def t_COMMENT(t):
    r'\#.*'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')
    return t

def t_CONST_FLOAT(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_CONST_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_CONST_STRING(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character {t.value[0]} in position {t.lexpos}")
    t.lexer.skip(1)

# Crear el lexer
lexer = lex.lex()

# Clase de tokens
class Tokens:
    def __init__(self, text):
        self.tokens = []
        self.pos = 0
        
        # A comparacion del codigo orignal, aqui se agrega un while que recorre el texto por el lexer y va agregando los tokens al array de tokens
        lexer.input(text)
        while True:
            tok = lexer.token()
            if not tok:
                break

            self.tokens.append((tok.type, tok.value))
        
        # Agregar el token EOL al final
        self.tokens.append(("EOL", ""))

    def current(self):
        return self.tokens[self.pos]

    def avanza(self):
        self.pos += 1
        return self.tokens[self.pos]

def addError(errors, expected, token, index):
    errors.append(f"ERROR en index {index}: esperaba {expected}, recibio {token}")

#FACTOR ::= '(' EXPRESION ')'| ( '+' | '-' )? ( 'id' | CTE )
def factor(tokens, errors):
    token, content = tokens.current()

    if token == "LPAREN":
        token, content = tokens.avanza()
        expr(tokens, errors)
        token, content = tokens.current()
        if token == "RPAREN":
            token, content = tokens.avanza()
        else:
            addError(errors, ")", content, tokens.pos)
    else:
        if token == "OP_ARITH" and content == "-" or content == "+":
            token, content = tokens.avanza()
        if token == "IDENTIFIER":
            token, content = tokens.avanza()
        else:
            cte(tokens, errors)

# CTE ::= 'cte_int'| 'cte_float'
def cte(tokens, errors):
    token, content = tokens.current()
    if token == "CONST_INT":
        token, content = tokens.avanza()
    elif token == "CONST_FLOAT":
        token, content = tokens.avanza()
    else:
        addError(errors, "CONST_INT o CONST_FLOAT", content, tokens.pos)

# TERMINO_PRIME ::= ( ( '*' | '/' ) FACTOR TERMINO_PRIME )*
def termino_prime(tokens, errors):
    token, content = tokens.current()

    if token == "OP_ARITH" and content == "*" or content == "/":
        token, content = tokens.avanza()
        factor(tokens, errors)
        termino_prime(tokens, errors)

# TERMINO ::= FACTOR TERMINO_PRIME
def termino(tokens, errors):
    factor(tokens, errors)
    termino_prime(tokens, errors)

# EXP_PRIME ::= ( ( '+' | '-' ) TERMINO EXP_PRIME)*
def expr_prime(tokens, errors):
    token, content = tokens.current()
    
    if token == "OP_ARITH" and content == "+" or content == "-":
        token, content = tokens.avanza()
        termino(tokens, errors)
        expr_prime(tokens, errors)

# EXP ::= TERMINO EXP_PRIME
def expr(tokens, errors):
    termino(tokens, errors)
    expr_prime(tokens, errors)

# EXPRESION::= EXP ( ( '>' | '<' | '!=' | '==' | '<=' | '>=' ) EXP )?
def expresion(tokens, errors):
    expr(tokens, errors)
    token, content = tokens.current()
    if token == "LESS":
        token, content = tokens.avanza()
        expr(tokens, errors)
    elif token == "GREATER":
        token, content = tokens.avanza()
        expr(tokens, errors)
    elif token == "LESS_EQUAL":
        token, content = tokens.avanza()
        expr(tokens, errors)
    elif token == "GREATER_EQUAL":
        token, content = tokens.avanza()
        expr(tokens, errors)
    elif token == "NOT_EQUAL":
        token, content = tokens.avanza()
        expr(tokens, errors)
    elif token == "EQUALS":
        token, content = tokens.avanza()
        expr(tokens, errors)
       
# ASSIGN ::= 'id' '=' EXPRESION ';'
def assign(tokens, errors):
    token, content = tokens.current()
    if token == "IDENTIFIER":
        token, content = tokens.avanza()
        if token == "OP_ASIGNA":
            token, content = tokens.avanza()
            expresion(tokens, errors)
            token, content = tokens.current()
            if token == "SEMICOL":
                token, content = tokens.avanza()
            else:
                addError(errors, ";", content, tokens.pos)
        else:
            addError(errors, "=", content, tokens.pos)
    else:
        addError(errors, "IDENTIFIER", content, tokens.pos)
        
# Inicio de el parser
def parser(text):
    tokens = Tokens(text)
    errors = []
    assign(tokens, errors)

    if tokens.pos < len(tokens.tokens)-1: #   Si no se consumio toda la linea, hubo algun token inesperado
        addError(errors, "operador", tokens.current(), tokens.pos)

    return errors


program = """ x = 10.5;
y = 3.14 * x + 2.0;
z = y / 2.0 - 1.0;

cond = x > y;
cond = y <= z + 1.5;
"""

with open("code.ld", "r") as file:
    program = file.read()

program = program.splitlines()

for line in program:
    print(f"\nTesting: {line}")
    errors = parser(line)
    
    if len(errors) == 0:
        print("OKS")
    else:
        for e in errors:
            print(e) 