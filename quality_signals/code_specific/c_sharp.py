"""
Filters specific for C#
"""

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.csharp_utils import *

from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

@register_quality_signal('qsc_codecsharp_frac_lines_func_ratio', 'codedocument')
class QSC_CodeCsharp_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the C# document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['csharp']:
            return [(0, len(code), None)]
        
        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = len(find_functions(code.code_raw_content))
        score = count / total
        score = round(score, PRECISION)

        return [(0, len(code), score)]


@register_quality_signal('qsc_codecsharp_cate_var_zero', 'codedocument')
class QSC_CodeCsharp_Cate_Var_Zero(QSCodeBase):
    """
    The C# document contains no variable declaration.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['csharp']:
            return [(0, len(code), None)]

        count = find_variables(code.code_raw_content)
        score = float(count == 0)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codecsharp_score_lines_no_logic', 'codedocument')
class QSC_CodeCsharp_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the C# document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['csharp']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        #1. count the number of function
        function_num = len(find_functions(code.code_raw_content))
        #2. count the number of include
        include_num = len(find_include(code.code_raw_content))
        #3. count the number of simple variable
        variable_num = len(find_simple_variables(code.code_raw_content))
        #4. count the number of simple return statements
        return_variable_num = len(find_simple_returns(code.code_raw_content))
        #5. count the number of class
        class_num = len(find_classes(code.code_raw_content))

        count = function_num + include_num + variable_num + return_variable_num + class_num
        
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
    
@register_quality_signal('qsc_codecsharp_frac_lines_print', 'codedocument')
class QSC_CodeCsharp_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of the number of lines that contain 'Console.WriteLine' in the C# document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['csharp']:
            return [(0, len(code), None)]
        
        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('Console.WriteLine' in line.text))
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
