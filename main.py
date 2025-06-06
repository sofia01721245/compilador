from lexer import PlyTokenizer
from parser_rules import parser, syntax_errors
from utils import print_tree
from semantic import estructura, print_quadruples, print_symbol_table, print_memory_allocation
from vm import convert_quadruples_to_test, test_interpreter

# Crear archivo ld
input_text = """
program prockaks;
var n : int;

void fact(n:int, a:int)
[ var b: int;
    { if(n>1)
        {
            b=a*n;
            fact(n-1, b);
        }else
        { print(a); };
    }
];

main
{   
n = 5;
    fact(n, 1);
    fact(n+1, 1);
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

estructura.__init__()  

try:
    # Parse
    print("Starting parse...")
    parse_tree = parser.parse(test_code, lexer=tokenizer.lexer, debug=False)
    print(f"Parse completed. Tree type: {type(parse_tree)}")
    
    if parse_tree is None:
        print("ERROR: Parser returned None - check for syntax errors")
        # Try to get more parser debug info
        import ply.yacc as yacc
        yacc.restart()
        parse_tree = parser.parse(test_code, lexer=tokenizer.lexer, debug=True)
    
except Exception as e:
    print(f"Exception during parsing: {e}")
    import traceback
    traceback.print_exc()
    parse_tree = None

print("\n--- PARSE TREE ---")
if parse_tree is not None:
    print_tree(parse_tree)
else:
    print("Parse tree is None - parsing failed")

print("\n--- SEMANTIC ANALYSIS RESULTS ---")
print(f"Final operand stack: {estructura.stack_operandos}")
print(f"Current function: {estructura.current_function}")
print(f"Line counter: {estructura.linea}")

if estructura.cuadruplos:
    print_quadruples()
    print_symbol_table()
    print_memory_allocation()

    test = convert_quadruples_to_test(estructura.cuadruplos)

    print("\n---Representacion intermediaria ---")
    print(test)

    print("\n=== Ejecutar programa ===")
    test_interpreter(test)
else:
    print("No quadruples generated - compilation failed")

if tokenizer.errors:
    print("\n--- ERRORES DE LEXICO DETECTADOS ---")
    for err in tokenizer.errors:
        lineno, lexpos, char = err
        print(f"Lexer error: Unrecognized character '{char}' at line {lineno}, position {lexpos}")
else:
    print("\n---NO SE DETECTARON ERRORES LÉXICOS ---")


if syntax_errors:
    print("\n--- ERRORES DE SINTAXIS DETECTADOS ---")
    for err in syntax_errors:
        print(err)
else:
    print("\n---NO SE DETECTARON ERRORES SINTÁCTICOS ---")

if estructura.semantic_errors:
    print("\n--- ERRORES SEMÁNTICOS DETECTADOS ---")
    for err in estructura.semantic_errors:
        print(err)
else:
    print("\n---NO SE DETECTARON ERRORES SEMÁNTICOS ---")
