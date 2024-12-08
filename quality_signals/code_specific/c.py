"""
Filters specific for C
"""

import regex as re
from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.c_utils import *
from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

@register_quality_signal('qsc_codec_frac_lines_func_ratio', 'codedocument')
class QSC_CodeC_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the C document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        count = len(find_functions(code.code_raw_content)) # TODO
        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]
        score = count / total
        score = round(score, PRECISION)

        return [(0, len(code), score)]


@register_quality_signal('qsc_codec_cate_bitsstdc', 'codedocument')
class QSC_CodeC_Cate_Bitsstdc(QSCodeBase):
    """
    The C document contains the header file "bits/stdc++.h" or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        target = "bits/stdc++.h"
        score = float(target in code.code_raw_content.strip().lower()[:200])
        score = round(score, PRECISION)

        return [(0, len(code), score)]


@register_quality_signal('qsc_codec_nums_lines_main', 'codedocument')
class QSC_CodeC_Nums_Lines_Main(QSCodeBase):
    """
    The number of lines that contain the main function declaration in the C document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        pattern = r'\bmain\s*\([^)]*\)\s*\{'
        matches = re.findall(pattern, code.code_raw_content)
        score = len(matches)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codec_frac_lines_goto', 'codedocument')
class QSC_CodeC_Frac_Lines_Goto(QSCodeBase):
    """
    The fraction of lines that contain the "goto" statement in the C document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('goto' in line.text))
        total = len(code.code_normalized_lines)

        if total == 0:
            return [(0, len(code), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codec_cate_var_zero', 'codedocument')
class QSC_CodeC_Cate_Var_Zero(QSCodeBase):
    """
    The C document contains no variable declaration or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        variable_lines = find_variables(code.code_raw_content)
        score = float(len(variable_lines) == 0)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codec_score_lines_no_logic', 'codedocument')
class QSC_CodeC_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the C document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        #1. count the number of function
        function_num = len(find_functions(code.code_raw_content))
        #2. count the number of include
        include_num = len(find_include(code.code_raw_content))
        #3. count the number of simple variable
        variable_num = len(find_simple_variables(code.code_raw_content))
        #4. count the number of simple return
        return_variable_num = len(find_simple_returns(code.code_raw_content))
        #5. count the number of class
        class_num = len(find_classes(code.code_raw_content))

        count = function_num + include_num + variable_num + return_variable_num + class_num
        total = len(code.code_normalized_lines) # TODO

        if total == 0:
            return [(0, len(code), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
    
@register_quality_signal('qsc_codec_frac_lines_print', 'codedocument')
class QSC_CodeC_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of lines that contain the "printf" statement in the C document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c']:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('printf' in line.text))
        total = len(code.code_normalized_lines)

        if total == 0:
            return [(0, len(code), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codecpp_frac_lines_preprocessor_directives', 'codedocument')    
@register_quality_signal('qsc_codec_frac_lines_preprocessor_directives', 'codedocument')
class QSC_CodeC_Frac_Lines_Preprocessor_Directives(QSCodeBase):
    """
    The fraction of lines that contain preprocessor directives in the C source document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['c', 'cpp']:
            return [(0, len(code), None)]
        
        if code.extension in ['h', 'hpp', 'hxx', 'hh', 'h++']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]
        
        directives = [r'#\s*include', r'#\s*define', r'#\s*if', r'#\s*ifdef', r'#\s*ifndef', r'#\s*else', r'#\s*elif', r'#\s*endif', r'#\s*error', r'#\s*pragma', r'#\s*warning', r'#\s*undef', r'#\s*line',
                      r'struct', r'using']
        count = sum(1 for line in code.code_normalized_lines if any(re.search(d, line.text) for d in directives))


        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]


