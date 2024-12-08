"""
Filters for general documents
"""

import re
from collections import Counter

from base import QSCodeBase, register_quality_signal
from document import QSCodeDocument
from utils.constants import BULLETS


from redpajama.core.constants import PRECISION
from redpajama.core.data_types import SignalType

from redpajama.core.quality_signals.content import (RPS_Doc_Curly_Bracket,
                                                    RPS_Doc_Stop_Word_Fraction)

from redpajama.core.quality_signals.natural_language import (RPS_Doc_Word_Count,
                                                             RPS_Doc_Mean_Word_Length,
                                                             RPS_Doc_Frac_Unique_Words,
                                                             RPS_Doc_Unigram_Entropy,
                                                             RPS_Doc_Frac_All_Caps_Words,)

from redpajama.core.quality_signals.repetitions import (RPS_Doc_Frac_Chars_Top_2gram,
                                                        RPS_Doc_Frac_Chars_Top_3gram,
                                                        RPS_Doc_Frac_Chars_Top_4gram,
                                                        RPS_Doc_Frac_Chars_Dupe_5Grams,
                                                        RPS_Doc_Frac_Chars_Dupe_6Grams,
                                                        RPS_Doc_Frac_Chars_Dupe_7Grams,
                                                        RPS_Doc_Frac_Chars_Dupe_8Grams,
                                                        RPS_Doc_Frac_Chars_Dupe_9Grams,
                                                        RPS_Doc_Frac_Chars_Dupe_10Grams,)


########## Founded on Redpajama content.py ##########

@register_quality_signal('qsc_doc_frac_chars_curly_bracket', 'codedocument')
class QSC_Doc_Frac_Chars_Curly_Bracket(QSCodeBase):
    """
    The character fraction of "{}".
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Curly_Bracket()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_doc_frac_words_redpajama_stop', 'codedocument')
class QSC_Doc_Frac_Words_Redpajama_Stop(QSCodeBase):
    """
    The ratio between the number of stop words and the number of words.
    """
    SUPPORT_LANGUAGES = ("en", "fr", "es", "it", "de")

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = {}
        for lang in self.SUPPORT_LANGUAGES:
            self.rps[lang] = RPS_Doc_Stop_Word_Fraction(lang)

    def __call__(self, document: QSCodeDocument) -> SignalType:
        if document.language not in self.SUPPORT_LANGUAGES:
            return [(0, len(document), None)]
        return self.rps[document.language](document)

########## Founded on Redpajama natural_language.py ##########


@register_quality_signal('qsc_doc_num_sentences', 'codedocument')
class QSC_Doc_Num_Sentences(QSCodeBase):
    """ 
    The number of sentences.
    """
    SENT_PATTERN = re.compile(r'\b[^.!?。！？؟]+[.!?。！？؟]*', flags=re.UNICODE)

    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:

        score = float(len(self.SENT_PATTERN.findall(document.raw_content)))
        return [(0, len(document), score)]

@register_quality_signal('qsc_code_num_words', 'codedocument')
@register_quality_signal('qsc_doc_num_words', 'codedocument')
class QSC_Doc_Num_Words(QSCodeBase):
    """
    The number of words.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Word_Count()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)

@register_quality_signal('qsc_code_num_chars', 'codedocument')
@register_quality_signal('qsc_doc_num_chars', 'codedocument')
class QSC_Doc_Num_Chars(QSCodeBase):
    """
    The number of characters.
    """
    def __call__(self, document: QSCodeDocument) -> SignalType:
        return [(0, len(document), float(len(document)))]


@register_quality_signal('qsc_doc_num_lines', 'codedocument')
class QSC_Doc_Num_Lines(QSCodeBase):
    """
    The number of lines.
    """
    def __call__(self, document: QSCodeDocument) -> SignalType:
        return [(0, len(document), float(len(document.raw_lines)))]

@register_quality_signal('qsc_code_mean_word_length', 'codedocument')
@register_quality_signal('qsc_doc_mean_word_length', 'codedocument')
class QSC_Doc_Mean_Word_Length(QSCodeBase):
    """
    The mean length of words.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Mean_Word_Length()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_doc_frac_words_full_bracket', 'codedocument')
class QSC_Doc_Frac_Words_Full_Bracket(QSCodeBase):
    """
    The fractions of words of full-width bracket '【】'.
    """
    SYMBOLS = ("【", "】")
    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        total = document.num_raw_words

        if total == 0:
            return [(0, len(document), None)]

        count = 0
        for word in document.raw_words:
            count += int(word in self.SYMBOLS)

        score = count / total
        score = round(score, PRECISION)

        return [(0, len(document), score)]


@register_quality_signal('qsc_doc_frac_lines_end_with_readmore', 'codedocument')
class QSC_Doc_Frac_Lines_End_With_Readmore(QSCodeBase):
    """
    The fraction of lines that end with a "readmore"-like content.
    """
    ELLIPSIS_SYMBOLS = (
        "...",             # en, es, pt, fr, de, it, nl, ar
        "…",               # general, zh, ja
        '全文',             # zh
        '详情',             # zh
        '详细',             # zh
        '更多',             # zh
        'المزيد',          # ar
        'تفاصيل',          # ar
        'اقرأ المزيد',     # ar
        'もっと',           # ja
        '詳細',            # ja
        'もっと読む'        # ja
    )

    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        num_lines = len(document.raw_lines)

        if num_lines == 0:
            return [(0, len(document), None)]

        total_ellipsis_lines = float(sum(
            text_slice.text.rstrip().rstrip(']】)>》').endswith(self.ELLIPSIS_SYMBOLS)
            for text_slice in document.raw_lines
        ))

        score = total_ellipsis_lines / num_lines
        score = round(score, PRECISION)
        return [(0, len(document), score)]


@register_quality_signal('qsc_doc_frac_lines_start_with_bullet', 'codedocument')
class QSC_Doc_Frac_Lines_Start_With_Bullet(QSCodeBase):
    """
    The fraction of lines that start with an bullet symbol.
    """
    BULLET_SYMBOLS = BULLETS

    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        num_lines = len(document.raw_lines)

        if num_lines == 0:
            return [(0, len(document), None)]

        total_bullet_lines = float(sum(
            text_slice.text.lstrip().startswith(self.BULLET_SYMBOLS)
            for text_slice in document.raw_lines
        ))

        score = total_bullet_lines / num_lines
        score = round(score, PRECISION)
        return [(0, len(document), score)]


@register_quality_signal('qsc_code_frac_words_unique', 'codedocument')
@register_quality_signal('qsc_doc_frac_words_unique', 'codedocument')
class QSC_Doc_Frac_Words_Unique(QSCodeBase):  # noqa
    """
    The fraction of unique words in the content.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Unique_Words()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_doc_entropy_unigram', 'codedocument')
class QSC_Doc_Entropy_Unigram(QSCodeBase):  # noqa
    """
    The entropy of the unigram distribution of the content.
    """
    DEFAULT_FILTER_CONFIG = {'en': 'lambda x: x < 3',
                             'es': 'lambda x: x < 3',
                             'pt': 'lambda x: x < 3',
                             'fr': 'lambda x: x < 3',
                             'de': 'lambda x: x < 3',
                             'it': 'lambda x: x < 3',
                             'nl': 'lambda x: x < 3',
                             'zh': 'lambda x: x < 3',
                             'ar': 'lambda x: x < 3',
                             'ja': 'lambda x: x < 3',
                             }

    def __init__(self, *args, **kwargs):
        self.rps = RPS_Doc_Unigram_Entropy()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_doc_frac_words_all_caps', 'codedocument')
class QSC_Doc_Frac_Words_All_Caps(QSCodeBase):
    """
    The fraction of words that are all in capital letters.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_All_Caps_Words()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


########## Founded on Redpajama repetitions.py ##########


@register_quality_signal('qsc_doc_frac_lines_dupe_lines', 'codedocument')
class QSC_Doc_Frac_Lines_Dupe_Lines(QSCodeBase):
    """
    The line fraction of depulicate lines.
    """
    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        if len(document.raw_lines) == 0:
            return [(0, len(document), None)]

        lines = [line.text.strip() for line in document.raw_lines if line.text.strip()]
        line2count = Counter(lines)
        count = sum([v for v in line2count.values() if v != 1])
        total = sum([v for v in line2count.values()])

        if total == 0:
            return [(0, len(document), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(document), score)]


@register_quality_signal('qsc_doc_frac_chars_dupe_lines', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_Lines(QSCodeBase):
    """
    The character fraction of depulicate lines.
    """
    __slots__ = ()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        if len(document.raw_lines) == 0:
            return [(0, len(document), None)]

        line2count = Counter((textslice.text.strip() for textslice in document.raw_lines))
        count = sum([len(k)*v for k, v in line2count.items() if v != 1])
        total = sum([len(k)*v for k, v in line2count.items()])

        if total == 0:
            return [(0, len(document), None)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(document), score)]


@register_quality_signal('qsc_code_frac_chars_top_2grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_top_2grams', 'codedocument')
class QSC_Doc_Frac_Chars_Top_2Grams(QSCodeBase):
    """
    The fraction of characters in the top word 2gram.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Top_2gram()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_top_3grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_top_3grams', 'codedocument')
class QSC_Doc_Frac_Chars_Top_3Grams(QSCodeBase):
    """
    The fraction of characters in the top word 3gram.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Top_3gram()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_top_4grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_top_4grams', 'codedocument')
class QSC_Doc_Frac_Chars_Top_4Grams(QSCodeBase):
    """
    The fraction of characters in the top word 4gram.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Top_4gram()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_5grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_5grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_5Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 5grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_5Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_6grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_6grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_6Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 6grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_6Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_7grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_7grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_7Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 7grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_7Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_8grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_8grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_8Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 8grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_8Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_9grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_9grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_9Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 9grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_9Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


@register_quality_signal('qsc_code_frac_chars_dupe_10grams', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_dupe_10grams', 'codedocument')
class QSC_Doc_Frac_Chars_Dupe_10Grams(QSCodeBase):
    """
    The fraction of characters in duplicate word 10grams.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.rps = RPS_Doc_Frac_Chars_Dupe_10Grams()

    def __call__(self, document: QSCodeDocument) -> SignalType:
        return self.rps(document)


########## New ##########

@register_quality_signal('qsc_code_frac_chars_replacement_symbols', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_replacement_symbols', 'codedocument')
class QSC_Doc_Frac_Chars_Replacement_Symbol(QSCodeBase):
    """
    the fraction of character '�' in the content.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, document: QSCodeDocument) -> SignalType:
        total = len(document.raw_content)
        if total == 0:
            return [(0, len(document), None)]
        count = document.raw_content.count('�')
        score = count / total
        score = round(score, PRECISION)

        return [(0, len(document), score)]


@register_quality_signal('qsc_doc_cate_code_related_file_name', 'codedocument')
class QSC_Doc_Cate_Code_Related_File_Name(QSCodeBase):
    """
    The document is code-related file name or not.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_file_names = ["readme", "notes", "todo", "description", "cmakelists"]

    
    def __call__(self, document: QSCodeDocument) -> SignalType:
        
        # remove ext from file name
        file_name = document.filename.split('.')[0].lower()

        flag = ("requirement" in file_name) or (file_name in self.related_file_names) or (file_name == "read.me")
        
        return [(0, len(document), float(flag))]
    

@register_quality_signal('qsc_doc_num_chars_sentence_length_mean', 'codedocument')
class QSC_Doc_Num_Chars_Sentence_Length_Mean(QSCodeBase):
    """
    The mean length of sentences in the content.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, document: QSCodeDocument) -> SignalType:
        sentences = re.split(r'\.|\?|\!|\n', document.raw_content)
        if len(sentences) == 0:
            return [(0, len(document), None)]
        

        mean = sum([len(sentence) for sentence in sentences]) / len(sentences)
        mean = round(mean, PRECISION)
        return [(0, len(document), mean)]
    

@register_quality_signal('qsc_doc_frac_chars_hyperlink_html_tag', 'codedocument')
class QSC_Doc_Frac_Chars_Url_Html_Tag(QSCodeBase):
    """
    The fraction of characters that are hyperlink or HTML tags.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, document: QSCodeDocument) -> SignalType:
        total = len(document.raw_content)
        if total == 0:
            return [(0, len(document), None)]
        
        link_pattern = r'\(https?://\S+\)'
        html_tag_pattern = r'<.*?>'
        link_list = re.findall(link_pattern, document.raw_content)
        html_tag_list = re.findall(html_tag_pattern, document.raw_content)

        url_char_num = sum([len(link) for link in link_list])
        html_tag_char_num = sum([len(html_tag) for html_tag in html_tag_list])
        count = url_char_num + html_tag_char_num

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(document), score)]


@register_quality_signal('qsc_doc_frac_chars_alphabet','codedocument')
class QSC_Doc_Frac_Chars_Alphabet(QSCodeBase):
    """
    The fraction of characters that are alphabet.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, document: QSCodeDocument) -> SignalType:
        if len(document.visible_content) == 0:
            return [(0, len(document), 0.0)]
        if document.language != 'en':
            return [(0, len(document), None)]
        
        score = sum(c.isalpha() for c in document.visible_content)
        score = score / len(document.visible_content)

        score = round(score, PRECISION)

        return [(0, len(document), score)]


@register_quality_signal('qsc_code_frac_chars_digital', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_digital', 'codedocument')
class QSC_Doc_Frac_Chars_Digital(QSCodeBase):
    """
    The fraction of characters that are digital.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, document: QSCodeDocument) -> SignalType:
        count, total = 0, 0
        
        total = len(document.visible_content)

        for c in document.visible_content:
            if c.isdigit():
                count += 1

        if not total:
            return [(0, len(document), 1.0)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(document), score)]

@register_quality_signal('qsc_code_frac_chars_whitespace', 'codedocument')
@register_quality_signal('qsc_doc_frac_chars_whitespace', 'codedocument')
class QSC_Doc_Frac_Chars_Whitespace(QSCodeBase):
    """
    The fraction of characters that are whitespace.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, document: QSCodeDocument) -> SignalType:
        count, total = 0, 0
        
        total = len(document.raw_content)

        white_chars = re.findall(r'\s', document.raw_content)
        count = len(white_chars)

        if not total:
            return [(0, len(document), 1.0)]

        score = count / total
        score = round(score, PRECISION)
        return [(0, len(document), score)]

@register_quality_signal('qsc_doc_frac_chars_hex_words', 'codedocument')
class QSC_Doc_Frac_Chars_Hex_Words(QSCodeBase):
    """
    The fraction of characters that are hex words.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, document: QSCodeDocument) -> SignalType:
        total = len(document.raw_content)
        if total == 0:
            return [(0, len(document), None)]
        
        count = sum(len(element) for element in re.findall(r'\b0[xX][0-9a-fA-F]+\b', document.raw_content))
        score = count / total
        score = round(score, PRECISION)

        return [(0, len(document), score)]
