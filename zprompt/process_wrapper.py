import os, urllib.parse, re, json, time, subprocess, sys, string, shlex
from zprompt.expect_test import expect, test_case
from zprompt.prompts import load_state, extract_around_cursor, state_path
from zprompt.common import read_json, open_log_as_stderr, update_json

def get_ssh_hosts():
    ssh_config = os.path.expanduser('~/.ssh/config')
    for line in open(ssh_config).read().splitlines():
        if line.startswith('Host '):
            hostname = line.split()[1]
            if '*' in hostname: continue
            yield hostname

def make_command(command_runner, rest):
    if command_runner == 'b':
        return ['sh', '-c', rest]
    elif command_runner in list(get_ssh_hosts()):
        return ['ssh', '-t', command_runner, rest]
    else:
        return ['echo', 'unknown command_runner %r' % command_runner]

def main(out_filename):
    meta_filename = out_filename + '.meta.json'
    meta = read_json(meta_filename)
    title = out_filename
    sys.stdout.write('\33]0;%s\a' % (title, ))
    sys.stdout.flush()
    command = meta['command']
    split = command.split(None, 1)
    if len(split) == 1:
        split += ('',)
    command_runner, rest = split

    wrapped_command = make_command(command_runner, rest)
    
                
    r = subprocess.run([
        'script',
        '--flush',
        '--quiet',
        '--return',
        '--command',
        ' '.join([ shlex.quote(cmd) for cmd in wrapped_command ]),
        out_filename])

    if r.returncode != 0:
        print('[result: %d]' % r.returncode)

    with update_json(meta_filename) as data:
        data['finished_at'] = time.time()
        
if __name__ == '__main__':
    main(sys.argv[1])


