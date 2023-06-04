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

def join_command(args):
    return ' '.join([ shlex.quote(cmd) for cmd in args ])
            
def make_command(command_runner, rest):
    if command_runner == 'py' or command_runner.startswith('py:'):
        cmd = ['python3', '-c', rest]
        if command_runner == 'py':
            return cmd
        else:
            return make_command(command_runner[3:], join_command(cmd))
    elif command_runner == 'b':
        return ['sh', '-c', rest]
    elif command_runner in list(get_ssh_hosts()):
        return ['ssh', '-t', command_runner, rest]
    else:
        return ['echo', 'unknown command_runner %r' % command_runner]

def main(out_filename):
    os.chdir(os.path.dirname(os.path.dirname(out_filename)))
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
    
    print('[running]', command_runner, rest)
    r = subprocess.run([
        'script',
        '--flush',
        '--quiet',
        '--return',
        '--command',
        join_command(wrapped_command),
        out_filename])

    print('[result: %d]' % r.returncode)

    with update_json(meta_filename) as data:
        data['exit_code'] = r.returncode
        data['finished_at'] = time.time()
        
if __name__ == '__main__':
    main(sys.argv[1])


