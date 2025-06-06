from lexer import PlyTokenizer
from semantic import estructura, get_operand_and_type
import ply.yacc as yacc
from lexer import tokens

# agregar presedence para evitar warnings
precedence = (
    ('left', 'COMMA'),
    ('right', 'COLON'),
    ('right', 'ASSIGN_SIGN'),
)

def p_programa(p):
    'Programa : KEYWORD_PROGRAM ID SEMICOLON vars_opt funcs_opt main_marker LBRACE body RBRACE KEYWORD_END SEMICOLON'
    
    # gotomain al principio
    estructura.cuadruplos.insert(0, (1, 'GOTOMAIN', -1, -1, estructura.main_start_line + 2)) # mas dos por shift
    
    for i in range(1, len(estructura.cuadruplos)):
        old_quad = estructura.cuadruplos[i]
        estructura.cuadruplos[i] = (old_quad[0] + 1,) + old_quad[1:]
    
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea + 1, 'END', -1, -1, -1))
    
    estructura.current_function = 'global'
    p[0] = ('Programa', [('program', p[2]), p[4], p[5], ('main', p[8]), ('end', ';')])

def p_main_marker(p):
    'main_marker : KEYWORD_MAIN'
    estructura.main_start_line = estructura.linea + 1  # Next quadruple will be main start
    print(f"DEBUG: Main starts at line {estructura.main_start_line}")
    p[0] = ('main_marker', p[1])

def p_vars_opt(p):
    '''vars_opt : var_block
                | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = ('vars', p[1])
    else:
        p[0] = ('vars', [])

def p_var_block(p):
    '''var_block : KEYWORD_VAR var_lines'''
    decls = []
    for var_decl in p[2]:
        ids = var_decl[1]['ids']
        var_type = var_decl[1]['type']

        for var_id in ids:
            if estructura.func_directory.has_variable(estructura.current_function, var_id):
                estructura.semantic_errors.append(
                    f"Variable '{var_id}' ya declarada en función '{estructura.current_function}'."
                )
            else:
                estructura.func_directory.add_variable(var_id, var_type, estructura.current_function, is_param=False)
    p[0] = p[2]

# Add precedence to help with parsing decisions
precedence = (
    ('left', 'COMMA'),
    ('left', 'SEMICOLON'),
    ('left', 'COLON'),
    ('left', 'ASSIGN_SIGN'),
)

def p_var_lines(p):
    '''var_lines : var_lines var_list SEMICOLON
                 | var_list SEMICOLON'''
    if len(p) == 4:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_var_lines(p):
    '''var_lines : var_lines var_list SEMICOLON
                 | var_list SEMICOLON'''
    if len(p) == 4:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

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
    p[0] = p[1]

def p_funcs_opt(p):
    '''funcs_opt : funcs_opt FUNCS
                 | FUNCS
                 | empty'''
    if len(p) == 3:
        p[0] = ('funcs', [p[1], p[2]])
    elif len(p) == 2 and p[1] != None:
        p[0] = ('funcs', [p[1]])
    else:
        p[0] = ('funcs', [])

def p_FUNCS(p):
    'FUNCS : KEYWORD_VOID ID func_start LPAREN parametros_opt RPAREN LBRACKET vars_opt LBRACE body RBRACE RBRACKET func_end SEMICOLON'
    func_name = p[2]
    params = p[5]
    vars_local = p[8]
    body = p[10]  # body is now at position 10 due to added LBRACE
    
    # Void functions end naturally without explicit return
    
    p[0] = ('function', [('void', func_name), params, vars_local, body])

def p_func_start(p):
    'func_start :'
    func_name = p[-1]
    
    try:
        estructura.linea += 1
        start_quad = estructura.linea
        estructura.func_directory.add_function(func_name, start_quad)
        estructura.current_function = func_name
    except Exception as e:
        estructura.semantic_errors.append(str(e))

def p_func_end(p):
    'func_end :'
    # Add function end marker for void functions
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'ENDFUNC', -1, -1, -1))
    estructura.current_function = 'global'

def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | empty'''
    if p[1] == 'empty' or p[1] is None:
        p[0] = ('parametros_opt', [])
    else:
        p[0] = ('parametros_opt', p[1])

def p_parametros(p):
    '''parametros : parametros COMMA ID COLON type
                  | ID COLON type'''
    
    if len(p) == 6:
        var_id = p[3]
        var_type = p[5][1] if isinstance(p[5], tuple) else p[5]
        
        if estructura.func_directory.has_variable(estructura.current_function, var_id):
            existing_type = estructura.func_directory.get_variable_type(var_id, estructura.current_function)
            if existing_type != var_type:
                estructura.semantic_errors.append(
                    f"Error de tipos: Parametro '{var_id}' ya declarado con tipo '{existing_type}', no se puede redeclarar como '{var_type}'."
                )
            else:
                estructura.semantic_errors.append(
                    f"Parametro '{var_id}' ya declarado en función '{estructura.current_function}'."
                )
        else:
            estructura.func_directory.add_variable(var_id, var_type, estructura.current_function, is_param=True)
        
        prev_params = p[1][1] if isinstance(p[1], tuple) and len(p[1]) > 1 else []
        all_params = prev_params + [(var_id, var_type)]
        
    else:  
        var_id = p[1]
        var_type = p[3][1] if isinstance(p[3], tuple) else p[3]
        
        if estructura.func_directory.has_variable(estructura.current_function, var_id):
            existing_type = estructura.func_directory.get_variable_type(var_id, estructura.current_function)
            if existing_type != var_type:
                estructura.semantic_errors.append(
                    f"Error de tipos: Parametro '{var_id}' ya declarado con tipo '{existing_type}', no se puede redeclarar como '{var_type}'."
                )
            else:
                estructura.semantic_errors.append(
                    f"Parametro '{var_id}' ya declarado en función '{estructura.current_function}'."
                )
        else:
            estructura.func_directory.add_variable(var_id, var_type, estructura.current_function, is_param=True)

        all_params = [(var_id, var_type)]
    
    p[0] = ('parametros', all_params)

def p_body(p):
    'body : statement_list'
    p[0] = ('body', p[1])

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | statement
                      | empty'''
    if len(p) == 3:
        if p[2] is None:
            p[0] = [p[1]]
        elif isinstance(p[2], list):
            p[0] = [p[1]] + p[2]
        elif isinstance(p[2], tuple):
            p[0] = [p[1]] + [p[2]]
        else:
            p[0] = [p[1]]
    elif len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    
def p_statement(p):
    '''statement : assign
                 | condition
                 | cycle
                 | f_call
                 | print'''
    p[0] = ('statement', p[1])

def p_assign(p):
    'assign : ID ASSIGN_SIGN expresion SEMICOLON'
    
    if not estructura.stack_operandos:
        estructura.semantic_errors.append("Error: No hay operando para asignación.")
        return
        
    valor, tipo_expresion = estructura.stack_operandos.pop()
    var_name = p[1]

    if estructura.func_directory.has_variable(estructura.current_function, var_name):
        tipo_variable = estructura.func_directory.get_variable_type(var_name, estructura.current_function)
    else:
        estructura.semantic_errors.append(f"Variable '{var_name}' no declarada.")
        return

    if tipo_expresion != tipo_variable:
        estructura.semantic_errors.append(f"Error de tipos: No se puede asignar '{tipo_expresion}' a variable '{var_name}' de tipo '{tipo_variable}'.")
        return
    
    # Get memory addresses
    var_address = estructura.get_operand_address(var_name)
    value_address = estructura.get_operand_address(valor)
    
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, '=', value_address, -1, var_address))
    
    p[0] = ('assign', [('ID', var_name), p[3]])

def p_print(p):
    'print : KEYWORD_PRINT LPAREN print_items RPAREN SEMICOLON'
    
    # Count expressions in print items
    expr_count = 0
    for item in p[3]:
        if item[0] == 'expresion':
            expr_count += 1
    
    # Pop operands for expressions (in reverse order)
    temp_operands = []
    for _ in range(expr_count):
        if estructura.stack_operandos:
            temp_operands.append(estructura.stack_operandos.pop())
    
    temp_operands.reverse()
    operand_index = 0
    
    # Generate print quadruples
    for item in p[3]:
        if item[0] == 'print_item' and len(item[1]) > 0 and item[1][0][0] == 'CTE_STRING':
            # String literal
            string_val = item[1][0][1]
            const_address = estructura.get_operand_address(string_val)
            estructura.linea += 1
            estructura.cuadruplos.append((estructura.linea, 'PRINT', const_address, -1, -1))
        elif item[0] == 'expresion':
            # Expression result
            if operand_index < len(temp_operands):
                operand, _ = temp_operands[operand_index]
                operand_address = estructura.get_operand_address(operand)
                operand_index += 1
                estructura.linea += 1
                estructura.cuadruplos.append((estructura.linea, 'PRINT', operand_address, -1, -1))
    
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
                  | varcte'''
    if isinstance(p[1], tuple) and p[1][0] != 'CTE_STRING':
        p[0] = ('expresion', p[1])
    else:
        p[0] = ('print_item', [('CTE_STRING', p[1])])

def p_cycle(p):
    'cycle : KEYWORD_DO cuadr_do LBRACE body RBRACE KEYWORD_WHILE LPAREN expresion RPAREN SEMICOLON'

    if not estructura.stack_operandos:
        estructura.semantic_errors.append("Error: No hay expresión para condición del ciclo.")
        return

    valor, tipo = estructura.stack_operandos.pop()
    if tipo != 'bool':
        estructura.semantic_errors.append(f"Error: La condición del ciclo debe ser booleana.")
        return

    if estructura.stack_saltos:
        start_line = estructura.stack_saltos.pop()
    else:
        estructura.semantic_errors.append("Error: No se encontró el inicio del ciclo.")
        return

    # Get address for condition value
    condition_address = estructura.get_operand_address(valor)

    # Generate GOTOT to loop back
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOT', condition_address, -1, start_line))

    p[0] = ('cycle', [p[4], ('expresion', p[8])])

def p_cuadr_do(p):
    'cuadr_do :'
    estructura.stack_saltos.append(estructura.linea + 1)

def p_condition(p):
    'condition : KEYWORD_IF LPAREN expresion RPAREN cuadr_if LBRACE body RBRACE else_arg SEMICOLON'
    if estructura.stack_saltos:
        salto_final_else = estructura.stack_saltos.pop()
        # Fix the jump destination for the final GOTO
        old_quad = estructura.cuadruplos[salto_final_else]
        estructura.cuadruplos[salto_final_else] = (old_quad[0], old_quad[1], old_quad[2], old_quad[3], estructura.linea + 1)
    p[0] = ('condition', [p[1], p[3], p[7], p[9]])

def p_cuadr_if(p):
    'cuadr_if :'
    if not estructura.stack_operandos:
        estructura.semantic_errors.append("Error: No hay operando para condición IF.")
        return
        
    valor, tipo = estructura.stack_operandos.pop()
    if tipo != 'bool':
        estructura.semantic_errors.append(f"Error: La condición no es booleana. Tipo encontrado: {tipo}")
        return
    
    condition_address = estructura.get_operand_address(valor)
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTOF', condition_address, -1, -1))  # Will be filled later
    estructura.stack_saltos.append(estructura.linea - 1)

def p_else_arg(p):
    'else_arg : KEYWORD_ELSE cuadr_else LBRACE body RBRACE'
    p[0] = [p[1], p[4]]

def p_cuadr_else(p):
    'cuadr_else :'
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOTO', -1, -1, -1))  # Will be filled later
    goto_final_index = estructura.linea - 1

    if estructura.stack_saltos:
        gotof_index = estructura.stack_saltos.pop()
        # Fill in the GOTOF destination
        old_quad = estructura.cuadruplos[gotof_index]
        estructura.cuadruplos[gotof_index] = (old_quad[0], old_quad[1], old_quad[2], old_quad[3], estructura.linea + 1)
        estructura.stack_saltos.append(goto_final_index)
    else:
        estructura.semantic_errors.append("Error: No hay salto para asignar en ELSE")

def p_else_arg_empty(p):
    'else_arg : empty'
    if estructura.stack_saltos:
        gotof_index = estructura.stack_saltos.pop()
        # Fill in the GOTOF destination
        old_quad = estructura.cuadruplos[gotof_index]
        estructura.cuadruplos[gotof_index] = (old_quad[0], old_quad[1], old_quad[2], old_quad[3], estructura.linea + 1)

def p_f_call_simple(p):
    'f_call : ID LPAREN expresion_list_opt RPAREN SEMICOLON'
    func_name = p[1]
    
    # Get expression list
    if isinstance(p[3], tuple) and len(p[3]) > 1:
        expr_list = p[3][1]
    else:
        expr_list = []
    
    # Pop arguments from operand stack
    args = []
    for i in range(len(expr_list)):
        if estructura.stack_operandos:
            operand, op_type = estructura.stack_operandos.pop()
            args.insert(0, (operand, op_type))
        
    if not estructura.func_directory.function_exsist(func_name):
        estructura.semantic_errors.append(f"Funcion '{func_name}' no esta declarada.")
        return

    expected_params = estructura.func_directory.get_func_param(func_name)
    
    # Check argument count and types
    if len(args) != len(expected_params):
        estructura.semantic_errors.append(f"Funcion '{func_name}' necesita {len(expected_params)} argumentos, pero recibió {len(args)}.")
        return

    # Generate ERA (space allocation) quadruple
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'ERA', func_name, -1, -1))

    # Generate parameter assignment quadruples
    for i, (arg_value, arg_type) in enumerate(args):
        expected_param_name, expected_type = expected_params[i]
        if arg_type != expected_type:
            estructura.semantic_errors.append(
                f"Error de tipo en llamada a '{func_name}': "
                f"argumento {i+1} ('{arg_value}') es '{arg_type}' pero el parametro '{expected_param_name}' espera '{expected_type}'"
            )
            return
        
        # Get memory addresses
        arg_address = estructura.get_operand_address(arg_value)
        param_address = estructura.func_directory.get_variable_address(expected_param_name, func_name)
        
        # Generate quadruple to assign argument value to parameter
        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, 'PARAM', arg_address, -1, param_address))

    # Generate function call quadruple
    func_start_quad = estructura.func_directory.get_start_line(func_name)
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, 'GOSUB', func_name, -1, func_start_quad))
    
    p[0] = ('f_call', {'function': func_name, 'args': args})

def p_expresion_list_opt(p):
    '''expresion_list_opt : expresion_list
                          | empty'''
    p[0] = ('expresion_list_opt', p[1] if isinstance(p[1], list) else [])

def p_expresion_list(p):
    '''expresion_list : expresion_list COMMA expresion
                      | expresion'''
    if len(p) == 4:        
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1]]
    
def p_expresion(p):
    '''expresion : exp comparador exp
                 | exp'''
    if len(p) == 4:
        # Comparison operation
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

        temp_var, temp_address = estructura.new_temp(resultado_tipo)
        estructura.stack_operandos.append((temp_var, resultado_tipo))
        
        # Get memory addresses
        left_address = estructura.get_operand_address(left_val)
        right_address = estructura.get_operand_address(right_val)
        
        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, left_address, right_address, temp_address))
        
        p[0] = ('expresion', [p[1], p[2], p[3]])
    else:
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
        if len(estructura.stack_operandos) < 2:
            estructura.semantic_errors.append("Error: Operandos insuficientes para operación.")
            return

        value2, tipo2 = estructura.stack_operandos.pop()
        value1, tipo1 = estructura.stack_operandos.pop()
        op = p[2]

        if tipo1 is None or tipo2 is None:
            estructura.semantic_errors.append(f"Tipos de operando desconocidos: {tipo1}, {tipo2}")
            return

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))
        if resultado_tipo is None:
            estructura.semantic_errors.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")
            return

        temp_var, temp_address = estructura.new_temp(resultado_tipo)
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        # Get memory addresses
        val1_address = estructura.get_operand_address(value1)
        val2_address = estructura.get_operand_address(value2)

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, val1_address, val2_address, temp_address))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]

def p_termino(p):
    '''termino : termino OP_MUL factor
               | termino OP_DIV factor
               | factor'''
    if len(p) == 4:
        if len(estructura.stack_operandos) < 2:
            estructura.semantic_errors.append("Error: Operandos insuficientes para operación.")
            return

        value2, tipo2 = estructura.stack_operandos.pop()
        value1, tipo1 = estructura.stack_operandos.pop()
        op = p[2]

        if tipo1 is None or tipo2 is None:
            estructura.semantic_errors.append(f"Tipos desconocidos: {tipo1}, {tipo2}")
            return

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))
        if resultado_tipo is None:
            estructura.semantic_errors.append(f"No se puede hacer operacion de {tipo1} {op} {tipo2}")
            return

        temp_var, temp_address = estructura.new_temp(resultado_tipo)
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        # Get memory addresses
        val1_address = estructura.get_operand_address(value1)
        val2_address = estructura.get_operand_address(value2)

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, val1_address, val2_address, temp_address))

        p[0] = (temp_var, resultado_tipo)
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : LPAREN expresion RPAREN
              | OP_SUM varcte
              | OP_SUB varcte
              | varcte'''
    if len(p) == 4:  # Parentheses
        p[0] = p[2]
    elif len(p) == 3:  # Unary + or -
        if not estructura.stack_operandos:
            estructura.semantic_errors.append("Error: No hay operando para operación unaria.")
            return
            
        valor, tipo = estructura.stack_operandos.pop()
        
        if p[1] == '-':
            # Generate unary minus quadruple
            temp_var, temp_address = estructura.new_temp(tipo)
            valor_address = estructura.get_operand_address(valor)
            estructura.linea += 1
            estructura.cuadruplos.append((estructura.linea, 'UMINUS', valor_address, -1, temp_address))
            estructura.stack_operandos.append((temp_var, tipo))
            p[0] = ('factor', [p[1], p[2]])
        else:  # Unary plus - no operation needed
            estructura.stack_operandos.append((valor, tipo))
            p[0] = ('factor', [p[2]])
    else:
        p[0] = p[1]

def p_varcte(p):
    '''varcte : ID
              | CTE_INT
              | CTE_FLOAT
              | CTE_STRING'''
    
    if p.slice[1].type == 'ID':
        var_name = p[1]
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
    elif p.slice[1].type == 'CTE_STRING':
        estructura.stack_operandos.append((p[1], 'string')) 
        p[0] =  ('varcte', [('CTE_STRING', p[1])])

def p_empty(p):
    '''empty :'''
    p[0] = None

def p_error(p):
    global syntax_errors
    if p:
        msg = f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)
        print(f"PARSER ERROR: {msg}")  # Debug output
        parser.errok()
    else:
        msg = "Error de sintaxis: fin de archivo inesperado"
        syntax_errors.append(msg)
        print(f"PARSER ERROR: {msg}")  # Debug output

parser = yacc.yacc(debug=True)
syntax_errors = []