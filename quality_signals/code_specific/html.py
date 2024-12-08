"""
Filters specific for HTML
"""

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

@register_quality_signal('qsc_codehtml_cate_ast', 'codedocument')
class QSC_CodeHtml_Cate_Ast(QSCodeBase):
    """
    The HTML document can be parsed successfully by the AST or not.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['html']:
            return [(0, len(code), None)]

        score = code.ast is not None
        return [(0, len(code), float(score))]


@register_quality_signal('qsc_codehtml_frac_words_text', 'codedocument')
class QSC_CodeHtml_Frac_Words_Text(QSCodeBase):
    """
    The fraction of words in the raw text of the HTML document.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, code: QSCodeDocument) -> SignalType:
        if code.program_lang not in ['html']:
            return [(0, len(code), None)]
        
        if len(code.raw_content) == 0:
            return [(0, len(code), None)]

        soup = code.ast
        if soup is None:
            return [(0, len(code), None)]

        text = soup.get_text()
        score = len(text) / len(code.raw_content)
        score = round(score, PRECISION)

        return [(0, len(code), score)]

@register_quality_signal('qsc_codehtml_num_chars_text', 'codedocument')
class QSC_CodeHtml_Num_Chars_Text(QSCodeBase):
    """
    The number of characters in the text of the HTML document.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, code:QSCodeDocument) -> SignalType:
        if code.program_lang not in ['html']:
            return [(0, len(code), None)]
        soup = code.ast
        if soup is None:
            return [(0, len(code), None)]
        text = soup.get_text()
        score = len(text)

        return [(0, len(code), float(score))]
        