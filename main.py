from lexer import PlyTokenizer
from parser_rules import parser, syntax_errors
from utils import print_tree
from semantic import estructura, print_quadruples, print_symbol_table, print_memory_allocation, generate_function_data
from vm import convert_quadruples_to_test, test_interpreter

# Crear archivo ld
input_text = """
program complete_test;
var counter : int;
var result : float;
var message : string;

void math_operations(a : int, b : float, c : int)
[ var temp : int;
  var factor : float;
  var output : string;
  { 
    temp = a * c;
    factor = b + temp;
    output = "Result: ";
    
    if(factor > 10.0)
    {
      print(output);
      print(factor);
    }
    else
    {
      temp = temp - 5;
      print(temp);
    };
  }
];

void string_processor(text : string, length : int)
[ var processed : string;
  var count : int;
  {
    processed = text;
    count = length;
    
    print("Processing: ");
    print(processed);
    print("Length: ");
    print(count);
  }
];

main 
{
  counter = 0;
  result = 0.0;
  message = "Hello World";
  
  math_operations(5, 3.14, 2);
  math_operations(1, 15.5, 3);

  
  string_processor("Test String", 11);
  string_processor(message, 11);
  
  counter = 1;
  do {
    result = result + counter * 2.5;
    counter = counter + 1;
    print("Iteration: ");
    print(counter);
    print("Result: ");
    print(result);
  } while(counter <= 5);
  
  counter = 10 + 5 * 3;
  result = counter / 2.0;
  
  print("Final counter: ");
  print(counter);
  print("Final result: ");
  print(result);
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

print("\n--- Semantica  ---")
print(f"Estado de funcion final: {estructura.current_function}")
print(f"Contador de linea: {estructura.linea}")

if estructura.cuadruplos:
    print_quadruples()
    print_symbol_table()
    print_memory_allocation()
    generate_function_data()

    test = convert_quadruples_to_test(estructura.cuadruplos)

    print("\n---Representacion intermediaria ---")
    print(test)

    print("\n--- Ejecutar programa ---")
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
