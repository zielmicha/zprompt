import os, urllib.parse, re, json, time, subprocess, sys, string
from zprompt.expect_test import expect, test_case
from zprompt import fzflike
from zprompt.core import Suggestion, ObjectInfo
from zprompt.prompts import load_state, extract_around_cursor, state_path
from zprompt.common import read_file, write_file

def get_plugins():
    from zprompt import plugin_paths, plugin_cmd
    return [plugin_paths, plugin_cmd]
    
def refresh(state):
    prompts = extract_around_cursor(state)
    results = []
    for p in get_plugins():
        results += p.process_prompt(state, prompts)

    if prompts['code-block']:
        results.append(ObjectInfo(prompts['code-block']))

    return results

shortcuts = [ (s1 + s2, None) for s1 in string.ascii_lowercase for s2 in string.ascii_lowercase ]

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

def render_suggestion(shortcut, suggestion):
    return shortcut + ' ' + suggestion.text

def save_allocated(allocated):
    write_file(state_path + '/allocated_shortcuts.json' , json.dumps([  {'start': s.start, 'text': s.text, 'shortcut': shortcut}   for shortcut, s in allocated ]))

def render(output, results):
    width, height = os.get_terminal_size()

    suggestions = [ r for r in results if isinstance(r, Suggestion) ]
    object_infos = [ r for r in results if isinstance(r, ObjectInfo) ]

    object_info_data = '\n-------\n'.join( [ r.data for r in object_infos] + [''] )
    
    remaining_height = height - object_info_data.count('\n')
    print('heights', height, remaining_height)
    

    allocated = [ (allocate_shortcut(s), s) for s in suggestions[:remaining_height-1] ]

    save_allocated(allocated)
    
    suggestion_data = '\n'.join( render_suggestion(shortcut, suggestion) for shortcut, suggestion in allocated )
    
    output.write('\x1b[H\x1b[2J\x1b[3J' + object_info_data + suggestion_data)
    output.flush()

def main():
    prev_state = None
    output = sys.stdout
    sys.stdout = sys.stderr = open(os.path.expanduser('~/var/zprompt/log.txt'), 'w', 1)
    while True:
        time.sleep(0.05)
        
        try:
            state = load_state()
        except Exception as ex:
            print(ex)
            continue
        
        if state != prev_state:
            results = refresh(state)
            render(output, results)
            prev_state = state

if __name__ == '__main__':
    main()
