class TestDemo():
    def __init__(self, *args, todo=None, **kwargs) -> None:
        print('args:')
        print(args)
        print('todo:')
        print(todo)
        print('kwargs:')
        print(kwargs)


if __name__ == '__main__':
    test = [1,2,3,5]
    TestDemo(1,2,3,a=1,b=2)