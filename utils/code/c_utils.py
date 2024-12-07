import regex as re

def find_functions(content: str):

    function_pattern = re.compile(
        r'\b((?:[a-zA-Z_]\w*\s*(?:\*+)?\s+)+' # match return types, allowing basic types, pointer types, and modifiers (e.g., const)
        r'(?:\*?\s*[a-zA-Z_]\w*)' # Match function names, allowing pointer modifiers
        r'\((?:[^)]*)\)\s*)' # match function argument list
        )
    return function_pattern.findall(content)


def find_include(content: str):
    include_pattern = re.compile(
        r'^\s*#\s*include\s+["<][^">]+[">]',
        re.MULTILINE
    )
    return include_pattern.findall(content)


def find_classes(content: str):
    class_pattern = re.compile(
        r'^\s*class\s+\w+\s*(:[^{]*)?\{',
        re.MULTILINE
    )
    return class_pattern.findall(content)


def find_simple_variables(content:str):
    class_pattern = re.compile(
        r'^\s*(?:unsigned\s+)?(?:int|float|double|char|bool|std::string|auto)\s+\w+\s*;',
        re.MULTILINE
    )
    return class_pattern.findall(content)


def find_simple_returns(content: str):
    simple_return_pattern = re.compile(
        r'^\s*return\s*(?:(\w+|\d+|\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\'|true|false|nullptr)\s*)?;\s*$',
        re.MULTILINE
    )
    return simple_return_pattern.findall(content)


def find_variables(content:str):

    variable_pattern = re.compile(
        r'\b((?:\w+(?:\s+\w+)?)\s+'                         # Match type names, including struct, class, and typedef type names (can include multiple words, such as unsigned int)
        r'(?:(?:\*+)?\s*'                                   # match pointer symbols (can be multiple '*')
        r'[\w\[\]]+'                                        # match variable names and their possible array declaration parts
        r'\s*(?:=\s*[^;]*)?'                                # match the possible assignment part (including the equals sign and the initial value)
        r'(?:,\s*(?:\*+)?\s*[\w\[\]]+\s*(?:=\s*[^;]*)?)*)'  # match multiple variable definitions, allowing multiple variables to be separated by commas
        r'\s*;)'                                            # match ';'
    )
    return variable_pattern.findall(content)
