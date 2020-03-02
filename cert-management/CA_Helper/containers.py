
from os.path import exists


class FileContainer():
    def __init__(self, obj, path=None, read=None, write=None):
        self.path = path
        self.read_method = read
        self.write_method = write

        if isinstance(obj, type):
            self.inst = obj()
            
            if self.path and exists(self.path) and self.read_method:
                self.readfile()
        else:
            self.inst = obj

        print(f'New { self.__class__.__name__ } that contains { self.inst.__class__.__name__ } object { self.inst }')

    def __getattr__(self, name):
        return getattr(self.inst, name)

    def readfile(self, method=None):
        if not method and not self.read_method:
            raise NotImplementedError(f'Read Function not specified for { self.__class__.__name__ }({ self.inst.__class__.__name__ }).')
        if not self.path:
            raise FileNotFoundError(f'File Path not specified!')

        print(f'Reading from file { self.path }')

        inst = ( method(self.path, type(self.inst)) if method else self.read_method(self.path, type(self.inst)) )

        if not type(inst) == type(self.inst):
            raise TypeError(f'Type returned by read method does not match : { inst.__class__.__name__ } != { self.inst.__class__.__name__ }')
        else:
            self.inst = inst

    def writefile(self, method=None):
        if not method and not self.write_method:
            raise NotImplementedError(f'Write Function not specified for { self.__class__.__name__ }({ self.inst.__class__.__name__ }).')
        if not self.path:
            raise FileNotFoundError(f'File Path not specified!')

        print(f'Writing to file { self.path }')

        method(self.path, type(self.inst), self.inst) if method else self.write_method(self.path, type(self.inst), self.inst)