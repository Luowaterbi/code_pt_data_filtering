from bs4 import BeautifulSoup


def parse_html(content: str):
    try:
        soup = BeautifulSoup(content, features='html.parser')
    except TimeoutError:
        raise TimeoutError("timeout")
    except:
        soup = None
    return soup