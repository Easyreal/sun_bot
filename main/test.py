
list_1 = [1, 2, 3]








def check_user(func):
    def wrapper(message, *args, **kwargs):

        if message in list_1:
            return func(message=message, admin=True, *args, **kwargs, )
        else:
            return func(message=message, admin=False, *args, **kwargs)


    wrapper.__name__ = func.__name__
    return wrapper



@check_user
def func_123(message, admin=None):
    if admin:
        print(message)
    else:
        print('no')


if __name__ == '__main__':
    func_123(3)
