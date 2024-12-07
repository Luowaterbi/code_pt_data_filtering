import regex as re

def find_imports(content: str):
    import_lines = []
    lines = content.split('\n')
    for line in lines:
        stripped_line = line.strip()
        in_multi_line_import = False

        # check if it is a single-line import statement.
        if re.match(r'^import\s+"[^"]+"$', stripped_line):
            import_lines.append(line)
        # check if it is a start of a multi-line import statement.
        elif stripped_line == 'import (':
            in_multi_line_import = True
            import_lines.append(line)
        # check if it is within a multi-line import statement.
        elif in_multi_line_import:
            if stripped_line == ')':
                in_multi_line_import = False
            import_lines.append(line)
    return import_lines


def find_functions(content: str):

    function_pattern = re.compile(
    r'(^func\s+'                          # match keyword 'func' 
    r'(?:\(\s*\w+\s+\*?\w+\s*\))?\s*'     # match the optional receiver parameter.
    r'(?:\w+)\s*'                         # match function name
    r'\((?:[^)]*)\)\s*'                   # match function argument list
    r'(?:\([^)]+\)|[\w\[\]]+)?\s*)'       # match return value (optional)
    , re.MULTILINE)
    return function_pattern.findall(content)


def find_classes(content: str):
    class_pattern = re.compile(
        r'^\s*type\s+\w+\s+(struct|interface)\s*\{[^}]*\}',
        re.MULTILINE | re.DOTALL
    )
    return class_pattern.findall(content)


def find_simple_returns(content:str):
    return_pattern = re.compile(
            r'^\s*return(?:\s+[^;\n]+)?\s*;?\s*$',
            re.MULTILINE
        )
    return return_pattern.findall(content)


def find_variables(content: str):

    variable_pattern = re.compile(
        r'^\s*((?:var|const)\s+\w+(?:,\s*\w+)*\s+[\w\[\]\*]+'                   # match variable definitions using var/const.
        r'|(?:var|const)\s+\w+(?:,\s*\w+)*(?:\s+[\w\[\]\*]+)?\s*=\s*[^;\n]+'    # match the initial value in variable definitions using var/const.
        r'|\w+(?:\s*,\s*\w+)*\s*:=\s*[^;\n]+'                                   # match direct variable assignments.
        r'|(?:var|const)\s+\(\s*(?:\w+\s+[\w\*\[\]]+\s*)+\))'                   # match multi-line variable definitions enclosed in parentheses
        ,re.MULTILINE
    )
    return variable_pattern.findall(content)


def find_simple_variables(content:str):
    simple_variables = re.compile(
        r'^\s*var\s+(\w+)\s+(\w+)\s*;?\s*$',
        re.MULTILINE
    )
    return simple_variables.findall(content)