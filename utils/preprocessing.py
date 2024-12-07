from artifacts.extension_to_program import EXTENSION_TO_PROGRAM
from artifacts.filename_to_program import FILENAME_TO_PROGRAM
from artifacts.program_to_type import PROGRAM_TO_TYPE



excluded_code_langs = ['adblock filter list', 'pic', 'postscript', 'purebasic', 'roff manpage', 'unity3d asset', 'wavefront object', 'pickle', 'stl', 'raw token data', 'x pixmap', 
                       '2-dimensional array', 'ags script', 'bicep', 'checksums', 'collada', 'csv', 'directx 3d file', 'e-mail', 'g-code',
                       'Gerber Image', 'git revision list', 'gnuplot', 'Checksums', 'irc log', 'jupyter notebook', 'kicad layout', 'kicad legacy layout',
                       'kicad schematic', 'lasso', 'linux kernel module', 'max', 'microsoft developer studio project', 'microsoft visual studio solution',
                       'pov-ray sdl', 'public key', 'pure data', 'robots.txt', 'subrip text', 'svg', 'tsv', 'webvtt']


def get_program_lang(filename:str, extension:str):
    if filename in FILENAME_TO_PROGRAM:
        return FILENAME_TO_PROGRAM[filename]
    if extension in EXTENSION_TO_PROGRAM:
        return EXTENSION_TO_PROGRAM[extension]
    return "unknown"

def get_doc_type(program_lang:str):
    if program_lang in excluded_code_langs:
        return "excluded"
    if program_lang in PROGRAM_TO_TYPE:
        return PROGRAM_TO_TYPE[program_lang]
    return "unknown"