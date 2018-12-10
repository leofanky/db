from storage import Storage
import pickle

# def leftnode(storage, leftaddress):
#     return stringToNode(storage.read(leftaddress))
#
# def rightnode(storage, rightaddress):
#     return stringToNode(storage.read(rightaddress))
def leftnode(storage, leftaddress):
    leftnode = stringToNode(storage.read(leftaddress))
    if leftnode:
        return leftnode
    else:
        return None
        #return BinaryTreeNode(None, None)

def rightnode(storage, rightaddress):
    rightnode = stringToNode(storage.read(rightaddress))
    if rightnode:
        return rightnode
    else:
        return None
        #return BinaryTreeNode(None, None)

class BinaryTreeNode(object):
    def __init__(self, key, value, leftaddress=None, rightaddress=None):
        self.key = key
        self.value = value
        self.leftaddress = leftaddress
        self.rightaddress = rightaddress

    def hasLeftNode(self):
        return self.leftaddress

    def hasRightNode(self):
        return self.rightaddress

    def isLeaf(self):
        return (not self.leftaddress) and (not self.rightaddress)

    def hasOneNode(self):
        return self.leftaddress or self.rightaddress

    def hasBothNode(self):
        return self.leftaddress and self.rightaddress



def nodeToString(node):
    return pickle.dumps(
        {
            'key': node.key,
            'value': node.value,
            'leftaddress': node.leftaddress,
            'rightaddress': node.rightaddress,
        }
    )


def stringToNode(string):
    if string != b'':
        data = pickle.loads(string)
        return BinaryTreeNode(
            data['key'],
            data['value'],
            data['leftaddress'],
            data['rightaddress'],
        )
    else:
        return None


class BinaryTree(object):
    def __init__(self, storage):
        self.storage = storage
        self.rootaddr = self.storage.getRootAddr()
        self.rootnode = stringToNode(self.storage.read(self.rootaddr))
        self.size = 0
        self.parentlist = []


    def length(self):
        return self.size

    def __len__(self):
        return self.size

    def get(self, key):
        if self.rootnode:
            #print(self.rootnode.key)
            node = self._get(key, self.rootnode)
            if node:
                return node.value
            else:
                return None
        else:
            print("no rootnode")
            return None

    def _get(self, key, currentnode):
        if not currentnode.key:
            return None
        elif key < currentnode.key:
            return self._get(key, leftnode(self.storage, currentnode.leftaddress))
        elif currentnode.key < key:
            return self._get(key, rightnode(self.storage, currentnode.rightaddress))
        else:
            return currentnode

    def __getitem__(self, key):
        return self.get(key)

    def set(self, key, value):
        if self.rootnode:
            self._set(key, value, self.rootnode)
        else:
            node = BinaryTreeNode(key, value)
            addr = self.storage.write(nodeToString(node))
            self.rootnode = node
            self.rootaddr = addr
            self.storage.updateRootAddr(self.rootaddr)
        self.size += 1

    def _set(self, key, value, currentnode):
        if key < currentnode.key:
            self.parentlist.append(currentnode)
            if currentnode.hasLeftNode():
                self._set(key, value, leftnode(self.storage, currentnode.leftaddress))
            else:
                node = BinaryTreeNode(key, value)
                nodeaddr = self.storage.write(nodeToString(node))
                self.updateParents(nodeaddr)
        elif currentnode.key < key:
            self.parentlist.append(currentnode)
            if currentnode.hasRightNode():
                self._set(key, value, rightnode(self.storage, currentnode.rightaddress))
            else:
                node = BinaryTreeNode(key, value)
                nodeaddr = self.storage.write(nodeToString(node))
                self.updateParents(nodeaddr)
        else:
            newnode = BinaryTreeNode(currentnode.key, value, currentnode.leftaddress, currentnode.rightaddress)
            if newnode.key == self.rootnode.key:
                self.rootaddr = self.storage.write(nodeToString(newnode))
                self.storage.updateRootAddr(self.rootaddr)
                self.parentlist = []
            else:
                nodeaddr = self.storage.write(nodeToString(newnode))
                self.updateParents(nodeaddr)

    def updateParents(self, currentaddr):
        preaddr = currentaddr
        while len(self.parentlist) > 0:
            curnode = self.parentlist.pop()
            prenode = stringToNode(self.storage.read(preaddr))
            if prenode.key < curnode.key:
                newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            else:
                newnode = BinaryTreeNode(curnode.key, curnode.value, curnode.leftaddress, preaddr)
            preaddr = self.storage.write(nodeToString(newnode))
        self.rootaddr = preaddr
        self.storage.updateRootAddr(self.rootaddr)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        if self._get(key, self.rootnode):
            return True
        else:
            return False

    def delete(self, key):
        if self.rootnode:
            nodetodel, newparentlist = self.getList(key, self.rootnode, [])
            if nodetodel:
                self._delete(nodetodel, newparentlist)
                self.size -= 1
            else:
                raise KeyError("key not found")
        else:
            raise KeyError("key not found")

    def _delete(self, currentnode, newparentlist):
        if len(newparentlist) == 0:
            if currentnode.isLeaf():
                self.rootaddr = None
                self.storage.updateRootAddr(self.rootaddr)
            elif currentnode.leftaddress and currentnode.rightaddress:
                successornode, newparentlist2 = self.getSuccessor(currentnode)
                if successornode:
                    newnode = BinaryTreeNode(successornode.key, successornode.value, currentnode.leftaddress,
                                         currentnode.rightaddress)
                    if len(newparentlist2) == 0:
                        if successornode.hasRightNode():
                            newnode.rightaddress = successornode.rightaddress
                        else:
                            newnode.rightaddress = None
                        self.rootaddr = self.storage.write(nodeToString(newnode))
                        self.storage.updateRootAddr(self.rootaddr)
                    else:
                        print("test p6")
                        self.updateParents6(newparentlist2, newnode, successornode)
            else:
                if currentnode.hasLeftNode():
                    self.rootaddr = currentnode.leftaddress
                    self.storage.updateRootAddr(self.rootaddr)
                else:
                    self.rootaddr = currentnode.rightaddress
                    self.storage.updateRootAddr(self.rootaddr)
        else:
            if currentnode.isLeaf():
                print("test p5")
                self.updateParents5(newparentlist, currentnode)
            elif currentnode.hasBothNode():
                successornode, newparentlist2 = self.getSuccessor(currentnode)
                newnode = BinaryTreeNode(successornode.key, successornode.value, currentnode.leftaddress,
                                     currentnode.rightaddress)
                if len(newparentlist2) == 0:
                    print("test p2")
                    self.updateParents2(newparentlist, newnode, currentnode)
                else:
                    print("test p3")
                    self.updateParents3(newparentlist, newnode, newparentlist2, currentnode)
            else:
                print("test p4")
                self.updateParents4(newparentlist, currentnode)

    def __delitem__(self, key):
        self.delete(key)

    def getList(self, key, currentnode, newparentlist):
        if not currentnode:
            return None, newparentlist
        elif currentnode.key == key:
            return currentnode, newparentlist
        elif key < currentnode.key:
            newparentlist.append(currentnode)
            left = leftnode(self.storage, currentnode.leftaddress)
            return self.getList(key, left, newparentlist)
        else:
            newparentlist.append(currentnode)
            right = rightnode(self.storage, currentnode.rightaddress)
            return self.getList(key, right, newparentlist)

    def getSuccessor(self, currentnode):
        newparentlist2 = []
        minnode = rightnode(self.storage, currentnode.rightaddress)
        #print("1", minnode.key)
        if minnode:
            while minnode.hasLeftNode():
                newparentlist2.append(minnode)
                minnode = leftnode(self.storage, minnode.leftaddress)
        #print("2", minnode.key)
        return minnode, newparentlist2

    def updateParents6(self, newparentlist2, currentnode, oldnode):
        preaddr = oldnode.rightaddress
        while len(newparentlist2) > 0:
            curnode = newparentlist2.pop()
            newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            preaddr = self.storage.write(nodeToString(newnode))
        currentnode.rightaddress = preaddr
        self.rootaddr = self.storage.write(nodeToString(currentnode))
        self.storage.updateRootAddr(self.rootaddr)

    def updateParents2(self, newparentlist, node, oldnode):
        node.rightaddress = rightnode(self.storage, node.rightaddress).rightaddress
        preaddr = self.storage.write(nodeToString(node))
        prenode = oldnode
        while len(newparentlist) > 0:
            curnode = newparentlist.pop()
            if leftnode(self.storage, curnode.leftaddress).key == prenode.key:
                newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            else:
                newnode = BinaryTreeNode(curnode.key, curnode.value, curnode.leftaddress, preaddr)
            preaddr = self.storage.write(nodeToString(newnode))
            prenode = newnode
        self.rootaddr = preaddr
        self.storage.updateRootAddr(self.rootaddr)

    def updateParents3(self, newparentlist, node, newparentlist2, oldnode):
        preaddr = None
        while len(newparentlist2) > 0:
            curnode = newparentlist2.pop()
            newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            preaddr = self.storage.write(nodeToString(newnode))
        newnode = BinaryTreeNode(node.key, node.value, node.leftaddress, preaddr)
        preaddr = self.storage.write(nodeToString(newnode))
        prenode = oldnode
        while len(newparentlist) > 0:
            curnode = newparentlist.pop()
            if leftnode(self.storage, curnode.leftaddress).key == prenode.key:
                newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            else:
                newnode = BinaryTreeNode(curnode.key, curnode.value, curnode.leftaddress, preaddr)
            preaddr = self.storage.write(nodeToString(newnode))
            prenode = newnode
        self.rootaddr = preaddr
        self.storage.updateRootAddr(self.rootaddr)

    def updateParents4(self, newparentlist, currentnode):
        if currentnode.hasLeftNode():
            preaddr = currentnode.leftaddress
        else:
            preaddr = currentnode.rightaddress
        prenode = currentnode
        while len(newparentlist) > 0:
            curnode = newparentlist.pop()
            if leftnode(self.storage, curnode.leftaddress).key == prenode.key:
                newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            else:
                newnode = BinaryTreeNode(curnode.key, curnode.value, curnode.leftaddress, preaddr)
            preaddr = self.storage.write(nodeToString(newnode))
            prenode = newnode
        self.rootaddr = preaddr
        self.storage.updateRootAddr(self.rootaddr)

    def updateParents5(self, newparentlist, currentnode):
        preaddr = None
        prenode = currentnode
        while len(newparentlist) > 0:
            curnode = newparentlist.pop()
            if leftnode(self.storage, curnode.leftaddress).key == prenode.key:
                newnode = BinaryTreeNode(curnode.key, curnode.value, preaddr, curnode.rightaddress)
            else:
                newnode = BinaryTreeNode(curnode.key, curnode.value, curnode.leftaddress, preaddr)
            preaddr = self.storage.write(nodeToString(newnode))
            prenode = newnode
        self.rootaddr = preaddr
        self.storage.updateRootAddr(self.rootaddr)

    def listAll(self):
        all = []
        if self.rootnode:
            print(self.rootnode.key)
            print(self.iter(self.rootnode, all))
        else:
            print("no item in db")

    def iter(self, currentnode, list):
        if currentnode.hasLeftNode():
            left = leftnode(self.storage, currentnode.leftaddress)
            self.iter(left, list)
        list.append(currentnode.key)
        if currentnode.hasRightNode():
            right = rightnode(self.storage, currentnode.rightaddress)
            self.iter(right, list)
        return list
