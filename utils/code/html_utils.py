from bs4 import BeautifulSoup
from document import QSCodeDocument


def parse_html(content: str):
    try:
        soup = BeautifulSoup(content, features='html.parser')
    except TimeoutError:
        raise TimeoutError("timeout")
    except:
        soup = None
    return soup