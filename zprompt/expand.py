import os, urllib.parse, re, json, time, subprocess, sys, string
from zprompt.expect_test import expect, test_case
from zprompt.core import Suggestion, ObjectInfo
from zprompt.prompts import load_state, extract_around_cursor, state_path
from zprompt.common import read_json

def main():
    state = load_state()
    point = state['point']-1
    shortcut = sys.argv[1]
    allocated_shortcuts = read_json(state_path + '/allocated_shortcuts.json')
            
    if shortcut in allocated_shortcuts:
        suggestion = allocated_shortcuts[shortcut]
        insert_at = suggestion['start']

        text = suggestion['text']

        while text and insert_at < point and text[0] == state['data'][insert_at]:
            text = text[1:]
            insert_at += 1

        print(json.dumps({
            'point': insert_at + 1,
            'text': text,
        }))

# /etc/pass
# (read-from-minibuffer "shortcut:")
        
if __name__ == '__main__':
    main()
