from .cli import cli
from . import cells, merge_outputs
from .papermill import clean, run


def main():
    cli()


if __name__ == '__main__':
    main()
