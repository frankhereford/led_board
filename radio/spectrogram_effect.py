# rtl_fm -M wbfm -f 98.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -

import sounddevice as sd

from lib.argparse import parse_arguments
from lib.layout import read_json_from_file
#from lib.scroll import render_scrolling_text_updated
from lib.spectrograph import *

args = parse_arguments()
layout = read_json_from_file("installation_v2_groups.json")

inject_args(args)
create_text_frames(args)
samplerate = create_spectrograph_parameters(layout)

try:
    with sd.InputStream(
        device=args.device,
        channels=1,
        callback=callback,
        blocksize=int(samplerate * args.block_duration / 1000),
        samplerate=samplerate,
    ):
        while True:
            response = input()
            if response in ("", "q", "Q"):
                break
            for ch in response:
                if ch == "+":
                    args.gain *= 2
                elif ch == "-":
                    args.gain /= 2
                else:
                    print(
                        "\x1b[31;40m",
                        usage_line.center(args.columns, "#"),
                        "\x1b[0m",
                        sep="",
                    )
                    break
except KeyboardInterrupt:
    exit("Interrupted by user")