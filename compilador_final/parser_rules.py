from lexer import PlyTokenizer
from semantic import estructura, get_operand_and_type
import ply.yacc as yacc
from lexer import tokens

def p_programa(p):
    'Programa : KEYWORD_PROGRAM ID SEMICOLON vars_opt funcs_opt KEYWORD_MAIN LBRACE body RBRACE KEYWORD_END SEMICOLON'
    # Switch back to global scope for main
    estructura.current_function = 'global'
    p[0] = ('Programa', [p[2], p[4], p[5], p[6], p[8], 'end', ';'])
def p_vars_opt(p):
    '''vars_opt : vars_opt VARS
                | VARS
                | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2 and p[1] != 'empty':
        p[0] = [p[1]]
    else:
        p[0] = []

def p_VARS(p):
    '''VARS : KEYWORD_VAR var_list SEMICOLON'''
    ids = p[2][1]['ids']
    var_type = p[2][1]['type'][1][0]

    for var_id in ids:
        if estructura.func_directory.has_variable(estructura.current_function, var_id):
            estructura.semantic_errors.append(
                f"Variable '{var_id}' ya declarada en función '{estructura.current_function}'."
            )
        else:
            estructura.func_directory.add_variable(var_id, var_type, estructura.current_function, is_param = False)
    p[0] = ('VARS', p[2])

def p_var_list(p):
    '''var_list : ID id_list COLON type'''
    ids = [p[1]] + p[2]
    p[0] = ('var_list', {'ids': ids, 'type': p[4]})

def p_id_list(p):
    '''id_list : COMMA ID id_list
               | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_type(p):
    '''type : KEYWORD_INT
            | KEYWORD_FLOAT
            | KEYWORD_STRING'''
    p[0] = ('type', [p[1]])

def p_funcs_opt(p):
    '''funcs_opt : funcs_opt FUNCS
                 | FUNCS
                 | empty'''
    if len(p) == 3:  # funcs_opt FUNCS
        p[0] = ('funcs_opt', [p[1], p[2]])
    elif len(p) == 2 and p[1] != 'empty':  # single FUNCS
        p[0] = ('funcs_opt', [p[1]])
    else:  # empty
        p[0] = ('funcs_opt', [])

def p_FUNCS(p):
    'FUNCS : KEYWORD_VOID ID func_start LPAREN parametros_opt RPAREN LBRACKET vars_opt body RBRACKET func_end SEMICOLON'
    func_name = p[2]
    params = p[5]
    vars_local = p[8]
    body = p[9]
    p[0] = ('FUNCS', [func_name, params, vars_local, body])

def p_func_start(p):
    'func_start :'
    # Get the function name from the parser stack
    # p[-1] refers to the ID token that was just parsed
    func_name = p[-1]
    
    # Add function to directory and switch scope
    try:
        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, '=', func_name, None, "function"))
        start_quad = estructura.linea
        estructura.func_directory.add_function(func_name, start_quad)
        estructura.current_function = func_name
    except Exception as e:
        estructura.semantic_errors.append(str(e))

def p_func_end(p):
    'func_end :'
    # Switch back to global scope when function ends
    estructura.current_function = 'global'

def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | empty'''
    if p[1] == 'empty' or p[1] is None:
        p[0] = ('parametros_opt', [])
    else:
        p[0] = ('parametros_opt', [p[1]])

def p_parametros(p):
    '''parametros : ID COLON type param_list'''
    # Collect the first parameter
    # First parameter
    all_params = [(p[1], p[3][1][0])]  # e.g., ('a', 'int')
    # Additional parameters from param_list
    for param in p[4]:
        all_params.append((param[0], param[1][1][0]))  # (ID, 'type')

    # Declare each parameter as a variable
    for var_id, var_type in all_params:
        if estructura.func_directory.has_variable(estructura.current_function, var_id):
            estructura.semantic_errors.append(
                f"Parametro '{var_id}' ya declarado en función '{estructura.current_function}'."
            )
        else:
            estructura.func_directory.add_variable(var_id, var_type, estructura.current_function, is_param = True)  

    p[0] = ('parametros', all_params)

def p_param_list(p):
    '''param_list : COMMA ID COLON type param_list
                  | empty'''
    if len(p) == 6:  # COMMA ID COLON type param_list
        p[0] = [('ID', p[2]), p[4]] + p[5]
    else:  # empty
        p[0] = []

def p_body(p):
    'body : statement_list'
    p[0] = ('body', [p[1]])

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | statement
                      | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        # Could be a single statement or empty
        if p[1] is None:  # empty production returns None
            p[0] = []
        else:
            p[0] = [p[1]]

def p_statement(p):
    '''statement : assign
                 | condition
                 | cycle
                 | f_call
                 | print'''
    p[0] = ('statement', [p[1]])

def p_assign(p):
    'assign : ID ASSIGN_SIGN expresion SEMICOLON'
    
    if not estructura.stack_operandos:
        estructura.semantic_errors.append("Error: No hay operando para asignación.")
        return
        
    valor, tipo = estructura.stack_operandos.pop()
    var_name = p[1]

    # Check if variable exists
    if estructura.func_directory.has_variable(estructura.current_function, var_name):
        tipo_variable = estructura.func_directory.get_variable_type(var_name, estructura.current_function)
    else:
        estructura.semantic_errors.append(f"Variable '{var_name}' no declarada.")
        return

    # Type compatibility check
    if tipo != tipo_variable:
        estructura.semantic_errors.append(f"Error de tipos: No se puede asignar {tipo} a {tipo_variable}.")
        return
    
    # Generate quadruple
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, '=', var_name, valor, None, tipo_variable))
    
    p[0] = ('assign', [('ID', var_name), p[3]])

def p_print(p):
    'print : KEYWORD_PRINT LPAREN print_items RPAREN SEMICOLON'
    for item in p[3]:
        if item[0] == 'print_item':
            # Handle string literals
            if item[1][0][0] == 'CTE_STRING':
                estructura.linea += 1
                estructura.cuadruplos.append((estructura.linea, 'PRINT', item[1][0][1], None, None, estructura.func_directory.get_variable_type(item[1][0][1], estructura.current_function)))
        else:
            if estructura.stack_operandos:
                operand, _ = estructura.stack_operandos.pop()
                estructura.linea += 1
                estructura.cuadruplos.append((estructura.linea, 'PRINT', operand, None, None, "operand"))
    
    p[0] = ('print', [p[3]])

def p_print_items(p):
    '''print_items : print_items COMMA print_item
                   | print_item'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_print_item(p):
    '''print_item : expresion
                  | CTE_STRING'''
    if isinstance(p[1], tuple) and p[1][0] != 'CTE_STRING':
        p[0] = ('expresion', p[1])
    else:
        p[0] = ('print_item', [('CTE_STRING', p[1])])

def p_cycle(p):
    'cycle : KEYWORD_DO LBRACE body RBRACE KEYWORD_WHILE LPAREN expresion RPAREN SEMICOLON'
    
    start_line = estructura.linea + 1 - len(p[2])

    if not estructura.stack_operandos:
        estructura.semantic_errors.append("Error de semantica: No hay expresión para condición del ciclo.")
        return
    
    valor, tipo = estructura.stack_operandos.pop()
    if tipo != 'bool':
        estructura.semantic_errors.append(f"Error de semantica: La condición del ciclo debe ser booleana en línea {estructura.linea + 1}")
        return

    # GOTOT para regresar al inicio del ciclo si la condición es verdadera
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOT', valor, None, start_line))

    p[0] = ('cycle', [p[2], ('condition', p[5])])


def p_condition(p):
    'condition : KEYWORD_IF LPAREN expresion RPAREN cuadr_if LBRACE body RBRACE else_arg SEMICOLON'
    if estructura.stack_saltos:
        salto_final_else = estructura.stack_saltos.pop()
        estructura.cuadruplos[salto_final_else] = (
            estructura.cuadruplos[salto_final_else][0],
            estructura.cuadruplos[salto_final_else][1],
            estructura.cuadruplos[salto_final_else][2],
            estructura.cuadruplos[salto_final_else][3],
            estructura.linea + 1
        )
    p[0] = ('condition', [p[1], p[3], p[7], p[9]])

def p_cuadr_if(p):
    'cuadr_if :'
    valor, tipo = estructura.stack_operandos.pop()
    if tipo != 'bool':
        estructura.semantic_errors.append(f"Error: La condición no es booleana. Tipo encontrado: {tipo}")
        return
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOF', valor, None, None))
    estructura.stack_saltos.append(estructura.linea - 1)

def p_else_arg(p):
    'else_arg : KEYWORD_ELSE cuadr_else LBRACE body RBRACE'
    p[0] = [p[1], p[4]]

def p_cuadr_else(p):
    'cuadr_else :'
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTO', None, None, None))
    goto_final_index = estructura.linea - 1

    if len(estructura.stack_saltos) > 0:
        gotof_index = estructura.stack_saltos.pop()
        estructura.cuadruplos[gotof_index] = (
            estructura.cuadruplos[gotof_index][0],
            estructura.cuadruplos[gotof_index][1],
            estructura.cuadruplos[gotof_index][2],
            estructura.cuadruplos[gotof_index][3],
            estructura.linea + 1 
        )
        estructura.stack_saltos.append(goto_final_index)
    else:
        estructura.semantic_errors.append(f"Error de semantica: No hay salto para asignar en ELSE")

def p_else_arg_empty(p):
    'else_arg : empty'
    if len(estructura.stack_saltos) > 0:
        gotof_index = estructura.stack_saltos.pop()
        estructura.cuadruplos[gotof_index] = (
            estructura.cuadruplos[gotof_index][0],
            estructura.cuadruplos[gotof_index][1],
            estructura.cuadruplos[gotof_index][2],
            estructura.cuadruplos[gotof_index][3],
            estructura.linea + 1
        )

def p_f_call(p):
    'f_call : ID LPAREN expresion_list_opt RPAREN SEMICOLON'
    func_name = p[1]
    args = (p[3])[1][0][1]  # lista de expresiones
    # verificar que exsiste la funcion
    if estructura.func_directory.function_exsist(func_name) == False:
        estructura.semantic_errors.append(f"Funcion '{func_name}' no esta declarada.")

    expected_params = estructura.func_directory.get_func_param(func_name)
    # validar cuantos argumentos se esperan
    if len(args) != len(expected_params):
        estructura.semantic_errors.append(f"Funcion '{func_name}' necesita {len(expected_params)} argumentos, pero recibió {len(args)}.")

    # validar tipos
    for i in range(len(expected_params)):
        param_name, expected_type = expected_params[i]
        arg = args[i][1]
        arg_type = estructura.func_directory.get_variable_type(arg, estructura.current_function)

        if arg_type != expected_type:
            estructura.semantic_errors.append(f"Error semantico de tipos en argumento {i+1} de la funcion '{func_name}'. Se esperaba '{expected_type}', y recibió '{arg_type}'.")
    
    func_start_quad = estructura.func_directory.get_start_line(func_name)
    estructura.linea+=1
    estructura.cuadruplos.append((estructura.linea, 'GOTO', func_name, None, func_start_quad))
    p[0] = ('f_call', {
        'function': func_name,
        'args': args
    })

def p_expresion_list_opt(p):
    '''expresion_list_opt : expresion_list
                          | empty'''
    p[0] = ('expresion_list_opt', p[1] if isinstance(p[1], list) else [])

def p_expresion_list(p):
    '''expresion_list : expresion_list COMMA expresion
                      | expresion'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expresion(p):
    '''expresion : exp comparador exp
                 | exp'''
    if len(p) == 4:
        # Comparison operation - existing logic is mostly correct
        if len(estructura.stack_operandos) < 2:
            estructura.semantic_errors.append("Error: Operandos insuficientes para comparación.")
            return
            
        right_val, right_type = estructura.stack_operandos.pop()
        left_val, left_type = estructura.stack_operandos.pop()
        op = p[2][1][0]

        resultado_tipo = estructura.cubo.get((left_type, right_type, op))
        if resultado_tipo is None:
            estructura.semantic_errors.append(f"Operación inválida: {left_type} {op} {right_type}")
            return

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))
        
        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, left_val, right_val, temp_var))
        
        p[0] = ('expresion', [p[1], p[2], p[3]])
    else:
        # Single expression - pass through
        p[0] = p[1]

def p_comparador(p):
    '''comparador : LESS
                  | GREATER
                  | NOT_EQUAL
                  | EQUAL
                  | GREATER_EQUAL
                  | LESS_EQUAL'''
    p[0] = ('comparador', [p[1]])

def p_exp(p):
    '''exp : exp OP_SUM termino
           | exp OP_SUB termino
           | termino'''
    if len(p) == 4:
        left = p[1]
        op = p[2]
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)
        if tipo1 is None or tipo2 is None:
            estructura.cuadruplos.append(f"Unknown operand types: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.cuadruplos.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea,op,value1,value2,temp_var))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino OP_MUL factor
               | termino OP_DIV factor
               | factor'''
    if len(p) == 4:
        left = p[1]
        op = p[2]
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)
        if tipo1 is None or tipo2 is None:
            estructura.cuadruplos.append(f"Unknown types: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.cuadruplos.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, value1, value2, temp_var))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]


def p_factor(p):
    '''factor : LPAREN expresion RPAREN
              | OP_SUM varcte
              | OP_SUB varcte
              | varcte'''
    if len(p) == 4:  # Parentheses
        p[0] = p[2]  # Pass through the expression result
    elif len(p) == 3:  # Unary + or -
        if not estructura.stack_operandos:
            estructura.semantic_errors.append("Error: No hay operando para operación unaria.")
            return
            
        valor, tipo = estructura.stack_operandos.pop()
        
        if p[1] == '-':
            # Generate unary minus quadruple
            temp_var = estructura.new_temp()
            estructura.linea += 1
            estructura.cuadruplos.append((estructura.linea, 'UMINUS', valor, None, temp_var))
            estructura.stack_operandos.append((temp_var, tipo))
            p[0] = ('factor', [p[1], p[2]])
        else:  # Unary plus - no operation needed
            estructura.stack_operandos.append((valor, tipo))
            p[0] = ('factor', [p[2]])
    else:  # Single varcte
        p[0] = p[1]

def p_varcte(p):
    '''varcte : ID
              | CTE_INT
              | CTE_FLOAT'''
    if p.slice[1].type == 'ID':
        var_name = p[1]
        # Look up variable type in symbol table
        if estructura.func_directory.has_variable(estructura.current_function, var_name):
            var_type = estructura.func_directory.get_variable_type(var_name, estructura.current_function)
            estructura.stack_operandos.append((var_name, var_type))
        else:
            estructura.semantic_errors.append(f"Variable '{var_name}' no declarada.")
            estructura.stack_operandos.append((var_name, 'error'))
        p[0] = ('varcte', [('ID', p[1])])
    elif p.slice[1].type == 'CTE_INT':
        estructura.stack_operandos.append((p[1], 'int'))
        p[0] = ('varcte', [('CTE_INT', p[1])])
    elif p.slice[1].type == 'CTE_FLOAT':
        estructura.stack_operandos.append((p[1], 'float'))
        p[0] = ('varcte', [('CTE_FLOAT', p[1])])

#agregar cte int y float separado
'''def p_CTE_INT(p): 
    'CTE: CTE_INT'
    estructura.stack_operandos.append([p[1],'int'])

def p_CTE_FLOAT(p): 
    'CTE: CTE_FLOAT'
    estructura.stack_operandos.append([p[1],'float'])
'''
def p_empty(p):
    '''empty :'''
    p[0] = None

def p_error(p):
    if p:
        msg = f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)
        # Skip the problematic token
        parser.errok()
    else:
        syntax_errors.append("Error de sintaxis: fin de archivo inesperado")

parser = yacc.yacc(debug=True)
syntax_errors = []
