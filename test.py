class Test(object):
    def __init__(self):
        self.a = 'a'


    def func3(self):
        print val

    val = 'val'

    def func4(self):
        self.func3()

test = Test()

print test.a

test.func4()
