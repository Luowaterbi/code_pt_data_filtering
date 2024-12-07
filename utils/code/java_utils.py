
import regex as re


def find_functions(content: str):
    function_pattern = re.compile(r'^\s*'
    r'((?:(?:public|protected|private|static)\s+)*'  # modifier and static
    r'(?:(?!\s*(?:public|private|protected|else|if)\s*)(?:<\w+>)?\s*\w+\s+)'  # return type(also include template and array), negative look ahead to exclude access modifier 'if' and 'else'
    r'(?:\w+\s*)'  # function name
    r'(?:\((?:[^\)]*)\))'  # parameter list，assume no round bracket in round bracket
    r'(?:\s*throws\s+[\w\, ]+)?)'  # exception list
    , re.MULTILINE)

    matches = function_pattern.findall(content)
    
    return function_pattern.findall(content)

def find_imports(content: str):
    import_pattern = re.compile(r'^\s*import\s+([\w\.\*]+)\s*;\s*$', re.MULTILINE)
    
    return import_pattern.findall(content)

def find_simple_variables(content: str):
    variable_pattern = re.compile(r'^\s*'
                     r'((?:(?:public|protected|private|final|static)\s+)*'  # modifier, final and static
                     r'(?:int|float|boolean|char|double|String|(?:[A-Z][\w<>]*))' # variable type
                     r'\s+(\w+)\s*;)' # variable name
                     ,re.MULTILINE)
    
    return variable_pattern.findall(content)

def find_variables(content: str):
    variable_pattern = re.compile(r'^\s*'
                     r'((?:(?:public|protected|private|final|static)\s+)*'  # modifier, final and static
                     r'(?:int|float|boolean|char|double|String|(?:[A-Z][\w<>]*))' # variable type
                     r'\s+(?:\w+)\s*' # variable name
                     r'(?:\s*=\s*[^;]+)?;)' # variable operation(optional)
                     ,re.MULTILINE)
    
    return variable_pattern.findall(content)

def find_simple_returns(content: str):
    # string_regex = r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\""
    pattern = re.compile(r'^\s*(return(?:;' # return;
                                r'|\s+(?:\w*|\"(?:[^\"\\]*(?:\\.[^\"\\]*)*)\")\s*;\s*))$', # return variable, or return variable ;
                                re.MULTILINE) 
    
    return pattern.findall(content)

def find_classes(content: str):
    class_pattern = re.compile(r'^\s*((?:public\s+|protected\s+|private\s+)?'  # modifier
                               r'(?:final\s+|abstract\s+)?'
                               r'class\s+([\w<>]+))', re.MULTILINE)
    
    return class_pattern.findall(content)

