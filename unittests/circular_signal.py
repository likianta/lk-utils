from argsense import cli

from lk_utils.binding import Signal
from lk_utils.binding import config


@cli.cmd()
def main(error_level: int = 1) -> None:
    match error_level:
        case 0:
            config.circular_signal_error = 'ignore'
        case 1:
            config.circular_signal_error = 'prompt'
        case 2:
            config.circular_signal_error = 'raise'
    
    width_changed = Signal()
    height_changed = Signal()
    
    width = 0
    height = 0
    
    def increse_width() -> None:
        nonlocal width
        width += 1
        width_changed.emit()
    
    def increse_height() -> None:
        nonlocal height
        height += 1
        height_changed.emit()
    
    # make a circular signal chain
    width_changed.bind(increse_height)
    height_changed.bind(increse_width)
    
    increse_width()


if __name__ == '__main__':
    # pox unittests/circular_signal.py 0
    # pox unittests/circular_signal.py 1
    # pox unittests/circular_signal.py 2
    cli.run(main)
