import binascii, os, json

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
