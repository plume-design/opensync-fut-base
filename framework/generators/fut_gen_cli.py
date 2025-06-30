#!/usr/bin/python3

import argparse
import json
import os
import sys
from pathlib import Path

from fut_gen import FutTestConfigGenClass

from framework.handlers.pod_handler import PodHandler
from framework.lib.fut_fixtures import resolve_pod_obj
from lib_testbed.generic.pod.generic.pod_api import PodApi
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
    parser.add_argument(
        "-V",
        "--force_version",
        required=False,
        default=None,
        type=str,
        help="Force version for which test configuration is generated. If not specified, the version is taken from the testbed configuration.",
    )
    input_args = parser.parse_args()
    return input_args


def write_json_to_file(json_data: object, filename: str) -> None:
    print(f"Saving test configuration to output {filename}")
    with open(filename, "w") as json_f:
        json.dump(json_data, json_f, sort_keys=True, indent=4)


if __name__ == "__main__":
    opts = parse_arguments()

    if opts.quiet:
        log.setLevel(50)

    testbed_name = os.getenv("OPENSYNC_TESTBED")
    testbed_cfg = load_tb_config(location_file=f"{testbed_name}.yaml", skip_deployment=True)

    gw_obj = resolve_pod_obj(name="gw", index=0, config=testbed_cfg, multi_obj=False)
    leaf_obj = resolve_pod_obj(name="l1", index=1, config=testbed_cfg, multi_obj=False)

    if opts.force_version:

        def opensync_version_override(self):
            return opts.force_version

        def version_override(self):
            return opts.force_version

        PodApi.opensync_version = opensync_version_override
        PodApi.version = version_override

    gw_handler = PodHandler(**gw_obj)
    leaf_handler = PodHandler(**leaf_obj)

    test_config_obj = FutTestConfigGenClass(
        gw=gw_handler,
        leaf=leaf_handler,
        modules=opts.modules,
        test_list=opts.test,
        version=opts.force_version,
    )
    gen_test_cfg = test_config_obj.get_test_configs()
    out_filename = f"{gw_handler.model}_{leaf_handler.model}" if not opts.json else opts.json
    modules_str = f"_{'_'.join(opts.modules)}" if opts.modules else ""
    write_json_to_file(json_data=gen_test_cfg, filename=f"{out_filename}{modules_str}_gen.json")
