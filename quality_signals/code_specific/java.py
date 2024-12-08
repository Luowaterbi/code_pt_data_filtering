"""
Filters specific for Java
"""

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.code.java_utils import *
from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType


@register_quality_signal('qsc_codejava_cate_var_zero', 'codedocument')
class QSC_CodeJava_Cate_Var_Zero(QSCodeBase):
    """
    The Java document can be parsed successfully by the AST or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        score = float(len(find_variables(code.code_raw_content))==0)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codejava_frac_lines_func_ratio', 'codedocument')
class QSC_CodeJava_Frac_Lines_Func_Ratio(QSCodeBase):
    """
    The fraction of lines that are function declarations in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = len(find_functions(code.code_raw_content))
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]


@register_quality_signal('qsc_codejava_score_lines_no_logic', 'codedocument')
class QSC_CodeJava_Score_Lines_No_Logic(QSCodeBase):
    """
    The score used to evaluate the degree of code logic in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        total = len(code.code_normalized_lines)
        if total == 0:
            return [(0, len(code), None)]
        
        # 1. count the number of functions
        function_num = len(find_functions(code.code_raw_content))
        # 2. count the number of imports
        import_num = len(find_imports(code.code_raw_content))
        # 3. count the number of simple variables
        variable_num = len(find_simple_variables(code.code_raw_content))
        # 4. count the number of simple return statements
        return_variable_num = len(find_simple_returns(code.code_raw_content))
        # 5. count the number of classes
        class_num = len(find_classes(code.code_raw_content))

        count = function_num + import_num + variable_num + return_variable_num + class_num
        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejava_frac_words_no_modifier', 'codedocument')
class QSC_CodeJava_Frac_Words_No_Modifier(QSCodeBase):
    """
    The fraction of functions and classes that have no access modifier in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        # get function line
        function_lines = find_functions(code.code_raw_content)
        function_num = len(function_lines)
        # count number of no modifier functions
        no_modifier_function_num = 0
        for line in function_lines:
            if 'public' in line or 'protected' in line or 'private' in line:
                no_modifier_function_num += 1
        
        # get class line
        class_lines = find_classes(code.code_raw_content)
        class_num = len(class_lines)
        # count number of no modifier classes
        no_modifier_class_num = 0
        for line in class_lines:
            if 'public' in line or 'protected' in line or 'private' in line:
                no_modifier_class_num += 1

        count = no_modifier_function_num + no_modifier_class_num
        total = function_num + class_num

        if total == 0:
            return [(0, len(code), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]

        
@register_quality_signal('qsc_codejava_frac_words_legal_var_name', 'codedocument')
class QSC_CodeJava_Frac_Words_Legal_Var_Name(QSCodeBase):
    """
    The fraction of variables that are legal variable names in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]


        name_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        
        variable_lines = find_variables(code.code_raw_content)
        total = len(variable_lines)

        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for line in variable_lines:
            if name_pattern.match(line[1]):
                count += 1

        score = count / total
        score = round(score, PRECISION)
        
        return [(0, len(code), score)]
        

@register_quality_signal('qsc_codejava_frac_words_legal_func_name', 'codedocument')
class QSC_CodeJava_Frac_Words_Legal_Func_Name(QSCodeBase):
    """
    The fraction of function names that are legal function names in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*$')
            
        variable_lines = find_functions(code.code_raw_content)
        total = len(variable_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for line in variable_lines:
            if name_pattern.match(line[1]):
                count += 1

        score = count / total
        score = round(score, PRECISION)
            
        return [(0, len(code), score)]


@register_quality_signal('qsc_codejava_frac_words_legal_class_name', 'codedocument')
class QSC_CodeJava_Frac_Words_Legal_Class_Name(QSCodeBase):
    """
    The fraction of class names that are legal class names in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        name_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
            
        variable_lines = find_classes(code.code_raw_content)
        total = len(variable_lines)
        if total == 0:
            return [(0, len(code), None)]

        count = 0
        for line in variable_lines:
            if name_pattern.match(line[1]):
                count += 1

        score = count / total
        score = round(score, PRECISION)
            
        return [(0, len(code), score)]
    

@register_quality_signal('qsc_codejava_frac_lines_print', 'codedocument')
class QSC_CodeJava_Frac_Lines_Print(QSCodeBase):
    """
    The fraction of the number of lines that contain 'print'-related statements in the Java document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['java']:
            return [(0, len(code), None)]

        count = sum(1 for line in code.code_normalized_lines if ('System.out.print' in line.text))
        total = len(code.code_normalized_lines)

        if total == 0:
            return [(0, len(code), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(code), score)]
