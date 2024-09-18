from lk_utils import fs


def write_txt() -> None:
    data = ['aaa', 'bbb', 'ccc', 'ddd']
    fs.dump(data, 'examples/_sample.txt')


def write_csv() -> None:
    data = [
        ['name', 'level', 'registered'],
        ['alpha', 123, True],
        ['beta', 456, False],
    ]
    fs.dump(data, 'examples/_sample.csv')


def write_yaml() -> None:
    data = {'name': 'alpha', 'level': 123, 'registered': True}
    fs.dump(data, 'examples/_sample.yaml')


def write_json() -> None:
    data = {'name': 'alpha', 'level': 123, 'registered': True}
    fs.dump(data, 'examples/_sample.json')
