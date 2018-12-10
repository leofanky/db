import portalocker
import os
import struct

class Storage(object):
    def __init__(self, f):
        self.f = f
        self.locked = False
        self.ensureSuperblock()

    def ensureSuperblock(self):
        self.lock()
        self.seekEnd()
        address = self.f.tell()
        if address < 2048:
            self.f.write(b'\x00' * (2048 - address))
        self.unlock()

    def refreshSuperblock(self):
        self.lock()
        self.seekSuperblock()
        self.f.write(b'\x00'*2048)
        self.unlock()

    def lock(self):
        if not self.locked:
            portalocker.lock(self.f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        if self.locked:
            self.f.flush()
            portalocker.unlock(self.f)
            self.locked = False

    def seekEnd(self):
        self.f.seek(0, os.SEEK_END)

    def seekSuperblock(self):
        self.f.seek(0)

    def bytesToInteger(self, byte):
        return struct.unpack("!Q",  byte)[0]

    def integerToBytes(self, integer):
        return struct.pack("!Q", integer)

    def readInteger(self):
        return self.bytesToInteger(self.f.read(8))

    def writeInteger(self, integer):
        self.lock()
        self.f.write(self.integerToBytes(integer))

    def write(self, data):
        self.lock()
        self.seekEnd()
        address = self.f.tell()
        self.writeInteger(len(data))
        self.f.write(data)
        return address

    def read(self, address):
        if address:
            self.f.seek(address)
            length = self.readInteger()
            data = self.f.read(length)
            return data
        else:
            return b''

    def updateRootAddr(self, rootaddress):
        self.lock()
        self.f.flush()
        if rootaddress:
            self.seekSuperblock()
            self.writeInteger(rootaddress)
        else:
            self.refreshSuperblock()
        self.f.flush()
        self.unlock()

    def getRootAddr(self):
        self.seekSuperblock()
        rootaddress = self.readInteger()
        return rootaddress

    def close(self):
        self.unlock()
        self.f.close()

    @property
    def closed(self):
        return self.f.closed