import binascii, os, json, sys, contextlib, re

def write_file(path, data):
    tmp_path = path + '.tmp.' + binascii.hexlify(os.urandom(6)).decode()
    if isinstance(data, str):
        data = data.encode('utf8')
    with open(tmp_path, 'wb') as f:
        f.write(data)

    os.rename(tmp_path, path)

def read_file(path):
    with open(path, 'r') as f: return f.read()

def read_json(path):
    return json.loads(read_file(path))

def write_json(path, data):
    write_file(path, json.dumps(data))

@contextlib.contextmanager
def update_json(path):
    data = read_json(path)
    yield data
    write_json(path, data)
    
def open_log_as_stderr():
    sys.stderr = open(os.path.expanduser('~/var/zprompt/log.txt'), 'a', 1)

def is_int(x):
    try: int(x, 10)
    except ValueError: return False
    else: return True

def time_span_to_hum(x):
    if x < 1:
        return '%.1fms' % (x/1000)
    elif x < 60:
        return '%.2fs' % x
    elif x < 3600:
        return '%.2fm' % (x/60)
    else:
        return '%.2fh' % (x/3600)

# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
_ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
def remove_ansi_escape(x):
    return _ansi_escape.sub('', x)
