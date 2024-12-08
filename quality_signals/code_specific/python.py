"""
Filters specific for Python
"""
import ast
from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.python_utils import *

from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

import sys
sys.setrecursionlimit(10000)  # increase the recursive depth limit to 10000

@register_quality_signal('qsc_codepython_cate_ast', 'codedocument')
class QSC_CodePython_Cate_Ast(QSCodeBase):
    """
    The Python document can be parsed successfully by the AST or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        parse_success = code.ast is not None
        return [(0, len(code), float(parse_success))]


@register_quality_signal('qsc_codepython_frac_lines_func_ratio', 'codedocument')
class QSC_CodePython_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        if code.ast is None:
            return [(0, len(code), None)]
        
        if code.valid_lines_len == 0:
            return [(0, len(code), None)]

        function_num = len(find_functions(code))
        score = function_num / code.valid_lines_len
        score = round(score, PRECISION)
        
        return [(0, len(code), score)]


@register_quality_signal('qsc_codepython_cate_var_zero', 'codedocument')
class QSC_CodePyton_Cate_Var_Zero(QSCodeBase):
    """
    The Python document contains no variable declaration or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        if code.ast is None:
                return [(0, len(code), None)]
        try:
            variable_lines = find_variables(code)
            return [(0, len(code), len(variable_lines)==0)]
        except:
            return [(0, len(code), float(True))]


@register_quality_signal('qsc_codepython_frac_lines_pass', 'codedocument')
class QSC_CodePython_Frac_Lines_Pass(QSCodeBase):
    """
    The fraction of lines that are pass statements in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        non_empty_lines = code.code_normalized_lines
        pass_lines_count = sum(1 for line in non_empty_lines if 'pass' in line.text.lower())
        total_non_empty_lines_count = len(non_empty_lines)
        score = pass_lines_count / total_non_empty_lines_count if total_non_empty_lines_count > 0 else 0.0
        score = round(score, PRECISION)

        return [(0, len(code), score)]

@register_quality_signal('qsc_codepython_frac_lines_import', 'codedocument')
class QSC_CodePython_Frac_Lines_Import(QSCodeBase):
    """
    The fraction of lines that are import statements in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        non_empty_lines = code.code_normalized_lines
        import_lines_count = sum(1 for line in non_empty_lines if 'import' in line.text.lower())
        total_non_empty_lines_count = len(non_empty_lines)
        score = import_lines_count / total_non_empty_lines_count if total_non_empty_lines_count > 0 else 0.0
        score = round(score, PRECISION)

        return [(0, len(code), score)]        


@register_quality_signal('qsc_codepython_frac_lines_simplefunc', 'codedocument')
class QSC_CodePython_Frac_Lines_SimpleFunc(QSCodeBase):
    """
    The fraction of lines that are simple function declarations in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]
        if code.ast is None:
            return [(0, len(code), None)]
        
        if code.valid_lines_len == 0:
            return [(0, len(code), None)]
        
        class SimpleFunctionFinder(ast.NodeVisitor):
            def __init__(self):
                self.simple_function_count = 0
                self.total_function_count = 0

            def visit_FunctionDef(self, node):
                self.total_function_count += 1
                if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                    self.simple_function_count += 1
                self.generic_visit(node)
        
        finder = SimpleFunctionFinder()
        finder.visit(code.ast)

        simple_function_ratio = finder.simple_function_count / code.valid_lines_len
        
        return [(0, len(code), simple_function_ratio)]


@register_quality_signal('qsc_codepython_score_lines_no_logic', 'codedocument')
class QSC_CodePython_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]

        if code.ast is None:
            return [(0, len(code), None)]
        
        if code.valid_lines_len == 0:
            return [(0, len(code), None)]
        
        #1. count the number of function
        function_num = len(find_functions(code))
        #2. count the number of import
        import_num = len(find_import(code))
        #3. count the number of class
        class_num = len(find_class(code))
        #4. count the number of simple return statements
        return_num = len(find_simple_return(code))
        #5. count the number of simple variable
        simple_variable = len(find_simple_variable(code))

        all_num = function_num + import_num + class_num + return_num + simple_variable

        frac = all_num / code.valid_lines_len
        frac = round(frac, PRECISION)
        return [(0, len(code), frac)]
    

@register_quality_signal('qsc_codepython_frac_lines_print', 'codedocument')
class QSC_CodePython_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of lines that contain a print statement in the Python document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['python']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('print' in line.text))
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]