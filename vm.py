def convert_quadruples_to_test(cuads):
    # Memory address ranges
    constants_map = {}
    
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

    def get_address(operand, context="operand"):
        if operand in (None, 'None', '-', -1):
            return -1
        
        # For jump destinations, return as-is
        if context == "jump":
            return str(operand)
        
        # If it's already an address, return it
        if isinstance(operand, int) and 1000 <= operand <= 19999:
            return str(operand)
        
        return str(operand)

    # Memory allocation tracking
    memory_regions = {
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
        'cte_str': 0
    }

    # Count memory usage from semantic analysis
    from semantic import estructura
    mm = estructura.func_directory.memory_manager
    
    for mem_type, counter in mm.counters.items():
        start_addr = mm.MEMORY_RANGES[mem_type][0]
        used = counter - start_addr
        memory_regions[mem_type] = used

    # Generate output sections
    sections = []
    
    # Constants section
    if mm.constants:
        constants_lines = []
        for const_val, addr in sorted(mm.constants.items(), key=lambda x: x[1]):
            constants_lines.append(f"{const_val} {addr}")
        sections.append("\n".join(constants_lines))
    else:
        sections.append("")  # Empty constants section
    
    # Memory allocation section
    memory_lines = [f"{k} {v}" for k, v in memory_regions.items()]
    sections.append("\n".join(memory_lines))
    
    # Quadruples section
    cuad_lines = []
    for quad in cuads:
        if len(quad) >= 5:
            num, op, arg1, arg2, dest = quad[:5]
            
            op_name = op.lower()
            
            if op_name in ['gotomain', 'goto', 'gotof', 'gotot', 'gosub']:
                op1 = get_address(arg1, "operand") if arg1 not in (None, 'None', '-', -1) else -1
                op2 = get_address(arg2, "operand") if arg2 not in (None, 'None', '-', -1) else -1
                dst = get_address(dest, "jump")
            else:
                op1 = get_address(arg1, "operand") if arg1 not in (None, 'None', '-', -1) else -1
                op2 = get_address(arg2, "operand") if arg2 not in (None, 'None', '-', -1) else -1
                dst = get_address(dest, "operand") if dest not in (None, 'None', '-', -1) else -1
            
            cuad_lines.append(f"{num} {op_name} {op1} {op2} {dst}")
    
    sections.append("\n".join(cuad_lines))
    
    return "\n".join(sections)

class VirtualMachine:
    def __init__(self):
        # Memory allocation ranges
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
        
        # Virtual memory
        self.virtual_memory = {}
        
        # Function call stack for handling recursion
        self.call_stack = []
        self.local_memory_stack = []
        
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
        
    def get_memory_type(self, address):
        """Determine memory type based on address range"""
        if isinstance(address, str):
            try:
                addr = int(address)
            except:
                return "temp"  # Assume temp variables for non-numeric addresses
        else:
            addr = address
            
        for mem_type, (start, end) in self.MEMORY_RANGES.items():
            if start <= addr <= end:
                return mem_type
        return "unknown"
    
    def push_local_context(self, func_name):
        """Push new local memory context for function call"""
        # Save current local memory state
        local_snapshot = {}
        for addr_str, value in self.virtual_memory.items():
            if addr_str.isdigit():
                addr = int(addr_str)
                if 7000 <= addr <= 11999:  # Local memory range
                    local_snapshot[addr_str] = value
        
        self.local_memory_stack.append(local_snapshot)
        
        # Clear local memory for new function
        to_remove = []
        for addr_str in self.virtual_memory:
            if addr_str.isdigit():
                addr = int(addr_str)
                if 7000 <= addr <= 11999:
                    to_remove.append(addr_str)
        
        for addr_str in to_remove:
            del self.virtual_memory[addr_str]
            
        print(f"Pushed local context for {func_name}")
    
    def pop_local_context(self):
        """Restore previous local memory context"""
        if self.local_memory_stack:
            local_snapshot = self.local_memory_stack.pop()
            
            # Clear current local memory
            to_remove = []
            for addr_str in self.virtual_memory:
                if addr_str.isdigit():
                    addr = int(addr_str)
                    if 7000 <= addr <= 11999:
                        to_remove.append(addr_str)
            
            for addr_str in to_remove:
                del self.virtual_memory[addr_str]
            
            # Restore previous local memory
            for addr_str, value in local_snapshot.items():
                self.virtual_memory[addr_str] = value
                
            print("Popped local context")
        
    def load_and_initialize_memory(self, quadruple_string):
        """Load intermediate representation and initialize virtual memory"""
        test_split = quadruple_string.strip().split('\n')
        section = 0
        
        print("=== LOADING MEMORY ===")
        
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
                        print(f"Constant INT -> Memory[{address}] = {const_value}")
                        
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
        
        return test_split, section

    def get_memory_value(self, address_str):
        """Access virtual memory with proper handling for temp variables"""
        if address_str is None or address_str == '-1':
            return None
        
        # Handle temporary variable names like 't1', 't2', etc.
        if isinstance(address_str, str) and address_str.startswith('t') and address_str[1:].isdigit():
            # Map temp variable to its memory address
            temp_num = int(address_str[1:])
            temp_address = str(12000 + temp_num - 1)  # Map t1->12000, t2->12001, etc.
            if temp_address in self.virtual_memory:
                return self.virtual_memory[temp_address]
            else:
                self.virtual_memory[temp_address] = 0
                return 0
            
        if str(address_str) in self.virtual_memory:
            return self.virtual_memory[str(address_str)]
        else:
            # Initialize memory location if accessing for first time
            self.virtual_memory[str(address_str)] = 0
            return 0
    
    def set_memory_value(self, address_str, value):
        """Set value in virtual memory with proper handling for temp variables"""
        if address_str is None or address_str == '-1':
            return
        
        # Handle temporary variable names
        if isinstance(address_str, str) and address_str.startswith('t') and address_str[1:].isdigit():
            temp_num = int(address_str[1:])
            temp_address = str(12000 + temp_num - 1)
            self.virtual_memory[temp_address] = value
            mem_type = self.get_memory_type(temp_address)
            print(f"Memory[{temp_address}] ({mem_type}) := {value}")
            return
            
        self.virtual_memory[str(address_str)] = value
        mem_type = self.get_memory_type(address_str)
        print(f"Memory[{address_str}] ({mem_type}) := {value}")


def test_interpreter(test_quadruples):
    """Execute quadruples using proper memory allocation and function calls"""
    
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

    print("")
    for i, quad in enumerate(quadruples):
        print(f"  {i}: {quad}")
    
    print(f"")
    print(f"Total quads: {len(quadruples)}")
    
    # Find starting point (gotomain)
    start_pc = 0
    for i, (num, op, arg1, arg2, dest) in enumerate(quadruples):
        if op == 'gotomain':
            start_pc = int(dest) - 1
            break
    
    
    # Execute quadruples
    pc = start_pc
    max_iterations = 1000
    iteration = 0
    
    while pc < len(quadruples) and iteration < max_iterations:
        iteration += 1
        if pc < 0 or pc >= len(quadruples):
            print(f"Error: PC out of bounds: {pc}")
            break
            
        num, op, arg1, arg2, dest = quadruples[pc]
        
        print(f"PC={pc+1}: {op} {arg1} {arg2} {dest}")
        
        if op == 'gotomain':
            new_pc = int(dest) - 1
            if 0 <= new_pc < len(quadruples):
                print(f"Jumping to main at PC={new_pc+1}")
                pc = new_pc
                continue
            else:
                print(f"Error: Invalid jump destination {dest}")
                break
            
        elif op == 'int_to_float':
            # Convert integer to float
            int_val = vm.get_memory_value(arg1)
            float_val = float(int_val)
            vm.set_memory_value(dest, float_val)
            
        elif op == '=':
            value = vm.get_memory_value(arg1)
            vm.set_memory_value(dest, value)
            
        elif op == '+':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            result = val1 + val2
            vm.set_memory_value(dest, result)
            
        elif op == '-':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            result = val1 - val2
            vm.set_memory_value(dest, result)
            
        elif op == '*':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            result = val1 * val2
            vm.set_memory_value(dest, result)
            
        elif op == '/':
            val1 = vm.get_memory_value(arg1)
            val2 = vm.get_memory_value(arg2)
            result = val1 / val2 if val2 != 0 else 0
            vm.set_memory_value(dest, result)
            
        elif op == 'uminus':
            val = vm.get_memory_value(arg1)
            vm.set_memory_value(dest, -val)
            
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
            
        elif op == 'era':
            # Allocate space for function call
            func_name = arg1
            vm.push_local_context(func_name)
            
        elif op == 'param':
            # Assign parameter value
            param_value = vm.get_memory_value(arg1)
            vm.set_memory_value(dest, param_value)
            
        elif op == 'gosub':
            # Function call
            func_name = arg1
            return_address = pc + 1
            vm.call_stack.append(return_address)
            pc = int(dest) - 1
            continue
            
        elif op == 'endfunc':
            # End of void function - return to caller
            if vm.call_stack:
                print(f"Void function ended naturally, returning to caller")
                return_address = vm.call_stack.pop()
                vm.pop_local_context()
                pc = return_address
                continue
            else:
                print("Warning: ENDFUNC without call stack")
        
        elif op == 'return':
            # Explicit return (shouldn't happen in void functions, but handle it)
            if vm.call_stack:
                return_address = vm.call_stack.pop()
                vm.pop_local_context()
                pc = return_address
                continue
            else:
                print("Program ended with RETURN")
                break
            
        elif op == 'print':
            value = vm.get_memory_value(arg1)
            print(f"OUTPUT: {value}")
            
        elif op == 'end':
            print("Program ended normally")
            break
            
        else:
            print(f"Unknown operation: {op}")
        
        pc += 1
    
    # Show final memory state organized by ranges
    print(f"\n===  Memoria estado final===")
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