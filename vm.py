def convert_quadruples_to_test(cuads):
    # Memory address ranges for different types
    CONST_INT_START = 17000
    CONST_FLOAT_START = 17100
    CONST_STR_START = 17200
    
    # Track constants and their addresses
    constants_map = {}
    const_int_counter = CONST_INT_START
    const_float_counter = CONST_FLOAT_START
    const_str_counter = CONST_STR_START
    
    memory_map = {}
    next_address = 1000

    def get_addr(name):
        nonlocal next_address, const_int_counter, const_float_counter, const_str_counter
        
        if name in (None, 'None', '-', -1):
            return -1
            
        # Handle integer literals - assign them to constants section
        if isinstance(name, int) or (isinstance(name, str) and name.isdigit()):
            const_key = str(name)
            if const_key not in constants_map:
                constants_map[const_key] = const_int_counter
                const_int_counter += 1
            return str(constants_map[const_key])
            
        if isinstance(name, float) or (isinstance(name, str) and '.' in name and name.replace('.', '').isdigit()):
            const_key = str(name)
            if const_key not in constants_map:
                constants_map[const_key] = const_float_counter
                const_float_counter += 1
            return str(constants_map[const_key])
        
        # para temps
        if name not in memory_map:
            memory_map[name] = next_address
            next_address += 1
        return str(memory_map[name])

    for quad in cuads:
        if len(quad) == 6:
            num, op, arg1, arg2, dest, type_info = quad
        else:
            num, op, arg1, arg2, dest = quad
        
        get_addr(arg1)
        get_addr(arg2)
        get_addr(dest)

    memory_regions = {
        'global_int': 2,
        'global_float': 1,
        'global_str': 0,
        'global_void': 0,
        'local_int': 0,
        'local_float': 0,
        'local_str': 0,
        'temp_int': 0,
        'temp_float': 2,
        'temp_bool': 0,
        'cte_int': len([k for k in constants_map.keys() if '.' not in k]),  # Count integer constants
        'cte_float': len([k for k in constants_map.keys() if '.' in k]),    # Count float constants
        'cte_str': 0,
    }

    constants_lines = []
    for const_val, addr in sorted(constants_map.items(), key=lambda x: x[1]):
        constants_lines.append(f"{const_val} {addr}")

    memory_lines = [f"{k} {v}" for k, v in memory_regions.items()]

    cuad_lines = []
    for quad in cuads:
        if len(quad) == 6:
            num, op, arg1, arg2, dest, type_info = quad
        else:
            num, op, arg1, arg2, dest = quad
        
        op_name = op.lower() # estandarizar
        
        op1 = get_addr(arg1)
        op2 = get_addr(arg2)
        dst = get_addr(dest)
        
        cuad_lines.append(f"{num} {op_name} {op1} {op2} {dst}")

    sections = []
    
    if constants_lines:
        sections.append("\n".join(constants_lines))
    
    sections.append("\n".join(memory_lines))
    sections.append("\n".join(cuad_lines))
    
    return "\n".join(sections)

"""ejemplo 
7 17000
3 17001
2 17002
global_int 2
global_float 1
global_str 0
global_void 0
local_int 0
local_float 0
local_str 0
temp_int 0
temp_float 2
temp_bool 0
cte_int 3
cte_float 0
cte_str 0
1 gotomain -1 -1 2
2 = 17000 -1 1000
3 = 17001 -1 1001
4 / 1000 1001 13000
5 + 13000 17002 13001
6 = 13001 -1 2001
7 print 2001 -1 -1
8 println -1 -1 -1
9 print 2001 -1 -1
10 print 2001 -1 -1
11 println -1 -1 -1
12 print 17001 -1 -1
13 println -1 -1 -1
"""

class Cuadruplo:
    def __init__(self, data):
        if len(data) == 5:
            self.numero = data[0]
            self.operador = data[1]
            self.argIzq = data[2]
            self.argDer = data[3]
            self.destino = data[4]
        else:
            # Handle dummy cuadruplo or other formats
            self.numero = -1
            self.operador = ""
            self.argIzq = -1
            self.argDer = -1
            self.destino = -1

def execute_quadruples(quadruple_string):
    test_split = quadruple_string.strip().split('\n')
    memo = {}
    cuads = [Cuadruplo([-1, -1, -1, -1, -1])]
    section = 0
    allocation_log = []  
    for l in test_split:
        if l.strip() == "":
            section += 1
            continue

        linea = l.strip().split()

        if section == 0 and len(linea) == 2:
            try:
                dir = int(linea[1])
                if dir < 18000:
                    memo[linea[1]] = int(linea[0])
                elif dir < 19000:
                    memo[linea[1]] = float(linea[0])
                else:
                    memo[linea[1]] = linea[0]
            except ValueError:
                continue

        elif section == 1 and len(linea) == 2:
            continue

        elif section == 2 and len(linea) == 5:
            cuads.append(Cuadruplo(linea))

    indx = 1
    while indx < len(cuads):
        quad = cuads[indx]
        op = quad.operador
        dst = str(quad.destino)

        def log(value):
            if dst != '-1':
                allocation_log.append((dst, value))
                memo[dst] = value

        if op == 'gotomain':
            indx = int(quad.destino)
        elif op == '=':
            log(memo[str(quad.argIzq)])
            indx += 1
        elif op == '/':
            log(memo[str(quad.argIzq)] / memo[str(quad.argDer)])
            indx += 1
        elif op == '+':
            log(memo[str(quad.argIzq)] + memo[str(quad.argDer)])
            indx += 1
        elif op == '*':
            log(memo[str(quad.argIzq)] * memo[str(quad.argDer)])
            indx += 1
        elif op == '-':
            log(memo[str(quad.argIzq)] - memo[str(quad.argDer)])
            indx += 1
        elif op == '>':
            log(memo[str(quad.argIzq)] > memo[str(quad.argDer)])
            indx += 1
        elif op == '<':
            log(memo[str(quad.argIzq)] < memo[str(quad.argDer)])
            indx += 1
        elif op == '>=':
            log(memo[str(quad.argIzq)] >= memo[str(quad.argDer)])
            indx += 1
        elif op == '<=':
            log(memo[str(quad.argIzq)] <= memo[str(quad.argDer)])
            indx += 1
        elif op == '==':
            log(memo[str(quad.argIzq)] == memo[str(quad.argDer)])
            indx += 1
        elif op == '!=':
            log(memo[str(quad.argIzq)] != memo[str(quad.argDer)])
            indx += 1
        elif op == 'gotof':
            if not memo[str(quad.argIzq)]:
                indx = int(quad.destino)
            else:
                indx += 1
        elif op == 'goto':
            indx = int(quad.destino)
        elif op == 'print':
            print(memo[str(quad.argIzq)], end=" ")
            indx += 1
        elif op == 'println':
            print()
            indx += 1
        else:
            print(f"Unknown operation: {op}")
            indx += 1

    return memo, allocation_log

def test_interpreter(test_quadruples):    
    final_memory, allocations = execute_quadruples(test_quadruples)
    
    print(f"\nFinal memory state: {final_memory}")
    print("\nMemory allocations during execution:")
    for addr, value in allocations:
        print(f"Address {addr} := {value}")
