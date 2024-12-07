import re
import jieba
import nltk
import pygments.token
import zhconv
import pygments
from pygments.lexers import get_lexer_by_name
from typing import Tuple
from functools import partial
from itertools import chain

from redpajama.core.document import Document, split_paragraphs, _compute_ngrams
from redpajama.core.data_types import TextSlice

from utils.text_utils import normalize_text
from artifacts.extension_to_program import EXTENSION_TO_PROGRAM
from artifacts.filename_to_program import FILENAME_TO_PROGRAM


import sys
sys.setrecursionlimit(10000)  # increase the recursive depth limit to 10000


# English and other tokenizer
def _nltk_tokenize(x): return nltk.wordpunct_tokenize(x)
# Chinese tokenizer
def _jieba_tokenize(x): return [w for w in jieba.lcut(x) if w.strip()]
# Japanese tokenizer
def _mecab_tokenize(x): 
    import MeCab
    mecab = MeCab.Tagger("-Owakati")
    result = mecab.parse(x)
    if not result:
        result = ""
    return result.strip().split()

class QSCodeDocument(Document):
    def __init__(
            self, 
            content:str,
            filename: str,
            language: str,
            extension: str,
            file_size_in_byte: int,
            program_lang: str,
            doc_type: str,
    ):
        
        # initialize the document general attributes
        self.init_doc_attributes(content, language)
        # initialize the code specific attributes
        self.init_code_attributes(
            filename, 
            extension, 
            file_size_in_byte, 
            program_lang, 
            doc_type
        )

    def init_doc_attributes(self, content, language):
        self._lang = language

        if language == 'zh':
            self._raw_content = zhconv.convert(content, 'zh-cn')
            self._len_raw_content = len(content)
            self.tokenize_func = _jieba_tokenize
        elif language == 'ja':
            self._raw_content = content
            self._len_raw_content = len(content)
            self.tokenize_func = _mecab_tokenize
        else:
            self._raw_content = content
            self._len_raw_content = len(content)
            self.tokenize_func = _nltk_tokenize


        self._normalize_func = partial(normalize_text,
                                       remove_control=True,
                                       halfpunct=True,
                                       punct='replace',
                                       lowercase=True,
                                       white_space=True,
                                       unicode='NFKC',
                                       remove_zh_whitespace=False,
                                       remove_digits=False)

        self._normalized_content = None
        self._raw_lines = None
        self._normalized_lines = None
        self._raw_words_in_line = None
        self._raw_words = None
        self._normalized_words_in_line = None
        self._normalized_words = None
        self._num_raw_words = None
        self._num_normalized_words = None
        self._raw_2grams = None
        self._raw_3grams = None
        self._norm_2grams = None
        self._norm_3grams = None
        self._norm_4grams = None

    def init_code_attributes(self, filename, extension, file_size_in_byte, program_lang, doc_type):
        self.filename = filename
        self._extension = extension
        self._file_size_in_byte = file_size_in_byte
        self._program_lang = program_lang
        self._doc_type = doc_type

        self._ast = None
        self._is_code = None

        # code content without comment
        self._code_raw_content = None
        self._code_raw_lines = None
        self._code_normalized_lines = None

        # comment content without code
        self._comment_raw_content = None
        self._comment_raw_lines = None
        self._comment_normalized_lines = None

        # content without blank characters
        self._visiable_content = None


    def __len__(self):
        return self._len_raw_content
    
    @classmethod
    def get_program_language(cls, extension, filename=''):
        if filename in FILENAME_TO_PROGRAM:
            return FILENAME_TO_PROGRAM[filename]
        if extension in EXTENSION_TO_PROGRAM:
            return EXTENSION_TO_PROGRAM[extension]
        return "unknown"
    

    @property
    def language(self):
        return self._lang

    @property
    def raw_content(self):
        return self._raw_content

    @property
    def normalized_content(self):
        if not self._normalized_content:
            # the normalized content: lowercased and punctuation removed
            self._normalized_content = ' '.join([l.text for l in self.normalized_lines])
        return self._normalized_content

    @property
    def raw_lines(self):
        if not self._raw_lines:
            # the lines of the document (split by newline)
            self._raw_lines: Tuple[TextSlice] = split_paragraphs(
                text=self.raw_content, normalizer=lambda x: x, remove_empty=False
            )
        return self._raw_lines

    @property
    def normalized_lines(self):
        if not self._normalized_lines:
            # the lines of the document (split by newline), normalized
            self._normalized_lines: Tuple[TextSlice] = split_paragraphs(
                text=self.raw_content, normalizer=self._normalize_func, remove_empty=False
            )
        return self._normalized_lines

    @property
    def raw_words_in_line(self):
        if not self._raw_words_in_line:
            self._raw_words_in_line = tuple(tuple(self.tokenize_func(textslice.text)) for textslice in self.raw_lines)
        return self._raw_words_in_line

    @property
    def raw_words(self):
        if not self._raw_words:
            self._raw_words = tuple(chain(*self.raw_words_in_line))
        return self._raw_words

    @property
    def normalized_words_in_line(self):
        if not self._normalized_words_in_line:
            # the normalized words of the document (split by whitespace)
            if self._lang == 'zh':
                self._normalized_words_in_line = tuple(tuple(self.tokenize_func(textslice.text)) for textslice in self.normalized_lines)
            else:
                self._normalized_words_in_line = tuple(tuple(self.tokenize_func(textslice.text)) for textslice in self.normalized_lines)
        return self._normalized_words_in_line

    @property
    def normalized_words(self):
        if not self._normalized_words:
            self._normalized_words = tuple(chain(*self.normalized_words_in_line))
        return self._normalized_words

    @property
    def num_raw_words(self):
        if not self._num_raw_words:
            self._num_raw_words = len(self.raw_words)
        return self._num_raw_words

    @property
    def num_normalized_words(self):
        if not self._num_normalized_words:
            self._num_normalized_words = len(self.normalized_words)
        return self._num_normalized_words

    @property
    def raw_1grams(self):
        return self._raw_words

    @property
    def raw_2grams(self):
        if not self._raw_2grams:
            self._raw_2grams = _compute_ngrams(self.raw_words, 2)
        return self._raw_2grams

    @property
    def raw_3grams(self):
        if not self._raw_3grams:
            self._raw_3grams = _compute_ngrams(self.raw_words, 3)
        return self._raw_3grams

    @property
    def norm_1grams(self):
        return self.normalized_words

    @property
    def norm_2grams(self):
        if not self._norm_2grams:
            self._norm_2grams = _compute_ngrams(self.normalized_words, 2)
        return self._norm_2grams

    @property
    def norm_3grams(self):
        if not self._norm_3grams:
            self._norm_3grams = _compute_ngrams(self.normalized_words, 3)
        return self._norm_3grams

    @property
    def norm_4grams(self):
        if not self._norm_4grams:
            self._norm_4grams = _compute_ngrams(self.normalized_words, 4)
        return self._norm_4grams
    
    @property
    def visible_content(self):
        if not self._visiable_content:
            self._visiable_content = re.sub(r'\s+', '', self.raw_content)
        return self._visiable_content

    @property
    def extension(self):
        return self._extension

    @property
    def program_lang(self):
        if self._program_lang is None:
            self._program_lang = self.get_program_language(self.extension)
        return self._program_lang
    
    @property
    def doc_type(self):
        return self._doc_type
    
    @property
    def file_size_in_byte(self):
        return self._file_size_in_byte
    
    @property
    def code_raw_content(self):
        if self.program_lang is None:
            self._comment_raw_content = self.raw_content
            self._code_raw_content = self.raw_content
            return self._code_raw_content

        if self._code_raw_content:
            return self._code_raw_content

        if self.program_lang == 'perl':
            self._code_raw_content, self._comment_raw_content = self.get_perl_comment()
            return self._code_raw_content

        if self.program_lang == 'python':
            pass

        code_raw_content = ""
        comment_raw_content = ""
        try:
            #1. parse by pygments lexer
            lexer = get_lexer_by_name(self.program_lang)
            tokens = pygments.lex(self.raw_content, lexer)
            for token_type, token in tokens:
                if not (
                    token_type == pygments.token.Comment.Multiline
                    or token_type == pygments.token.Comment.Single
                    or token_type == pygments.token.Literal.String.Doc
                    or token_type == pygments.token.Comment.Hashbang
                    or token_type == pygments.token.Comment.Special
                ):
                    code_raw_content += token
                else:
                    comment_raw_content += token

        except pygments.util.ClassNotFound:
            #2. parse by hand
            code_raw_content, comment_raw_content = self.get_comment_by_hand()
        
        self._code_raw_content = code_raw_content
        self._comment_raw_content = comment_raw_content
        return self._code_raw_content

    @property
    def comment_raw_content(self):
        if not self._comment_raw_content:
            # comment and code are simultanoeusly generated
            self.code_raw_content
        return self._comment_raw_content
    
    @property
    def code_normalized_lines(self):
        if not self._code_normalized_lines:
            self._code_normalized_lines = split_paragraphs(text=self.code_raw_content,normalizer=lambda x:x, remove_empty=True)
        return self._code_normalized_lines
    
    @property
    def comment_normalized_lines(self):
        if not self._comment_normalized_lines:
            self._comment_normalized_lines = split_paragraphs(text=self.comment_raw_content,normalizer=lambda x:x, remove_empty=True)
        return self._comment_normalized_lines

    # remove blank characters
    @property
    def visible_content(self):
        if not self._visiable_content:
            self._visiable_content = re.sub(r'\s+', '', self.raw_content)
        return self._visiable_content
    
    @property
    def valid_lines_len(self):
        return len(self.code_normalized_lines)

    @property
    def ast(self):
        from utils.code.js_utils import parse_js
        from utils.code.python_utils import parse_py
        from utils.code.html_utils import parse_html
        if not self._ast:
            if self.program_lang == 'javascript':
                self._ast = parse_js(self.raw_content)
            elif self.program_lang == 'python':
                self._ast = parse_py(self.raw_content)
            elif self.program_lang == 'html':
                self._ast = parse_html(self.raw_content)
        return self._ast

    def get_comment_by_hand(self):
        code_raw_content = ""
        comment_raw_content = ""
        in_multiline_comment = False
        comment_flag = False
        for line in self.raw_lines:
            strip_line = line.text.strip()
            if strip_line.startswith(('"""','/*')) or strip_line.endswith(('"""', '*/')):
                in_multiline_comment = not in_multiline_comment
                comment_flag = in_multiline_comment
                comment_raw_content += line.text
                continue
            if strip_line.startswith(('#','//','--')) or in_multiline_comment:
                in_multiline_comment = True
                comment_raw_content += line.text
                continue
            if strip_line == '\n' and comment_flag:
                comment_raw_content += line.text
                continue
            
            comment_flag = False
            code_raw_content += line.text
        return code_raw_content, comment_raw_content

    def get_perl_comment(self):
        code_raw_content = ""
        comment_raw_content = ""
        in_multiline_comment = False
        comment_flag = False
        for line in self.raw_lines:
            strip_line = line.text.strip()
            if strip_line.startswith('=cut'):
                in_multiline_comment = False
                comment_flag = False
                comment_raw_content += line.text
                continue
            if strip_line.startswith('='):
                in_multiline_comment = True
                comment_flag = True
                comment_raw_content += line.text
                continue
            if strip_line.startswith('#') or in_multiline_comment:
                comment_raw_content += line.text
                continue
            if strip_line == '\n' and comment_flag:
                comment_raw_content += line.text
                continue
            comment_flag = False
            code_raw_content += line.text
        return code_raw_content, comment_raw_content