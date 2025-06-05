from lexer import PlyTokenizer
from parser_rules import parser, syntax_errors
from utils import print_tree
from semantic import estructura, print_quadruples, print_symbol_table
from vm import convert_quadruples_to_test, test_interpreter

# Crear archivo ld
input_text = """program proquacks;
var n : int ;
  j , i : float;
  s : string;
 
void fact (n : int, a : float)
[  var b : float;
 
    if (n > 1 )
      {  b = a * n * 0.55;
         fact (n-1, b);  
      }
      else
      {  print(a);   }; 

];
 
 
void some_other( c : string )
[  var n : float
   { 
      c = "woooooooooo 9"; 
      print("hello "); 
      xf = 7;
 
      fact(3, 5.8);
   } 
];
 
 
main 
{  n = 5;
   fact(n, 1.1);
 
   fact(n+1, 1.2);
 
    do {
      print(3, "w", 4);
    }while( 3 <7 );
 
    if ( 3 >= 8)
    {
      print("texto ");
      n = 58 + 9 * 5;
    };
 
print("texto ");
some_other("yes")
n = 58 + 9 * 5;
 
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

test = (convert_quadruples_to_test(estructura.cuadruplos))

print(test)

test_interpreter(test)

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
