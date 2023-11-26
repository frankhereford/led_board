import argparse
import shutil
import sounddevice as sd
import numpy as np


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def parse_arguments():
    usage_line = " press <enter> to quit, +<enter> or -<enter> to change scaling "

    try:
        columns, _ = shutil.get_terminal_size()
    except AttributeError:
        columns = 80

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--list-devices",
        action="store_true",
        help="show list of audio devices and exit",
    )
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description="\n\nSupported keys:" + usage_line,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser],
    )
    parser.add_argument(
        "-b",
        "--block-duration",
        type=float,
        metavar="DURATION",
        default=25,
        help="block size (default %(default)s milliseconds)",
    )
    parser.add_argument(
        "-c", "--columns", type=int, default=32, help="width of spectrogram"
    )
    parser.add_argument(
        "-d",
        "--device",
        type=int_or_str,
        default=7,
        help="input device (numeric ID or substring)",
    )
    parser.add_argument(
        "-g",
        "--gain",
        type=float,
        default=50,
        help="initial gain factor (default %(default)s)",
    )
    parser.add_argument(
        "-r",
        "--range",
        type=float,
        nargs=2,
        metavar=("LOW", "HIGH"),
        default=[50, 1000],
        help="frequency range (default %(default)s Hz)",
    )

    parser.add_argument(
        "-s",
        "--hide-spectrogram",
        action="store_false",
        default=True,
        help="Enable this option to hide the spectrogram.",
    )

    parser.add_argument(
        "-t",
        "--show-scroll",
        action="store_true",
        default=False,
        help="Enable this option to show scrolling in the standard output.",
    )

    parser.add_argument(
        "-m",
        "--render-scroll",
        type=int,
        nargs="?",
        const=300,
        default=None,
        help="Enable this option to show scrolling text on the lights. Defaults to 300 if no value is provided.",
    )

    parser.add_argument(
        "-w",
        "--message",
        type=str,
        nargs="?",
        const="KUTX",
        default="KUTX",
        help="Specify a message to display. Defaults to 'KUTX'.",
    )

    np.set_printoptions(
        linewidth=200,
        formatter={"int": "{:4d}".format},
    )

    args = parser.parse_args(remaining)
    return args
