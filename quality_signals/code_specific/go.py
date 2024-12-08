"""
Filters specific for Golang
"""

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.go_utils import *
from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

@register_quality_signal('qsc_codego_cate_testfile', 'codedocument')
class QSC_CodeGo_Cate_Testfile(QSCodeBase):
    """
    The Go document is a test file or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['go']:
            return [(0, len(code), None)]

        score = float(code.filename.lower().endswith('_test.go'))
        score = round(score, PRECISION)
        
        return [(0, len(code), score)]
    

@register_quality_signal('qsc_codego_frac_lines_func_ratio', 'codedocument')
class QSC_CodeGo_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the Go document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['go']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = len(find_functions(code.code_raw_content))
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codego_cate_var_zero', 'codedocument')
class QSC_CodeGo_Cate_Var_Zero(QSCodeBase):
    """
    The Go document contains no variable declaration.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(slef, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['go']:
            return [(0, len(code), None)]

        score = float(find_variables(code.code_raw_content) == 0)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codego_score_lines_no_logic', 'codedocument')
class QSC_CodeGo_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the Go document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['go']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        #1. count the number of function
        function_num = len(find_functions(code.code_raw_content))
        #2. count the number of include
        include_num = len(find_imports(code.code_raw_content))
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
    
@register_quality_signal('qsc_codego_frac_lines_print', 'codedocument')
class QSC_CodeGo_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of lines that contain a print statement in the Go document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['go']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = sum([1 for line in code.code_normalized_lines if ('fmt.Print' in line.text)])
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
