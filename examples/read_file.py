from lk_utils import fs


def read_txt() -> None:
    data = fs.load('examples/_sample.txt')
    print(data)
    #   aaa
    #   bbb
    #   ccc
    #   ddd


def read_csv() -> None:
    data = fs.load('examples/_sample.csv')
    print(data)
    #   [
    #       ['name', 'level', 'registered'],
    #       ['alpha', '123', 'true'],
    #       ['beta', '456', 'false'],
    #   ]


def read_yaml() -> None:
    data = fs.load('examples/_sample.yaml')
    print(data)
    #   {'name': 'alpha', 'level': 123, 'registered': True}


def read_json() -> None:
    data = fs.load('examples/_sample.json')
    print(data)
    #   {'name': 'alpha', 'level': 123, 'registered': True}


if __name__ == '__main__':
    read_csv()
