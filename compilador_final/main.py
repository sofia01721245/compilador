from lexer import PlyTokenizer
from parser_rules import parser, syntax_errors
from utils import print_tree
from semantic import estructura, print_quadruples, print_symbol_table

# Crear archivo ld
input_text = """program mayor_numero;
var x, y, z, mayor : int;


void title(a:int)[
    var b : int;
    a=b;
];


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
    title(x);
    print(mayor);
}
end;
"""

with open("semantica.ld", "w") as f:
    f.write(input_text)

# Leer el archivold 
with open("semantica.ld", "r") as f:
    test_code = f.read()


# ----------------LEXER------------------
tokenizer = PlyTokenizer()

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
