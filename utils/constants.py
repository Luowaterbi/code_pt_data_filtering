import string
from collections import defaultdict

def half_to_full_width(text):
    """
    convert half-width characters to full-width characters.
    """
    full_width_text = ""
    for char in text:
        unicode_code = ord(char)
        if unicode_code == 32:  # 空格特殊处理
            unicode_code = 0x3000
        elif 33 <= unicode_code <= 126:  # 其他ASCII字符
            unicode_code += 0xfee0
        full_width_text += chr(unicode_code)
    return full_width_text


def full_to_half_width(text):
    """
    convert full-width characters to half-width characters.
    """
    half_width_text = ""
    for char in text:
        unicode_code = ord(char)
        if unicode_code == 0x3000:  # 空格特殊处理
            unicode_code = 32
        elif 33 + 0xfee0 <= unicode_code <= 126 + 0xfee0:  # 其他ASCII字符
            unicode_code -= 0xfee0
        half_width_text += chr(unicode_code)
    return half_width_text


def get_punctuation_constants():
    data = {
        "language": ["en", "es", "pt", "fr", "de", "it", "nl", "zh", "ar", "ja"],
        "comma": [",", ",", ",", ",", ",", ",", ",", "，", "،", "、"],
        "period": [".", ".", ".", ".", ".", ".", ".", "。", ".", "。"],
        "colon": [":", ":", ":", " : ", ":", " : ", ":", "：", ":", "："],
        "semicolon": [";", ";", ";", " ; ", ";", " ; ", ";", "；", ";", "；"],
        "question": ["?", "?", "?", " ?", "?", " ?", "?", "？", "؟", "？"],
        "exclamation": ["!", "¡", "!", " !", "!", " !", "!", "！", "!", "！"],
        "quotation": ["“ ”", "« »", "“ ”", "« »", "„ “", "« »", "「 」", "“ ”", "« »", "「 」"],
        "parentheses": ["( )", "( )", "( )", "( )", "( )", "( )", "( )", "（ ）", "( )", "（ ）"],
        "hyphen": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
        "Ellipsis": ["…", "…", "…", "…", "…", "…", "…", "…", "...", "…"]
    }

    additional_punctuation = {
        "en": "-",
        "es": "¿ ¡",
        "pt": "-",
        "fr": "« »",
        "de": "„ “ ‚ ‘ – ",
        "it": "« »",
        "nl": "‘’ “” -",
        "zh": "· 「」 《》 【】 “” ￥ ‘’ —/、=。/、@·「」=…《》【】“”￥‘’—",
        "ar": "ء ـ",
        "ja": "・ ー 『』 「」 〈〉 《》"
    }

    lang_to_punctuation_detail = defaultdict(dict)
    for lang in data['language']:
        index = data['language'].index(lang)
        for key in data:
            if key == 'language':
                continue
            lang_to_punctuation_detail[lang][key] = data[key][index]
    for lang in additional_punctuation:
        lang_to_punctuation_detail[lang]['additional'] = additional_punctuation[lang]
    
    half_punctuations = string.punctuation  # 33 <= ord(c) <= 126
    full_punctuations = half_to_full_width(half_punctuations)  # 33 + 0xfee0 <= ord(c) <= 126 + 0xfee0
    full_punct_to_half = {
        '。': '.',
        '、': ',',
        '=': '=',
        '《': '"',
        '》': '"',
        '【': '[',
        '】': ']',
        '「': "'",
        '」': "'",
        '“': '"',
        '”': '"',
        '￥': '¥',
        '‘': "'",
        '’': "'",
    }
    full_punct_to_half.update({f: h for f, h in zip(full_punctuations, half_punctuations)})
    half_punct_to_full = {v: k for k, v in full_punct_to_half.items()}
    
    # to keep identical to previous code, zh and en use old code
    zh_punctuations = '。/、@·」=…《》【】“”「￥‘’—'  # not 33 <= ord(c) <= 126
    base_punctuations = set(half_punctuations) | set(full_punctuations) | set(zh_punctuations)

    lang_to_punctuations = defaultdict(set)
    lang_to_punctuations['zh'] = base_punctuations
    lang_to_punctuations['en'] = base_punctuations

    for lang in lang_to_punctuation_detail:
        if lang in ['zh', 'en']:
            continue
        _ps = [lang_to_punctuation_detail[lang][k] for k in lang_to_punctuation_detail[lang]]
        _ps = set(c for c in ''.join(_ps) if c != ' ')
        lang_to_punctuations[lang] = _ps
    
    return half_punctuations, full_punctuations, base_punctuations, lang_to_punctuation_detail, lang_to_punctuations, full_punct_to_half, half_punct_to_full

HALF_PUNCTUATIONS, FULL_PUNCTUATIONS, BASE_PUNCTUATIONS, LANG_TO_PUNCTUATION_DETAIL, LANG_TO_PUNCTUATIONS, FULL_PUNCT_TO_HALF, HALF_PUNCT_TO_FULL = get_punctuation_constants()


def get_refinedwebstopword_constants():

    stop_words_data = {
        "language": ["en", "es", "pt", "fr", "German", "it", "nl", "zh", "ar", "ja"],
        "the": ["the", "el la los las", "o a os as", "le la les", "der die das", "il lo la i gli le", "de het", "的", "ال", "-"],
        "be": ["be", "ser estar", "ser estar", "être", "sein", "essere stare", "zijn", "是", "كان", "です である"],
        "to": ["to", "a", "a", "à", "zu", "a", "naar", "到", "إلى", "へ に"],
        "of": ["of", "de", "de", "de", "von", "di", "van", "的", "من", "の"],
        "and": ["and", "y", "e", "et", "und", "e", "en", "和", "و", "と"],
        "that": ["that", "que", "que", "que", "dass", "che", "dat", "那", "أن", "それ あれ"],
        "have": ["have", "haber tener", "ter", "avoir", "haben", "avere", "hebben", "有", "لديه", "持っている"],
        "with": ["with", "con", "com", "avec", "mit", "con", "met", "与 和", "مع", "と"]
    }
    
    lang_to_rsw_detail = defaultdict(dict)
    for lang in stop_words_data['language']:
        index = stop_words_data['language'].index(lang)
        for key in stop_words_data:
            if key == 'language':
                continue
            lang_to_rsw_detail[lang][key] = stop_words_data[key][index]
    
    lang_to_rsws = defaultdict(set)
    for lang in lang_to_rsw_detail:
        _ws = [lang_to_rsw_detail[lang][k] for k in lang_to_rsw_detail[lang]]
        _ws = set(c for c in ' '.join(_ws).split() if c)
        lang_to_rsws[lang] = _ws

    # to keep identical to previous code, zh and en use old code
    lang_to_rsws['zh'] = {'去', '的', '和'}

    return lang_to_rsw_detail, lang_to_rsws

LANG_TO_REFINEDWEBSTOPWORD_DETAIL, LANG_TO_REFINEDWEBSTOPWORDS = get_refinedwebstopword_constants()

CONTROL_CHARS_INFO = (('\u0000', 'NULL',  ''),
                      ('\u0001', 'START OF HEADING', ''),
                      ('\u0002', 'START OF TEXT', ''),
                      ('\u0003', 'END OF TEXT', ''),
                      ('\u0004', 'END OF TRANSMISSION', ''),
                      ('\u0005', 'ENQUERY', ''),
                      ('\u0006', 'ACKNOWLEDGE', ''),
                      ('\u0007', 'BELL', ''),
                      # ('\u000b', 'LINE TABULATION', ''),
                      ('\u000e', 'SHIFT OUT', ''),
                      ('\u000f', 'SHIFT IN', ''),
                      ('\u0010', 'DATA LINK ESCAPE', ''),
                      ('\u0011', 'DEVICE CONTROL ONE', ''),
                      ('\u0012', 'DEVICE CONTROL TWO', ''),
                      ('\u0013', 'DEVICE CONTROL THREE', ''),
                      ('\u0014', 'DEVICE CONTROL FOUR', ''),
                      ('\u0015', 'NEGATIVE ACKNOWLEDGE', ''),
                      ('\u0016', 'SYNCHRONOUS IDLE', ''),
                      ('\u0017', 'END OF TRANSMISSION BLOCK', ''),
                      ('\u0018', 'CANCEL', ''),
                      ('\u0019', 'END OF MEDIUM', ''),
                      ('\u001a', 'SUBSTITUTE', ''),
                      # ('\u001b', 'ESCAPE', ''),
                      ('\u001c', 'INFORMATION SEPARATOR FOUR', ''),
                      ('\u001d', 'INFORMATION SEPARATOR THREE', ''),
                      ('\u001e', 'INFORMATION SEPARATOR TWO', ''),
                      ('\u001f', 'INFORMATION SEPARATOR ONE', ''),
                      # ('\u00a0', 'NO-BREAK SPACE', ' '),
                      ('\u2009', 'THIN SPACE', ' '),
                      ('\u200b', 'ZERO WIDTH SPACE', ' '),
                      ('\u202c', 'POP DIRECTIONAL FORMATTING', ''),
                      # ('\u202d', 'LEFT-TO-RIGHT OVERRIDE', ''),
                      )
CONTROL_TO_NORM = {x: z for x, y, z in CONTROL_CHARS_INFO}


BULLETS = ('\u2022',
           '\u2023',
           '\u2043',
           '\u204C',
           '\u204D',
           '\u2219',
           '\u25A0',
           '\u25A1',
           '\u25A2',
           '\u25A3',
           '\u25A4',
           '\u25A5',
           '\u25A6',
           '\u25A7',
           '\u25A8',
           '\u25A9',
           '\u25AA',
           '\u25AB',
           '\u25AC',
           '\u25AD',
           '\u25AE',
           '\u25AF',
           '\u25CB',
           '\u25CF',
           '\u25E6',
           '\u25C6',
           '\u25C7',
           '\u25C8',
           '\u25C9',
           '\u25CA',
           '\u25CB',
           '\u25D0',
           '\u25D1',
           '\u25D2',
           '\u25D3',
           '\u25D4',
           '\u25D5',
           '\u25D6',
           '\u25D8',
           '\u25D9',
           '\u25E2',
           '\u25E3',
           '\u25E4',
           '\u25E5',
           '\u25E6',
           '\u25EF',
           '\u2611',
           '\u2612',
           '\u2B1B',
           '\u2B1C',
           '\u2B24',
           '\u2B1E',
           '\u2B1F',
           '\u29BE'
           )

COUNTERWORDS = ("reviewsvip",
                "recensiesvip",
                "Hits",
                "hits",
                "hits",
                "hit",
                "Comments",
                "comments",
                "Comment",
                "comment",
                "Views",
                "views",
                "View",
                "view",
                "Reviews",
                "reviews",
                "Review",
                "review",
                "Ratings",
                "ratings",
                "Rating",
                "rating",
                "Likes",
                "likes",
                "Like",
                "like",
                )

CODE_CONFIG = {
    "programming_language_support": [
        "ada",
        "agda",
        "alloy",
        "antlr",
        "applescript",
        "assembly",
        "augeas",
        "awk",
        "batchfile",
        "bluespec",
        "c",
        "csharp",
        "clojure",
        "cmake",
        "coffeescript",
        "commonlisp",
        "cpp",
        "css",
        "cuda",
        "dart",
        "dockerfile",
        "elixir",
        "elm",
        "emacslisp",
        "erlang",
        "fsharp",
        "fortran",
        "gisl",
        "go",
        "groovy",
        "haskell",
        "html",
        "idris",
        "isabelle",
        "java",
        "javaserverpages",
        "javascript",
        "json",
        "julia",
        "kotlin",
        "lean",
        "literateagda",
        "literatecoffeescript",
        "literatehaskell",
        "lua",
        "makefile",
        "maple",
        "markdown",
        "mathematica",
        "matlab",
        "ocaml",
        "pascal",
        "perl",
        "php",
        "powershell",
        "prolog",
        "protocolbuffer",
        "python",
        "r",
        "racket",
        "restructuredtext",
        "rmarkdown",
        "ruby",
        "rust",
        "sas",
        "scala",
        "scheme",
        "shell",
        "smalltalk",
        "solidity",
        "sparql",
        "sql",
        "stan",
        "standardml",
        "stata",
        "systemverilog",
        "tel",
        "tcsh",
        "tex",
        "thrift",
        "typescript",
        "verilog",
        "vhdl",
        "visualbasic",
        "xslt",
        "yacc",
        "yaml",
        "zig"
    ],
    "natural_language_support":[
        "text",
        "markdown",
    ]
}
