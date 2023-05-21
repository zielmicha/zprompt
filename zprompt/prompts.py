import os, urllib.parse, re, json, time, subprocess, sys, string
from zprompt.expect_test import expect, test_case

state_path = os.path.expanduser('~/var/zprompt')

def load_state():
    point = json.load(open(state_path + '/point.json'))
    filename = point['buffer']
    quoted_filename = state_path + '/files/' + urllib.parse.quote(filename, safe='') if filename is not None else None
    data = ''
    if quoted_filename and os.path.exists(quoted_filename):
        data = open(quoted_filename).read()

    return dict(point=point['point'], filename=filename, data=data)

def _extract_around(data, pos, regex):
    result = pos, ''
    for m in re.finditer(regex, data):
        if m.start() > pos:
            break
        result = m.start(), m.group(0)

    return result

single_line_re = re.compile(r'^.*$', re.MULTILINE)
single_word_re = re.compile(r'(\w|[./~$-])+', re.MULTILINE)
code_block_re = re.compile(r'^\$\[\[(.*?)\]\]$', re.MULTILINE | re.DOTALL)

def extract_around_cursor(state):
    pos = state['point'] - 1
    data = state['data']

    line_start, line = _extract_around(data, pos, single_line_re)
    line_to_cursor = data[line_start : pos]
    word_start, word = _extract_around(data, pos, single_word_re)
    word_to_cursor = data[word_start : pos]

    code_block_start, code_block = _extract_around(data, pos, code_block_re)
    if not code_block and line.startswith('$'):
        code_block = line
        code_block_start = line_start

    return {
        'line': line,
        'line-start': line_start,
        'line-to-cursor': line_to_cursor,
        'word-to-cursor': word_to_cursor,
        'word-start': word_start,
        'word': word,
        'code-block': code_block,
        'code-block-start': code_block_start,
    }
    

@test_case
def test_extract_around_cursor():
    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 4,
    }))
    expect(r'''4
{'line': 'hello', 'line-start': 2, 'line-to-cursor': 'h', 'word-to-cursor': 'h', 'word-start': 2, 'word': 'hello', 'code-block': ''} ''')

    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 2,
    }))
    expect(r'''2
{'line': 'x', 'line-start': 0, 'line-to-cursor': 'x', 'word-to-cursor': 'x', 'word-start': 0, 'word': 'x', 'code-block': ''} ''')

    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 3,
    }))
    expect(r'''3
{'line': 'hello', 'line-start': 2, 'line-to-cursor': '', 'word-to-cursor': '', 'word-start': 2, 'word': 'hello', 'code-block': ''} ''')

    print(extract_around_cursor({
        'data': 'single line',
        'point': 3,
    }))
    expect(r'''3
{'line': 'single line', 'line-start': 0, 'line-to-cursor': 'si', 'word-to-cursor': 'si', 'word-start': 0, 'word': 'single', 'code-block': ''} ''')

    print(extract_around_cursor({
        'data': 'h=/etc/passwd',
        'point': 7,
    }))
    expect(r'''7
{'line': 'h=/etc/passwd', 'line-start': 0, 'line-to-cursor': 'h=/etc', 'word-to-cursor': '/etc', 'word-start': 2, 'word': '/etc/passwd', 'code-block': ''} ''')
    
    print(extract_around_cursor({
        'data': 'h\n$[[\ncmd 1 2 3\n]]\naaaa\n$[[\nx\n]]\nyy',
        'point': 7,
    }))
    expect(r'''7
{'line': 'cmd 1 2 3', 'line-start': 6, 'line-to-cursor': '', 'word-to-cursor': '', 'word-start': 6, 'word': 'cmd', 'code-block': '$[[\ncmd 1 2 3\n]]'} ''')
