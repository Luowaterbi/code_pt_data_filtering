import esprima

from document import QSCodeDocument


def parse_js(content: str):
    # parse in module mode
    try:
        if 'import' in content or 'export' in content:
            try:
                return esprima.parseModule(content)
            except TimeoutError:
                raise TimeoutError("timeout")
            except esprima.Error as e:
                # parse fail, try to parse in script mode
                return esprima.parseScript(content)
        else:
            # parse in script mode
            return esprima.parseScript(content)
    except TimeoutError:
        raise TimeoutError("timeout")
    except esprima.Error as e:
        return None

def traverse(node, walk_func):
    for key, value in vars(node).items():
        if isinstance(value, esprima.nodes.Node):
            walk_func(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, esprima.nodes.Node):
                    walk_func(item)

def find_variables(code: QSCodeDocument):
    variables = []

    def walk(node):
    # check variable declaration
        if node.type == 'VariableDeclaration':
            for declarator in node.declarations:
                if declarator and declarator.id.name and not isinstance(declarator.init, esprima.nodes.FunctionExpression):
                    variables.append(declarator.id.name)
        # check module.exports.xxx
        elif node.type == 'AssignmentExpression':
            if (node.left.type == 'MemberExpression' and
                node.left.object.type == 'MemberExpression' and
                node.left.object.object.name == 'module' and
                node.left.object.property.name == 'exports'):
                exported_name = node.left.property.name
                if exported_name and node.right.type != 'FunctionExpression' and node.right.type != 'ArrowFunctionExpression':
                    variables.append(exported_name)
        
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)

    return variables

def find_simple_variables(code: QSCodeDocument):
    simple_variables = []

    def walk(node):
        if node.type == 'VariableDeclaration':
            for declarator in node.declarations:
                # check simple variable declaration (not function)
                if declarator and not isinstance(declarator.init, esprima.nodes.FunctionExpression) and (declarator.init == None or declarator.init.type in ['Literal', 'Identifier', 'UnaryExpression']):
                    simple_variables.append(declarator.id.name)
        
        elif node.type == 'AssignmentExpression':
            if (node.left.type == 'MemberExpression' and
                node.left.object.type == 'MemberExpression' and
                node.left.object.object.name == 'module' and
                node.left.object.property.name == 'exports'):
                exported_name = node.left.property.name
                if exported_name and node.right.type != 'FunctionExpression' and node.right.type != 'ArrowFunctionExpression' and \
                    (node.right.type in ['Literal', 'Identifier', 'UnaryExpression']):
                    simple_variables.append(exported_name)
        
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)

    return simple_variables

def find_functions(code: QSCodeDocument):
    functions = []

    def walk(node):
        # check function declaration
        if node.type == 'VariableDeclaration':
            for declarator in node.declarations:
                if (isinstance(declarator.init, esprima.nodes.FunctionExpression) and 
                    declarator.id and declarator.id.name):
                    functions.append(declarator.id.name)
        elif node.type == 'FunctionDeclaration':
            if node.id and node.id.name:
                functions.append(node.id.name)
        # check module.exports.xxx
        elif node.type == 'AssignmentExpression':
            if (node.left.type == 'MemberExpression' and
                node.left.object.type == 'MemberExpression' and
                node.left.object.object.name == 'module' and
                node.left.object.property.name == 'exports'):
                exported_name = node.left.property.name
                if exported_name and (node.right.type == 'FunctionExpression' or node.right.type == 'ArrowFunctionExpression'):
                    functions.append(exported_name)
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)

    return functions

def find_classes(code: QSCodeDocument):
    classes = []

    def walk(node):
    # check class declaration
        if isinstance(node, esprima.nodes.ClassDeclaration):
            if node.id and node.id.name:
                classes.append(node.id.name)
        
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)

    return classes

def find_simple_returns(code: QSCodeDocument):
    simple_returns = []

    def walk(node):
        if node.type == 'ReturnStatement':
            # check if the return statement is simple(variable, literal, unary expression, undefined, etc.)
            if node.argument == None or node.argument.type in ['Literal', 'Identifier', 'UnaryExpression']:
                simple_returns.append(node)
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)
    
    return simple_returns


def find_imports(code: QSCodeDocument):
    imports = []
    
    def walk(node):
        if node.type == 'ImportDeclaration':
            imports.append(node)
        
        # traverse the AST
        traverse(node, walk_func=walk)

    walk(code.ast)

    return imports
