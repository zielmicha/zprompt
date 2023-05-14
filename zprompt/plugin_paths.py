import subprocess, glob, os
from zprompt.core import Suggestion, ObjectInfo

# /etc/passwd

def extract_path_from_word(word):
    if '~/' in word:
        return '~/' + word.split('~/', 1)[1]
    elif '/' in word:
        return '/' + word.split('/', 1)[1]
    else:
        return None

def append_slash_to_dirs(paths):    
    return [
        path + '/' if os.path.isdir(path) else path 
        for path in paths
    ]
    
def my_glob(path):
    if path.startswith('~/'):
        home = os.environ['HOME']
        if not home.endswith('/'): home += '/'
        res = append_slash_to_dirs(glob.glob(home + path[2:]))

        return [ '~/' + result[len(home):] if result.startswith(home) else result for result in res ]
    else:
        return append_slash_to_dirs(glob.glob(path))
    
def suggest_path_completions(state, prompts):
    word = prompts['word-to-cursor']
    path = extract_path_from_word(word)
    if path:
        found_paths = my_glob(path + '*')
        
        return [
            Suggestion(prompts['word-start'], found)
            for found in found_paths
        ]
    else:
        return []
    

def path_info(state, prompts):
    word = prompts['word']
    path = extract_path_from_word(word)
    print('path_info', repr(path))
    
    if path:
        path = os.path.expanduser(path)
        try:
            out = subprocess.check_output(['stat', '--', path])
        except subprocess.CalledProcessError:
            return []
        
        return [ObjectInfo(out.decode('utf8', 'replace'))]
    else:
        return []
    
def process_prompt(state, prompts):
    return suggest_path_completions(state, prompts) + path_info(state, prompts)
