def convert_quadruples_to_test(cuads):
    # Memory address ranges
    constants_map = {}
    variable_map = {}
    
    # Counters for each memory type
    const_int_counter = 17000
    const_float_counter = 18000
    const_str_counter = 19000
    
    global_int_counter = 1000
    global_float_counter = 2000
    global_str_counter = 3000
    
    temp_int_counter = 12000
    temp_float_counter = 13000
    temp_bool_counter = 14000

    # First, analyze context to determine what should be constants vs variables
    print_operands = set()
    other_operands = set()
    
    for quad in cuads:
        if len(quad) >= 5:
            num, op, arg1, arg2, dest = quad[:5]
            
            if op.upper() == 'PRINT':
                # Anything in PRINT is likely a string constant
                if isinstance(arg1, str) and not arg1.startswith('t') and not arg1.isdigit():
                    print_operands.add(arg1)
            else:
                # Everything else are variables/identifiers
                for operand in [arg1, arg2, dest]:
                    if isinstance(operand, str) and not operand.startswith('t') and not operand.isdigit():
                        other_operands.add(operand)

    def get_address(name, context="operand"):
        nonlocal const_int_counter, const_float_counter, const_str_counter
        nonlocal global_int_counter, global_float_counter, global_str_counter
        nonlocal temp_int_counter, temp_float_counter, temp_bool_counter
        
        if name in (None, 'None', '-', -1):
            return -1
        
        # For jump destinations, return as-is
        if context == "jump":
            return str(name)
            
        # Handle constants
        if isinstance(name, int) or (isinstance(name, str) and name.isdigit()):
            const_key = str(name)
            if const_key not in constants_map:
                constants_map[const_key] = const_int_counter
                const_int_counter += 1
            return str(constants_map[const_key])
            
        if isinstance(name, float) or (isinstance(name, str) and '.' in name and name.replace('.', '').replace('-', '').isdigit()):
            const_key = str(name)
            if const_key not in constants_map:
                constants_map[const_key] = const_float_counter
                const_float_counter += 1
            return str(constants_map[const_key])
        
        # Handle strings based on context
        if isinstance(name, str):
            # String literals that appear in PRINT statements → constants
            if name in print_operands:
                if name not in constants_map:
                    constants_map[name] = const_str_counter
                    const_str_counter += 1
                return str(constants_map[name])
            
            # Everything else → variables
            if name not in variable_map:
                if name.startswith('t') and name[1:].isdigit():
                    # Temporary variables
                    variable_map[name] = temp_int_counter
                    temp_int_counter += 1
                elif name in ['n']:
                    # Global int variables (from symbol table)
                    variable_map[name] = global_int_counter
                    global_int_counter += 1
                elif name in ['a', 'b', 'i', 'j']:
                    # Global float variables (from symbol table)
                    variable_map[name] = global_float_counter
                    global_float_counter += 1
                elif name in ['s']:
                    # Global string variables (from symbol table)
                    variable_map[name] = global_str_counter
                    global_str_counter += 1
                else:
                    # Function names and other identifiers
                    variable_map[name] = global_str_counter
                    global_str_counter += 1
            
            return str(variable_map[name])
        
        return str(name)

    # First pass: collect all operands
    for quad in cuads:
        if len(quad) >= 5:
            num, op, arg1, arg2, dest = quad[:5]
            
            op_lower = op.lower()
            
            if op_lower in ['gotomain', 'goto', 'gotof', 'gotot']:
                # Process operands but not jump destinations
                if arg1 not in (None, 'None', '-', -1):
                    get_address(arg1, "operand")
                if arg2 not in (None, 'None', '-', -1):
                    get_address(arg2, "operand")
            else:
                # Regular operations
                if arg1 not in (None, 'None', '-', -1):
                    get_address(arg1, "operand")
                if arg2 not in (None, 'None', '-', -1):
                    get_address(arg2, "operand")
                if dest not in (None, 'None', '-', -1):
                    get_address(dest, "operand")

    # Count memory usage correctly
    memory_regions = {
        'global_int': global_int_counter - 1000,
        'global_float': global_float_counter - 2000,
        'global_str': global_str_counter - 3000,
        'global_void': 0,
        'local_int': 0,
        'local_float': 0,
        'local_str': 0,
        'temp_int': temp_int_counter - 12000,
        'temp_float': temp_float_counter - 13000,
        'temp_bool': temp_bool_counter - 14000,
        'cte_int': len([k for k in constants_map.keys() if k.replace('-', '').isdigit() and '.' not in k]),
        'cte_float': len([k for k in constants_map.keys() if '.' in k and k.replace('.', '').replace('-', '').isdigit()]),
        'cte_str': len([k for k in constants_map.keys() if not (k.replace('-', '').isdigit() and '.' not in k) and not ('.' in k and k.replace('.', '').replace('-', '').isdigit())])
    }

    # Generate output
    sections = []
    
    # Constants section
    if constants_map:
        constants_lines = []
        for const_val, addr in sorted(constants_map.items(), key=lambda x: x[1]):
            constants_lines.append(f"{const_val} {addr}")
        sections.append("\n".join(constants_lines))
    
    # Memory allocation section
    memory_lines = [f"{k} {v}" for k, v in memory_regions.items()]
    sections.append("\n".join(memory_lines))
    
    # Quadruples section
    cuad_lines = []
    for quad in cuads:
        if len(quad) >= 5:
            num, op, arg1, arg2, dest = quad[:5]
            
            op_name = op.lower()
            
            if op_name in ['gotomain', 'goto', 'gotof', 'gotot']:
                op1 = get_address(arg1, "operand") if arg1 not in (None, 'None', '-', -1) else -1
                op2 = get_address(arg2, "operand") if arg2 not in (None, 'None', '-', -1) else -1
                dst = get_address(dest, "jump")  # Keep line number as-is
            else:
                op1 = get_address(arg1, "operand") if arg1 not in (None, 'None', '-', -1) else -1
                op2 = get_address(arg2, "operand") if arg2 not in (None, 'None', '-', -1) else -1
                dst = get_address(dest, "operand") if dest not in (None, 'None', '-', -1) else -1
            
            cuad_lines.append(f"{num} {op_name} {op1} {op2} {dst}")
    
    sections.append("\n".join(cuad_lines))
    
    return "\n".join(sections)

class VirtualMachine:
    def __init__(self):
        # Memory allocation ranges matching your specification
        self.MEMORY_RANGES = {
            'global_int': (1000, 1999),
            'global_float': (2000, 2999),
            'global_str': (3000, 3999),
            'global_void': (4000, 6999),
            'local_int': (7000, 7999),
            'local_float': (8000, 8999),
            'local_str': (9000, 11999),
            'temp_int': (12000, 12999),
            'temp_float': (13000, 13999),
            'temp_bool': (14000, 16999),
            'cte_int': (17000, 17999),
            'cte_float': (18000, 18999),
            'cte_str': (19000, 19999)
        }
        
        # Virtual memory - the big array managed by the VM
        self.virtual_memory = {}
        
        # Memory allocation tracking
        self.memory_allocation = {
            'global_int': 0,
            'global_float': 0,
            'global_str': 0,
            'global_void': 0,
            'local_int': 0,
            'local_float': 0,
            'local_str': 0,
            'temp_int': 0,
            'temp_float': 0,
            'temp_bool': 0,
            'cte_int': 0,
            'cte_float': 0,
            'cte_str': 0,
        }
        
        # Execution tracking
        self.allocation_log = []
        
    def get_memory_type(self, address):
        """Determine memory type based on address range"""
        addr = int(address)
        for mem_type, (start, end) in self.MEMORY_RANGES.items():
            if start <= addr <= end:
                return mem_type
        return "unknown"
        
    def load_and_initialize_memory(self, quadruple_string):
        """Load intermediate representation and initialize virtual memory"""
        test_split = quadruple_string.strip().split('\n')
        section = 0
        
        print("=== LOADING WITH PROPER MEMORY ALLOCATION ===")
        
        for line in test_split:
            if line.strip() == "":
                section += 1
                continue

            parts = line.strip().split()

            if section == 0 and len(parts) == 2:  # Constants section
                try:
                    value, address = parts
                    address = int(address)
                    
                    # Load constants into their proper memory ranges
                    if 17000 <= address <= 17999:  # Integer constants
                        try:
                            const_value = int(value)
                        except:
                            const_value = value.strip('"').strip("'")
                        self.virtual_memory[str(address)] = const_value
                        print(f"Constant -> Memory[{address}] = {const_value}")
                        
                    elif 18000 <= address <= 18999:  # Float constants
                        const_value = float(value)
                        self.virtual_memory[str(address)] = const_value
                        print(f"Constant FLOAT -> Memory[{address}] = {const_value}")
                        
                    elif 19000 <= address <= 19999:  # String constants
                        const_value = value.strip('"').strip("'")
                        self.virtual_memory[str(address)] = const_value
                        print(f"Constant STRING -> Memory[{address}] = '{const_value}'")
                        
                except ValueError:
                    continue

            elif section == 1 and len(parts) == 2:  # Memory allocation section
                memory_type, count = parts
                self.memory_allocation[memory_type] = int(count)
                
        # Show memory allocation summary using your ranges
        print("\n=== MEMORY ALLOCATION BY RANGES ===")
        for mem_type, (start, end) in self.MEMORY_RANGES.items():
            count = self.memory_allocation.get(mem_type, 0)
            if count > 0:
                print(f"{mem_type}: {count} variables in range {start}-{end}")
        
        return test_split, section

    def get_memory_value(self, address_str):
        """Access virtual memory"""
        if address_str is None or address_str == '-1':
            return None
            
        if address_str in self.virtual_memory:
            return self.virtual_memory[address_str]
        else:
            # Initialize memory location if accessing for first time
            self.virtual_memory[address_str] = 0
            return 0
    
    def set_memory_value(self, address_str, value):
        """Set value in virtual memory"""
        if address_str is None or address_str == '-1':
            return
            
        self.virtual_memory[address_str] = value
        self.allocation_log.append((address_str, value))
        mem_type = self.get_memory_type(address_str)
        print(f"Memory[{address_str}] ({mem_type}) := {value}")


def test_interpreter(test_quadruples):
    """Execute quadruples using proper memory allocation"""
    
    # Create VM instance
    vm = VirtualMachine()
    
    # Load and initialize memory
    test_split, _ = vm.load_and_initialize_memory(test_quadruples)
    
    # Parse quadruples
    quadruples = []
    section = 0
    
    for line in test_split:
        if line.strip() == "":
            section += 1
            continue
            
        parts = line.strip().split()
        
        if section == 2 and len(parts) == 5:  # Quadruples section
            num, op, arg1, arg2, dest = parts
            quadruples.append((int(num), op, arg1, arg2, dest))

    print("\n=== EXECUTING QUADRUPLES ===")
    
    # Execute quadruples
    pc = 0
    max_iterations = 1000
    iteration = 0
    
    # Find starting point (gotomain)
    start_pc = 0
    for i, (num, op, arg1, arg2, dest) in enumerate(quadruples):
        if op == 'gotomain':
            start_pc = int(dest) - 1
            break
    
    pc = start_pc
    
    while pc < len(quadruples) and iteration < max_iterations:
        iteration += 1
        num, op, arg1, arg2, dest = quadruples[pc]
        
        print(f"PC={pc+1}: {op} {arg1} {arg2} {dest}")
        
        if op == 'gotomain':
            pc = int(dest) - 1
            continue
            
        elif op == '=':
            value = vm.get_memory_value(arg1)
            vm.set_memory_value(dest, value)
            
        elif op == '+':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 + val2)
            
        elif op == '-':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 - val2)
            
        elif op == '*':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 * val2)
            
        elif op == '/':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            result = val1 / val2 if val2 != 0 else 0
            vm.set_memory_value(dest, result)
            
        elif op == '>':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 > val2)
            
        elif op == '<':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 < val2)
            
        elif op == '>=':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 >= val2)
            
        elif op == '<=':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 <= val2)
            
        elif op == '==':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 == val2)
            
        elif op == '!=':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            vm.set_memory_value(dest, val1 != val2)
            
        elif op == 'gotof':
            condition = vm.get_memory_value(arg1)
            if not condition:
                pc = int(dest) - 1
                continue
                
        elif op == 'gotot':
            condition = vm.get_memory_value(arg1)
            if condition:
                pc = int(dest) - 1
                continue
                
        elif op == 'goto':
            pc = int(dest) - 1
            continue
            
        elif op == 'print':
            value = vm.get_memory_value(arg1)
            print(f"OUTPUT: {value}")
            
        elif op == 'println':
            print("OUTPUT: (newline)")
            
        else:
            print(f"Unknown operation: {op}")
        
        pc += 1
    
    # Show final memory state organized by ranges
    print(f"\n=== FINAL MEMORY STATE BY RANGES ===")
    for mem_type, (start, end) in sorted(vm.MEMORY_RANGES.items(), key=lambda x: x[1][0]):
        values_in_range = []
        for addr_str in vm.virtual_memory:
            try:
                addr = int(addr_str)
                if start <= addr <= end:
                    values_in_range.append((addr, vm.virtual_memory[addr_str]))
            except:
                continue
        
        if values_in_range:
            print(f"\n{mem_type} ({start}-{end}):")
            for addr, value in sorted(values_in_range):
                print(f"  [{addr}] = {value}")
    
    return vm.virtual_memory