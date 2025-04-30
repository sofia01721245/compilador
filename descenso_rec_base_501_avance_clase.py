# -*- coding: utf-8 -*-

class Tokens:
    def __init__(self, lista):
        self.tokens = lista
        self.pos = 0

    # Devuelve el token actual
    def current(self):
        return self.tokens[self.pos]

    # Consume un token, avanzando al siguiente
    def avanza(self):
        self.pos += 1
        return self.tokens[self.pos]

# Guarda errores en una lista
def addError(errors, expected, token, index):
  #print(  f"ERROR index {index}: esperaba {expected}, recibio {token}"  )
  errors.append( f"ERROR en index {index}: esperaba {expected}, recibio {token}"  )

# F ->  ( E ) | const_int
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
    elif token == "CTE_INT":
        token, content = tokens.avanza()
    else:
        addError(errors, "( o CTE_INT", content, tokens.pos)

# T' -> * F T' | epsilon
def termino_prime(tokens, errors):
    token, content = tokens.current()
    if token == "OP_MUL":
        token, content = tokens.avanza()
        factor(tokens, errors)
        termino_prime(tokens, errors)

# T -> F T'
def termino(tokens, errors):
    factor(tokens, errors)
    termino_prime(tokens, errors)

# E' -> + T E' | epsilon
# <expresion_prime> ::= + <termino> <expresion_prime> | <vacio>
def expr_prime(tokens, errors):
    token, content = tokens.current()
    if token == "OP_SUM":
        token, content = tokens.avanza()
        termino(tokens, errors)
        expr_prime(tokens, errors)

# E -> T E'
def expr(tokens, errors):
    termino(tokens, errors)
    expr_prime(tokens, errors)

#    Cada linea tiene un EOL al final, para evitar desbordar
#    El tokenizer deberia producirlo
lineas = [
    [["CTE_INT", 14], ["OP_SUM", "+"], ["LPAREN", "("], ["CTE_INT", 14], ["OP_MUL", "*"], ["CTE_INT", 14], ["RPAREN", ")"], ["EOL", ""]],
    [["CTE_INT", 12], ["OP_SUM", "+"], ["EOL", ""]],
    [["CTE_INT", 12], ["OP_SUM", "+"], ["CTE_INT", 12], ["EOL", ""]],
    [["CTE_INT", 12], ["OP_MUL", "*"], ["CTE_INT", 12], ["EOL", ""]],
    [["OP_MUL", "*"], ["CTE_INT", 12], ["EOL", ""]],
    [["OP_SUM", "+"], ["CTE_INT", 12], ["EOL", ""]],
    [["LPAREN", "("], ["CTE_INT", 12], ["OP_SUM", "+"], ["CTE_INT", 12], ["EOL", ""]],
]

for linea in lineas:
    print("\n", linea)

    tokens = Tokens(linea)
    errors = []

    expr(tokens, errors)

    if tokens.pos < len(tokens.tokens) - 1:
        addError(errors, "operador", tokens.current(), tokens.pos)

    if len(errors) == 0:
        print("OKS\n")
    else:
        for e in errors:
            print(e)