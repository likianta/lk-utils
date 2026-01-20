from argsense import cli
from lk_utils.strict_yaml_parser import load_file

# print(load_file('test/_sample_yaml_files/dict.yaml'), ':l')


@cli
def main(file):
    print(load_file(file), ':l')


if __name__ == '__main__':
    cli.run(main)
