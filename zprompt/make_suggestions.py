import os, urllib.parse, re, json, time, subprocess, sys, string
from zprompt.expect_test import expect, test_case
from zprompt import fzflike
from zprompt import suggest_paths

state_path = os.path.expanduser('~/var/emacs-state')

def load_state():
    point = json.load(open(state_path + '/point.json'))
    filename = point['buffer']
    quoted_filename = state_path + '/' + urllib.parse.quote(filename, safe='') if filename is not None else None
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
single_word_re = re.compile(r'(\w|[/~-])+', re.MULTILINE)

def extract_around_cursor(state):
    print(state['point'])
    pos = state['point'] - 1
    data = state['data']

    line_start, line = _extract_around(data, pos, single_line_re)
    line_to_cursor = data[line_start : pos]
    word_start, word = _extract_around(data, pos, single_word_re)
    word_to_cursor = data[word_start : pos]
    
    return {
        'line': line,
        'line-start': line_start,
        'line-to-cursor': line_to_cursor,
        'word-to-cursor': word_to_cursor,
        'word-start': word_start,
        'word': word
    }
    

@test_case
def test_extract_around_cursor():
    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 4,
    }))
    expect(r'''4
{'line': 'hello', 'line-start': 2, 'line-to-cursor': 'h', 'word-to-cursor': 'h', 'word-start': 2, 'word': 'hello'} ''')

    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 2,
    }))
    expect(r'''2
{'line': 'x', 'line-start': 0, 'line-to-cursor': 'x', 'word-to-cursor': 'x', 'word-start': 0, 'word': 'x'} ''')

    print(extract_around_cursor({
        'data': 'x\nhello\nyy',
        'point': 3,
    }))
    expect(r'''3
{'line': 'hello', 'line-start': 2, 'line-to-cursor': '', 'word-to-cursor': '', 'word-start': 2, 'word': 'hello'} ''')

    print(extract_around_cursor({
        'data': 'single line',
        'point': 3,
    }))
    expect(r'''3
{'line': 'single line', 'line-start': 0, 'line-to-cursor': 'si', 'word-to-cursor': 'si', 'word-start': 0, 'word': 'single'} ''')

    print(extract_around_cursor({
        'data': 'h=/etc/passwd',
        'point': 7,
    }))
    expect(r'''7
{'line': 'h=/etc/passwd', 'line-start': 0, 'line-to-cursor': 'h=/etc', 'word-to-cursor': '/etc', 'word-start': 2, 'word': '/etc/passwd'} ''')


    
def refresh(state):
    prompts = extract_around_cursor(state)
    suggestions = suggest_paths.suggest_paths(state, prompts)
    print(suggestions)

    return suggestions

shortcuts = [ (s, None) for s in string.ascii_lowercase ]

def allocate_shortcut(completion):
    for i, (shortcut, shortcut_completion) in enumerate(list(shortcuts)):
        if shortcut_completion == completion:
            del shortcuts[i]
            shortcuts.append((shortcut, shortcut_completion))
            return shortcut

    shortcut, _ = shortcuts[0]
    del shortcuts[0]
    shortcuts.append((shortcut, completion))
    return shortcut

def render(output, suggestions):
    height, width = os.get_terminal_size()

    data = '\n'.join( repr((allocate_shortcut(s), s)) for s in suggestions[:height-1] )
    
    output.write('\x1b[H\x1b[2J\x1b[3J' + data)
    output.flush()

def main():
    prev_state = None
    output = sys.stdout
    sys.stdout = sys.stderr = open(os.path.expanduser('~/var/emacs-state/log.txt'), 'w', 1)
    while True:
        time.sleep(0.05)
        state = load_state()
        if state != prev_state:
            suggestions = refresh(state)
            render(output, suggestions)
            prev_state = state

if __name__ == '__main__':
    main()
