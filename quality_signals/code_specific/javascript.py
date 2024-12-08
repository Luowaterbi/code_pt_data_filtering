"""
Filters specific for Javascript
"""

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.js_utils import *
from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType
import regex as re


@register_quality_signal('qsc_codejavascript_cate_ast', 'codedocument')
class QSC_CodeJavascript_Cate_Ast(QSCodeBase):
    """
    The JavaScript document can be parsed successfully by the AST or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        score = float(bool(code.ast))
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejavascript_cate_var_zero', 'codedocument')
class QSC_CodeJavascript_Cate_Var_Zero(QSCodeBase):
    """
    The JavaScript document contains no variable declaration or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        if code.ast is None: # TODO
            return [(0, len(code), None)]

        variables = find_variables(code)
        score = float(len(variables) == 0)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codejavascript_frac_lines_func_ratio', 'codedocument')
class QSC_CodeJavascript_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        count = len(find_functions(code))
        # print(f'count: {count}')
        # print(f'total: {total}')
        # for i, line in enumerate(code.code_normalized_lines):
        #     print(f'line {i+1}:\n{line.text}')
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejavascript_num_statement_line', 'codedocument')
class QSC_CodeJavascript_Num_Statement_Line(QSCodeBase):
    """
    The number of statements in each line of the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        count = len(code.ast.body)
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejavascript_score_lines_no_logic', 'codedocument')
class QSC_CodeJavascript_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        # 1. count the number of function
        function_num = len(find_functions(code))
        # 2. count the number of import
        import_num = len(find_imports(code))
        # 3. count the number of simple variable
        variable_num = len(find_simple_variables(code))
        # 4. count the number of simple return statements
        return_variable_num = len(find_simple_returns(code))
        # 5. count the number of class
        class_num = len(find_classes(code))

        count = function_num + import_num + variable_num + return_variable_num + class_num
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejavascript_frac_words_legal_var_name', 'codedocument')
class QSC_CodeJavascript_Frac_Words_Legal_Var_Name(QSCodeBase):
    """
    The fraction of variables that have legal names in the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        
        name_pattern = re.compile(r'^[a-z\$][a-zA-Z0-9]*$')
            
        variables = find_variables(code)
        total = len(variables)
        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for var in variables:
            if name_pattern.match(var):
                count += 1
        
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejavascript_frac_words_legal_func_name', 'codedocument')
class QSC_CodeJavascript_Frac_Words_Legal_Func_Name(QSCodeBase):
    """
    The fraction of function names that are legal function names in the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        name_pattern = re.compile(r'^[a-zA-Z\$][a-zA-Z0-9]*$')
            
        functions = find_functions(code)
        total = len(functions)
        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for func in functions:
            if name_pattern.match(func):
                count += 1

        score = count / total
        score = round(score, PRECISION)
            
        return [(0, len(code), score)]
        

@register_quality_signal('qsc_codejavascript_frac_words_legal_class_name', 'codedocument')
class QSC_CodeJavascript_Frac_Words_Legal_Class_Name(QSCodeBase):
    """
    The fraction of class names that are legal class names in the JavaScript document
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]

        
        name_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
            
        classes = find_classes(code)
        total = len(classes)
        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for cls in classes:
            if name_pattern.match(cls):
                count += 1

        score = count / total
        score = round(score, PRECISION)
            
        return [(0, len(code), score)]
    

@register_quality_signal('qsc_codejavascript_frac_lines_print', 'codedocument')
class QSC_CodeJavascript_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of lines that contain 'console.log' in the JavaScript document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['javascript']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('console.log' in line.text))
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
