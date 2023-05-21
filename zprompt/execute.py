import os, urllib.parse, re, json, time, subprocess, sys, string, datetime, pipes, pathlib
from zprompt.expect_test import expect, test_case
from zprompt.core import Suggestion, ObjectInfo
from zprompt.prompts import load_state, extract_around_cursor, state_path
from zprompt.common import read_json, open_log_as_stderr, write_json

def strip_code_block(x):
    x = x.strip()
    if x.startswith('$[[') and x.endswith(']]'):
        return x[3:-2].strip()
    else:
        return x.lstrip('$').strip()

def is_int(x):
    try:
        int(x)
    except ValueError: return False
    else: return True
    
def allocate_filename(out_dir):
    taken = [ int(name) for name in os.listdir(out_dir) if is_int(name) ]
    taken.append(0)
    new_id = max(taken) + 1
    new_path = out_dir + '/' + str(new_id)
    pathlib.Path(new_path).touch(exist_ok=False)
    return new_id, new_path

def main():
    open_log_as_stderr()
    
    state = load_state()
    prompts = extract_around_cursor(state)
    point = state['point']-1
    
    code_block = prompts['code-block']
    target_pos = prompts['code-block-start'] + len(code_block)

    command = strip_code_block(code_block)
    
    out_dir = pipes.quote(state['filename'] + '.out')
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    id, out_filename = allocate_filename(out_dir)

    write_json(out_filename + '.meta.json', {
        'command': command,
        'start': time.time(),
    })

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    insert_text = '\n$out/%d (%s)' % (id, now_str)

    print(json.dumps({
        'point': target_pos + 1,
        'text': insert_text,
        'launch-command': pipes.quote(out_filename),
    }))
        

if __name__ == '__main__':
    main()
