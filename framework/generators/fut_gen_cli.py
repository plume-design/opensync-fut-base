#!/usr/bin/python3

import argparse
import json
import os
import sys
from pathlib import Path

from fut_gen import FutTestConfigGenClass

from lib_testbed.generic.pod.pod import Pod
from lib_testbed.generic.util.config import load_tb_config
from lib_testbed.generic.util.logger import log

fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(fut_base_dir)


def parse_arguments():
    """Standalone method for parsing script input arguments."""  # Instantiate the parser
    tool_description = """
    Generate FUT test configuration
    Tool generates FUT test configuration and outputs in JSON file if specified

    Example of usage:
    python3 fut_gen.py -j test.config.json
    """
    parser = argparse.ArgumentParser(
        description=tool_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Define options
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
    return input_args


def write_json_to_file(json_data: object, filename: str) -> None:
    print(f"Saving test configuration to output {filename}")
    with open(filename, "w") as json_f:
        json_f.write(json.dumps(json_data, sort_keys=True, indent=4))


if __name__ == "__main__":
    opts = parse_arguments()

    if opts.quiet:
        log.setLevel(50)

    testbed_name = os.getenv("OPENSYNC_TESTBED")
    testbed_cfg = load_tb_config(location_file=f"{testbed_name}.yaml", skip_deployment=True)

    device_obj = Pod()
    gw_obj = device_obj.resolve_obj(**{"config": testbed_cfg, "nickname": "gw"})
    leaf_obj = device_obj.resolve_obj(**{"config": testbed_cfg, "nickname": "l1"})

    for obj in [gw_obj, leaf_obj]:
        if hasattr(obj, "override_version_specific_ifnames"):
            obj.override_version_specific_ifnames()

    test_config_obj = FutTestConfigGenClass(
        gw=gw_obj,
        leaf=leaf_obj,
        modules=opts.modules,
        test_list=opts.test,
    )
    gen_test_cfg = test_config_obj.get_test_configs()
    out_filename = f"{gw_obj.model}_{leaf_obj.model}" if not opts.json else opts.json
    modules_str = f"_{'_'.join(opts.modules)}" if opts.modules else ""
    write_json_to_file(json_data=gen_test_cfg, filename=f"{out_filename}{modules_str}_gen.json")
