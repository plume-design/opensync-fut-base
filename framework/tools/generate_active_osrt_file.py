#!/usr/bin/env python3

"""Module to generate active OSRT file."""

import sys
from pathlib import Path
topdir_path = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(topdir_path)

from framework.server_handler import ServerHandlerClass

SERVER_HANDLER = ServerHandlerClass()

if __name__ == "__main__":
    res = SERVER_HANDLER.generate_active_osrt_location_file()
    sys.exit(0 if res is True else 1)
