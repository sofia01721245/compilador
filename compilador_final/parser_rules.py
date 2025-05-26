from lexer import PlyTokenizer
from semantic import estructura, get_operand_and_type
import ply.yacc as yacc
from lexer import tokens

def p_programa(p):
    'Programa : KEYWORD_PROGRAM ID SEMICOLON vars_opt funcs_opt KEYWORD_MAIN body KEYWORD_END SEMICOLON'
    p[0] = ('Programa', [p[2], p[4], p[5], p[7], 'end', ';'])

def p_vars_opt(p):
    '''vars_opt : vars_opt VARS
                | VARS
                | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_VARS(p):
    '''VARS : KEYWORD_VAR var_list SEMICOLON'''
    ids = p[2][1]['ids']
    var_type = p[2][1]['type'][1][0]

    for var_id in ids:
        if var_id in estructura.symbol_table:
            print(f"Error de semántica: Variable '{var_id}' ya declarada.")
        else:
            estructura.symbol_table[var_id] = var_type

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
    '''funcs_opt : FUNCS
                 | empty'''
    if p[1] is not None:
        p[0] = ('funcs_opt', [p[1]])
    else:
        p[0] = ('funcs_opt', [])

def p_FUNCS(p):
    'FUNCS : KEYWORD_VOID ID LPAREN parametros_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOLON'
    func_name = p[2]
    params = p[4]  # lista de parámetros (name + type)
    vars_decl = p[7]  # si tienes semántica para registrar variables
    body = p[8]

    if func_name in estructura.func_dir:
        raise Exception(f"Function '{func_name}' already declared.")

    # Registrar en el directorio de funciones
    estructura.func_dir[func_name] = {
        'type': 'void',
        'params': [(name, typ) for (name, typ) in params],
        'vars': {},  # aquí puedes poner variables locales
        'start_quad': None  # si luego haces cuádruplos, lo llenarás
    }

    # Cambiar el contexto de función actual
    global current_function, local_var_table
    current_function = func_name
    local_var_table = {}

    # Guardar parámetros en la tabla de variables local
    for param_name, param_type in params:
        local_var_table[param_name] = {
            'type': param_type,
            'scope': 'local',
            'kind': 'param'
        }

    estructura.func_dir[func_name]['vars'] = local_var_table.copy()

    p[0] = ('FUNCS', [func_name, params, vars_decl, body])

def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | empty'''
    p[0] = ('parametros_opt', [p[1]])

def p_parametros(p):
    '''parametros : ID COLON type param_list'''
    p[0] = ('parametros', [('ID', p[1]), p[3]] + p[4])

def p_param_list(p):
    '''param_list : COMMA ID COLON type param_list
                  | empty'''
    if len(p) == 6:
        p[0] = [('ID', p[2]), p[4]] + p[5]
    else:
        p[0] = []

def p_body(p):
    'body : LBRACE statement_list RBRACE'
    p[0] = ('body', [p[2]])

def p_statement_list(p):
    '''statement_list : statement_list statement
                       | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
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
    valor, tipo = estructura.stack_operandos.pop()

    var_name = p[1]
    if var_name not in estructura.symbol_table:
        estructura.semantic_errors.append(f"Error de semantica: Variable '{var_name}' no declarada.")
        return

    #Checar compatibilidad tipo
    tipo_variable = estructura.symbol_table[var_name]
    if tipo != tipo_variable:
        estructura.semantic_errors.append(f"Error de Mismatch: No se puede asignar tipo {tipo} a variable '{var_name}' de tipo {tipo_variable}.")
        return
    
    #añadir a cuadruplos y stack
    estructura.linea += 1
    estructura.cuadruplos.append((estructura.linea, '=', valor, None, var_name))
    estructura.stack_operandos.append((var_name, tipo_variable))

    p[0] = ('assign', [('ID', var_name), p[3]])

def p_print(p):
    'print : KEYWORD_PRINT LPAREN print_items RPAREN SEMICOLON'
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
    if isinstance(p[1], tuple):
        p[0] = ('print_item', [p[1]])
    else:
        p[0] = ('print_item', [('CTE_STRING', p[1])])

def p_cycle(p):
    'cycle : KEYWORD_DO body KEYWORD_WHILE LPAREN expresion RPAREN SEMICOLON'
    
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
    'condition : KEYWORD_IF LPAREN expresion RPAREN cuadr_if body else_arg SEMICOLON'
    if estructura.stack_saltos:
        salto_final_else = estructura.stack_saltos.pop()
        estructura.cuadruplos[salto_final_else] = (
            estructura.cuadruplos[salto_final_else][0],
            estructura.cuadruplos[salto_final_else][1],
            estructura.cuadruplos[salto_final_else][2],
            estructura.cuadruplos[salto_final_else][3],
            estructura.linea + 1
        )
    p[0] = ('condition', [p[1], p[3], p[6], p[7]])

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
    'else_arg : KEYWORD_ELSE cuadr_else body'
    p[0] = [p[1], p[3]]

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
            estructura.linea + 1  # Inicio del else
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
    args = p[3]  # lista de expresiones

    # verificar que exsiste la funcion
    if func_name not in estructura.func_dir:
        estructura.semantic_errors.append(f"Funcion '{func_name}' no esta declarada.")

    func_info = estructura.func_dir[func_name]
    expected_params = func_info['params']

    # validar cuantos argumentos se esperan
    if len(args) != len(expected_params):
        estructura.semantic_errors.append(f"Funcion '{func_name}' necesita {len(expected_params)} argumentos, pero recibió {len(args)}.")

    # validar tipos
    for i in range(len(expected_params)):
        param_name, expected_type = expected_params[i]
        arg = args[i]
        arg_type = arg['type']

        if arg_type != expected_type:
            estructura.semantic_errors.append(f"Error semantico de tipos en argumento {i+1} de la funcion '{func_name}'. Se esperaba '{expected_type}', y recibió '{arg_type}'.")

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
        left = p[1]
        op = p[2][1][0]  # p[2] = ('comparador', [<operator>])
        right = p[3]

        tipo1, value1 = get_operand_and_type(left)
        tipo2, value2 = get_operand_and_type(right)

        if tipo1 is None or tipo2 is None:
         estructura.semantic_errors.append(f"Unknown tipos: {tipo1}, {tipo2} — left={left}, right={right}")

        resultado_tipo = estructura.cubo.get((tipo1, tipo2, op))

        if resultado_tipo is None:
            estructura.semantic_errors.append(f"No se puede hacer operación de comparación {tipo1} {op} {tipo2}")

        temp_var = estructura.new_temp()
        estructura.stack_operandos.append((temp_var, resultado_tipo))

        estructura.linea += 1
        estructura.cuadruplos.append((estructura.linea, op, value1, value2, temp_var))

        p[0] = (temp_var, resultado_tipo)
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
    if len(p) == 4:
        p[0] = ('factor', [p[2]])
    elif len(p) == 3:
        p[0] = ('factor', [p[1], p[2]])
    else:
        p[0] = ('factor', [p[1]])

def p_varcte(p):
    '''varcte : ID
              | CTE_INT
              | CTE_FLOAT'''
    if p.slice[1].type == 'ID':
        p[0] = ('varcte', [('ID', p[1])])

        # Para semántica, el tipo se consulta en la tabla de símbolos
    elif p.slice[1].type == 'CTE_INT':
        estructura.stack_operandos.append([p[1], 'int'])
        p[0] = ('varcte', [('CTE_INT', p[1])])
    elif p.slice[1].type == 'CTE_FLOAT':
        estructura.stack_operandos.append([p[1], 'float'])
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
    'empty :'
    p[0] = ('empty', [])

def p_error(p):
    if p:
        # If the unexpected token is not a semicolon, maybe missing a semicolon before?
        msg = f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)

        # Skip tokens until next semicolon or EOF to try to recover
        while True:
            tok = parser.token()
            if not tok or tok.type == 'SEMICOLON':
                break
        parser.errok()
    else:
        syntax_errors.append("Error de sintaxis: fin de archivo inesperado")

parser = yacc.yacc(debug=True)
syntax_errors = []
