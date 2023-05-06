import subprocess, glob, os

# /etc/passwd

def suggest_paths(state, prompts):
    word = prompts['word-to-cursor']
    print(prompts)
    if '/' in word:
        if '~/' in word:
            path = '~/' + word.split('~/', 1)[1]
        else:
            path = '/' + word.split('/', 1)[1]
        found_paths = glob.glob(os.path.expanduser(path) + '*')
        return [
            (prompts['word-start'], found)
            for found in found_paths
        ]
    else:
        return []
    
