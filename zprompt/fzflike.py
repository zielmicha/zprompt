import sys
from zprompt.expect_test import expect, test_case

def all_exist_in_order(words, line):
    for word in words:
        pos = line.find(word)
        if pos == -1: return False
        line = line[pos+len(word):]
    return True

@test_case
def test_all_exist_in_order():
    print(all_exist_in_order(['hello', 'world', 'boo'], 'hello xx world boo'))
    expect(r'''True ''')

    print(all_exist_in_order(['hello', 'world', 'boo'], 'hello boo world'))
    expect(r'''False ''')
    
def score_match(query, line):
    if line in query:
        return 3.

    words = query.split()
    if all_exist_in_order(words, line):
        return 2.

    return sum( w in line for w in words ) / len(words)    

def query(query):
    lines = open('/home/michal/.zsh_history', 'rb')
    for line in lines:
        if query in line.decode('utf8', 'replace'):
            pass

if __name__ == '__main__':
    query(sys.argv[1])
