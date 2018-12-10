import os
from storage import Storage
from binarytree import BinaryTree

class DB(object):
    def __init__(self, f):
        self.storage = Storage(f)
        self.tree = BinaryTree(self.storage)

    def assert_not_closed(self):
        if self.storage.closed:
            print("db closed")
            raise ValueError("db closed")

    def close(self):
        self.storage.close()

    def update(self):
        self.assert_not_closed()
        self.tree.update()

    def __getitem__(self, key):
        self.assert_not_closed()
        return self.tree.get(key)

    def __setitem__(self, key, value):
        self.assert_not_closed()
        return self.tree.set(key, value)

    def __delitem__(self, key):
        self.assert_not_closed()
        return self.tree.delete(key)

    def __contains__(self, key):
        self.assert_not_closed()
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __len__(self):
        return len(self.tree)

    def listAll(self):
        return self.tree.listAll()

def connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR|os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DB(f)