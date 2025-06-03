# Virtual Machine for your compiler
# Import your existing modules
from semantic import estructura

class VirtualMachine:
    def __init__(self, estructura_obj):
        self.estructura = estructura_obj
        self.memo = {}
        self.call_stack = []  # For function calls
        self.current_scope = 'global'
        
    def get_value(self, key):
        """Get value from memory, handling different data types"""
        if key is None or key == "None":
            return None
            
        if isinstance(key, str):
            # First check if it's in memory (variable)
            if key in self.memo:
                return self.memo[key]
            # Check if it's a numeric literal
            elif key.lstrip('-').isdigit():
                return int(key)
            elif self.is_float_string(key):
                return float(key)
            # Check if it's a string literal (enclosed in quotes or unquoted string)
            elif key.startswith('"') and key.endswith('"'):
                return key[1:-1]  # Remove quotes
            else:
                # It's either a string literal or unknown variable
                return key
        return key
    
    def is_float_string(self, s):
        """Check if string represents a float"""
        try:
            float(s)
            return '.' in s or 'e' in s.lower()
        except ValueError:
            return False
    
    def set_value(self, key, value):
        """Set value in memory"""
        if key is not None and key != "None":
            self.memo[str(key)] = value
    
    def initialize_memory(self):
        """Initialize memory from symbol table"""
        print("=== INITIALIZING VIRTUAL MACHINE ===")
        
        # Initialize global variables
        print("Global variables:")
        for name, var in self.estructura.func_directory.global_var_table.variables.items():
            if var.tipo == 'int':
                self.memo[name] = 0
            elif var.tipo == 'float':
                self.memo[name] = 0.0
            elif var.tipo == 'string':
                self.memo[name] = ""
            elif var.tipo == 'bool':
                self.memo[name] = False
            print(f"  {name}: {self.memo[name]} ({var.tipo})")
        
        # Store function start addresses
        print("\nFunction addresses:")
        for func_name, func in self.estructura.func_directory.functions.items():
            self.memo[func_name] = func.start_quad
            print(f"  {func_name}: starts at quadruple {func.start_quad}")
    
    def find_quadruple_index(self, line_number):
        """Find the index of a quadruple with given line number"""
        for i, quad in enumerate(self.estructura.cuadruplos):
            if len(quad) >= 1 and str(quad[0]) == str(line_number):
                return i
        return -1
    
    def execute(self):
        """Execute the quadruples"""
        self.initialize_memory()
        
        print("\n=== STARTING EXECUTION ===")
        cuadruplos = self.estructura.cuadruplos
        
        if not cuadruplos:
            print("No quadruples to execute!")
            return
        
        indx = 0
        execution_count = 0
        max_executions = 1000  # Prevent infinite loops during debugging
        
        while indx < len(cuadruplos) and execution_count < max_executions:
            execution_count += 1
            quad = cuadruplos[indx]
            
            # Handle both 5 and 6 element tuples
            if len(quad) == 6:
                num, op, arg1, arg2, res, type_info = quad
            elif len(quad) == 5: 
                num, op, arg1, arg2, res = quad
                type_info = "-"
            else:
                indx += 1
                continue
            
            print(f"Executing quad {num}: {op} {arg1} {arg2} -> {res}")
            
            if op == 'gotomain':
                target_line = res
                target_index = self.find_quadruple_index(target_line)
                if target_index != -1:
                    indx = target_index
                    continue
                else:
                    print(f"Warning: Could not find quadruple {target_line}")
                    indx += 1
                    
            elif op == '=':
                left_val = self.get_value(arg1)
                self.set_value(res, left_val)
                print(f"  Assigned {left_val} to {res}")
                
            elif op in ['+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=']:
                left_val = self.get_value(arg1)
                right_val = self.get_value(arg2)
                
                if op == '+':
                    result = left_val + right_val
                elif op == '-':
                    result = left_val - right_val
                elif op == '*':
                    result = left_val * right_val
                elif op == '/':
                    if right_val != 0:
                        result = left_val / right_val
                    else:
                        print("Error: Division by zero!")
                        result = 0
                elif op == '>':
                    result = left_val > right_val
                elif op == '<':
                    result = left_val < right_val
                elif op == '>=':
                    result = left_val >= right_val
                elif op == '<=':
                    result = left_val <= right_val
                elif op == '==':
                    result = left_val == right_val
                elif op == '!=':
                    result = left_val != right_val
                
                self.set_value(res, result)
                print(f"  {left_val} {op} {right_val} = {result}")
                
            elif op == 'PRINT' or op == 'print':
                value = self.get_value(arg1)
                print(f"OUTPUT: {value}", end=" ")
                
            elif op == 'println':
                print()  # New line
                
            elif op == 'GOTO':
                if arg1 and arg1 != "None":
                    target = self.get_value(arg1)
                    target_index = self.find_quadruple_index(target)
                else:
                    target_index = self.find_quadruple_index(res)
                
                if target_index != -1:
                    indx = target_index
                    continue
                else:
                    print(f"Warning: Could not find target quadruple")
                    
            elif op == 'GOTOF':
                condition = self.get_value(arg1)
                if not condition:  # If condition is false
                    target_index = self.find_quadruple_index(res)
                    if target_index != -1:
                        indx = target_index
                        continue
                        
            elif op == 'GOTOT':
                condition = self.get_value(arg1)
                if condition:  # If condition is true
                    target_index = self.find_quadruple_index(res)
                    if target_index != -1:
                        indx = target_index
                        continue
            else:
                print(f"  Unknown operation: {op}")
            
            indx += 1
        
        if execution_count >= max_executions:
            print(f"\nExecution stopped after {max_executions} steps (possible infinite loop)")
        
        print(f"\n=== EXECUTION COMPLETED ({execution_count} steps) ===")
        self.print_final_state()
    
    def print_final_state(self):
        """Print final memory state"""
        print("\nFinal memory state:")
        for key, value in self.memo.items():
            if not key.startswith('t'):  # Don't show temporary variables
                print(f"  {key}: {value}")

# To use this VM with your main code, add this at the end of your main:
def run_virtual_machine():
    if not estructura.semantic_errors:
        print("\n" + "="*50)
        print("RUNNING VIRTUAL MACHINE")
        print("="*50)
        
        vm = VirtualMachine(estructura)
        vm.execute()
    else:
        print("\nCannot run VM due to semantic errors.")

# Uncomment this line in your main to run the VM:
# run_virtual_machine()