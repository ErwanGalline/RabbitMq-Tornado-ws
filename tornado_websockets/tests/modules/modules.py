from tornado_websockets.modules import Module


class Module1(Module):
    pass


class Module2(Module):
    def __init__(self, name=''):
        pass


class Module3(Module):
    def __init__(self, name=''):
        pass

    def initialize(self):
        pass


class MyModule(Module):
    def __init__(self, name=''):
        if name:
            name = '_' + name
        super(MyModule, self).__init__('mymodule' + name)

    def initialize(self):
        print('initialized')
