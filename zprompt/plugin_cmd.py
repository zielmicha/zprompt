import subprocess, glob, os, time, itertools
from zprompt.core import Suggestion, ObjectInfo
from zprompt.common import is_int, read_json, time_span_to_hum

def render(filename):
    meta = read_json(filename + '.meta.json')

    data = 'command '
    if 'finished_at' in meta:
        data += '(finished in %s)' % (time_span_to_hum(meta['finished_at'] - meta['start']))
    else:
        data += '(running for %s)' % (time_span_to_hum(time.time() - meta['start']))

    try:
        lines = list(itertools.islice(open(filename, 'rb'), 1, 3))
    
        data += '\n'
        data += (b'\n'.join(lines).strip()).decode('utf8', 'replace')
    except IOError:
        data += '[failed to read output]'
        
    return ObjectInfo(data=data)

def process_prompt(state, prompts):
    word = prompts['word']
    if word.startswith('$out/'):
        id = word[len('$out/'):]
        if is_int(id):
            filename = state['filename'] + '.out/' + id

            if os.path.exists(filename) and os.path.exists(filename + '.meta.json'):
                
                return [render(filename)]
        
    return []
