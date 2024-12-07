import regex as re

def find_functions(content:str):

    function_pattern = re.compile(r'^\s*'
    r'((?:(?:public|protected|private|internal)\s+)?'  # modifier and static
    r'(?:(?:static|virtual|override|abstract|async)\s+)?'
    r'(?:(?!\s*(?:public|private|protected|if|else)\s*)(?:<\w+>)?\s*\w+\s+)'  # return type(also include template and array), negative look ahead to exclude access modifier
    r'(?:\w+\s*)'  # function name
    r'(?:\((?:[^\)]*)\)))'  # parameter list，assume no round bracket in round bracket
    , re.MULTILINE)

    return function_pattern.findall(content)

def find_variables(content:str):
    var_pattern = re.compile(
        r'\b(?:int|float|double|char|string|var|bool|byte|sbyte|short|ushort|uint|long|ulong|decimal)\s+\w+(?:\s*=\s*[^;\n]+)?',
        re.MULTILINE
    )
    return var_pattern.findall(content)

def find_include(content:str):
    using_pattern = re.compile(
        r'^\s*using\s+[a-zA-Z0-9_.]+\s*;',
        re.MULTILINE
    )
    return using_pattern.findall(content)

def find_classes(content:str):
    class_pattern = re.compile(
        r'\b(?:public|private|protected|internal|static|abstract|sealed)?\s*class\s+\w+',
        re.MULTILINE
    )
    return class_pattern.findall(content)

def find_simple_returns(content:str):
    return_pattern = re.compile(
        r'^\s*return\b(?:\s+[^;\n]+)?\s*;',
        re.MULTILINE
    )
    return return_pattern.findall(content)

def find_simple_variables(content:str):
    var_pattern = re.compile(
        r'\b(?:int|float|double|char|string|bool|byte|sbyte|short|ushort|uint|long|ulong|decimal)\s+\w+\s*;',
        re.MULTILINE
    )
    return var_pattern.findall(content)

