#!/usr/bin/python3

import argparse
import json
import sys
from pathlib import Path

from fut_gen import FutTestConfigGenClass

from lib_testbed.generic.util.logger import log

fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(fut_base_dir)


def parse_arguments():
    """Standalone method for parsing script input arguments."""  # Instantiate the parser
    tool_description = """
    Generate FUT test configuration
    Tool generates FUT test configuration and outputs in JSON file if specified

    Example of usage:
    python3 fut_gen.py --dut PP203X -ref PP203X -j test.config.json
    """
    parser = argparse.ArgumentParser(
        description=tool_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Define options
    parser.add_argument(
        "-d",
        "--dut",
        required=True,
        type=str,
        help="Model name for DUT",
    )
    parser.add_argument(
        "-r",
        "--ref",
        required=False,
        type=str,
        help="Model name for REF",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Silence logging module",
    )
    parser.add_argument(
        "-j",
        "--json",
        required=False,
        default=None,
        type=str,
        help="Output json to file provided path",
    )
    parser.add_argument(
        "-m",
        "--modules",
        required=False,
        default=None,
        type=str,
        nargs="+",
        help="Output test configuration for given test module(s)",
    )
    parser.add_argument(
        "-t",
        "--test",
        required=False,
        default=None,
        type=str,
        nargs="+",
        help="Output test configuration for given test name(s)",
    )
    input_args = parser.parse_args()
    if input_args.dut and not input_args.ref:
        log.warning(f"Model name for REF not provided, defaulting to DUT: {input_args.dut}")
        input_args.ref = input_args.dut
    return input_args


def write_json_to_file(json_data, filename):
    print(f"Saving test configuration to output {filename}")
    with open(filename, "w") as json_f:
        json_f.write(json.dumps(json_data, sort_keys=True, indent=4))


if __name__ == "__main__":
    opts = parse_arguments()

    if opts.quiet:
        log.setLevel(50)

    try:
        test_config_obj = FutTestConfigGenClass(
            gw_name=opts.dut,
            leaf_name=opts.ref,
            modules=opts.modules,
            test_list=opts.test,
        )
        gen_test_cfg = test_config_obj.get_test_configs()
    except Exception as e:
        log.error(f"Exception caught during test config generation\n{e}")
        sys.exit(1)

    out_filename = f"{opts.dut}_{opts.ref}" if not opts.json else opts.json
    modules_str = f"_{'_'.join(opts.modules)}" if opts.modules else ""
    write_json_to_file(json_data=gen_test_cfg, filename=f"{out_filename}{modules_str}_gen.json")
