from __future__ import print_function
import sys
import kvdb

def eprint(*args, **wsargs):
    return print(*args, file = sys.stderr, **wsargs)

def usage():
    print("Usage:")
    print("\tpython -m access DBNAME get 'KEY'")
    print("\tpython -m access DBNAME set 'KEY' 'VALUE'")
    print("\tpython -m access DBNAME delete 'KEY'")
    print("\tpython -m access DBNAME list")

def main(argv):
    if argv[-1] == "list":
        db = kvdb.connect(argv[-2])
        db.listAll()
        return True
    if len(argv) < 4 or len(argv) > 5:
        usage()
        return False
    dbname, verb, key, value = (argv[1:] + [None])[:4]
    if verb not in {'get', 'set', 'delete'}:
        return False
    db = kvdb.connect(dbname)
    try:
        if verb == 'get':
            if db[key]:
                print(key,":", db[key])
            else:
                print("key not found")
        elif verb == 'set':
            db[key] = value
            print("key/value added/updated")
        else:
            del db[key]
            print(key, "removed")
    except KeyError:
        print("key not found")
        return False
    return True

if __name__ == '__main__':
    result = main(sys.argv)
    if result:
        sys.exit(0)