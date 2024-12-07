import re
import string
import unicodedata
from utils.constants import *

def normalize_text(
        text: str,
        remove_control: bool = True,
        halfpunct: bool = True,
        punct: str = 'replace',
        lowercase: bool = True,
        white_space: bool = True,
        unicode: str = 'NFKC',
        remove_zh_whitespace: bool = True,
        remove_digits: bool = True,
    ):

    # step1: remove control chars
    if remove_control:
        text = ''.join(CONTROL_TO_NORM.get(c, c) for c in text)

    # step2: tohalfwidth punctuation, typically useful for Chinese
    if halfpunct:
        text = ''.join(FULL_PUNCT_TO_HALF.get(c, c) for c in text)

    # step3: remove whitespace between zh charaters
    if remove_zh_whitespace:
        pattern = r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])'
        text = re.sub(pattern, r'\1\2', text)

    # step4: deal with punctuation.
    if punct:
        # For Chinese, the punctuation is useful for seperation.
        if punct == 'replace':
            text = ''.join(' ' if c in string.punctuation else c for c in text)
        # For English, we use whitespace for seperation, we can just remove
        elif punct == 'remove':
            text = text.translate(str.maketrans('', '', string.punctuation))

    # step5: lowercase
    if lowercase:
        text = text.lower()

    # step6: remove digits
    if remove_digits:
        text = re.sub(r"(\d+)|(\d+\.\d+)", " ", text)

    # step7: normalize whitespace
    if white_space:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)

    # step8: unicode normalizetion
    if unicode:
        text = unicodedata.normalize(unicode, text)

    return text