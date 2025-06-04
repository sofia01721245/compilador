def print_tree(node, indent="", last=True):
    branch = "└── " if last else "├── "
    
    # Si es un terminal 
    if isinstance(node, (str, int, float)):
        print(indent + branch + str(node))
        return
    
    # Si es un no terminal
    if isinstance(node, tuple):
        label, children = node
        print(indent + branch + str(label))
        indent += "    " if last else "│   "
        if isinstance(children, list):
            for i, child in enumerate(children):
                print_tree(child, indent, i == len(children) - 1)
        else:
            print_tree(children, indent, True)
        return
    
    # Si es una lista
    if isinstance(node, list):
        for i, child in enumerate(node):
            print_tree(child, indent, i == len(node) - 1)
        return
    
    # Si llega algo inesperado, error
    print(indent + branch + f"<{type(node).__name__}> {node}")