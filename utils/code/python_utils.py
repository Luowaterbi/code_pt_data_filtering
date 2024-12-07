import ast,re
from document import QSCodeDocument

def parse_py(content):
    try:
        tree = ast.parse(content)
    except TimeoutError:
        raise TimeoutError("timeout")
    except:
        tree = None
    return tree


def find_variables(code: QSCodeDocument):
    variables = set()
    class VariableVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            # Assign 
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.add(target.id)

        def visit_For(self, node):
            # For
            if isinstance(node.target, ast.Name):
                variables.add(node.target.id)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            # Func def
            for arg in node.args.args:
                variables.add(arg.arg)
            self.generic_visit(node)
    
    visitor = VariableVisitor()
    visitor.visit(code.ast)
    return list(variables)


def find_functions(code: QSCodeDocument):
    functions = []
    class FunctionVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            # when visist the function definition node, add the function name to the list
            functions.append(node.name)
            # continue to visit the child nodes
            self.generic_visit(node)

    visitor = FunctionVisitor()
    visitor.visit(code.ast)
    return functions


def find_import(code: QSCodeDocument):
    import_lines = [line for line in code.code_normalized_lines if line.text.strip().lower().count('import')!=0 ]
    return import_lines

def find_class(code: QSCodeDocument):
    classes = []
    class ClassCounter(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            classes.append(node.name)
            self.generic_visit(node)

    visitor = ClassCounter()
    visitor.visit(code.ast)
    return classes

def find_simple_return(code: QSCodeDocument):
    pattern = re.compile(r'^\s*return(\s+.+)?\s*$', re.MULTILINE)
    return pattern.findall(code.code_raw_content)

def find_simple_variable(code: QSCodeDocument):
    simple_vars = []
    class ClassMemberFinder(ast.NodeVisitor):
        def visit_ClassDef(self, node):
            for item in node.body:
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                simple_vars.append(target)
                    elif isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name):
                            simple_vars.append(item)   
    
    visitor = ClassMemberFinder()
    visitor.visit(code.ast)

    return simple_vars