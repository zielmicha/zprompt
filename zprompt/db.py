import psycopg2.extras, contextlib, os, getpass
import polars as pl

@contextlib.contextmanager
def make_conn():
    name = getpass.getuser()
    with psycopg2.connect("dbname=%s user=%s host=%s" % (name, name, os.path.expanduser('~/var/postgresql'))) as db_conn:
        psycopg2.extras.register_hstore(db_conn)
        yield db_conn
        
def query(*args):
    with make_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(*args)
        return pl.DataFrame(list( dict(i) for i in cur))

if __name__ == '__main__':
    print(query('select 1 as foo'))
