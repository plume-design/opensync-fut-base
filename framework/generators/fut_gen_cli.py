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
        required=True,
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
    return input_args


def load_explicit_testcase_configurations(dut_model, modules):
    import importlib

    importlib.invalidate_caches()
    test_case_config = {}
    if Path(f"config/model/{dut_model}/testcase").is_dir():
        config_path = Path(f"config/model/{dut_model}/testcase")
    elif Path(f"internal/config/model/{dut_model}/testcase").is_dir():
        config_path = Path(f"internal/config/model/{dut_model}/testcase")
    else:
        return test_case_config
    # Define test_case_mod before applying config_path.absolute()
    test_case_mod = config_path.as_posix().replace("/", ".")
    config_path = config_path.absolute()
    inputs_files = [file.stem for file in config_path.iterdir() if "_config.py" in file.name]
    if modules:
        inputs_files = [f"{mod}_config" for mod in modules if config_path.joinpath(f"{mod}_config.py").is_file()]
    inputs_files = sorted(inputs_files)
    for cfg_file in inputs_files:
        spec = importlib.util.find_spec(f"{test_case_mod}.{cfg_file}")
        if spec is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Shallow-merge new module over existing dictionary
        test_case_config = {**test_case_config, **module.test_cfg}
    return test_case_config


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

    # Now import all the old configs for one particular device model
    def_test_cfg = load_explicit_testcase_configurations(dut_model=opts.dut, modules=opts.modules)

    def_test_cfg_keys = list(def_test_cfg.keys())
    gen_test_cfg_keys = list(gen_test_cfg.keys())
    # Missing configs, to be added manually:
    def_keys_missing_in_gen = [key for key in def_test_cfg_keys if key not in gen_test_cfg_keys]
    common_keys = list(set(def_test_cfg_keys) - set(def_keys_missing_in_gen))
    # Redundant configs, to be removed:
    gen_keys_missing_in_def = [key for key in gen_test_cfg_keys if key not in def_test_cfg_keys]

    if opts.json:
        modules_str = f"_{'_'.join(opts.modules)}" if opts.modules else ""
        print("" if set(def_test_cfg_keys) == set(common_keys) else def_keys_missing_in_gen, end="")
        write_json_to_file(json_data=gen_test_cfg, filename=f"{opts.json}{modules_str}_gen.json")
        print("" if not gen_keys_missing_in_def else gen_keys_missing_in_def, end="")
        write_json_to_file(json_data=def_test_cfg, filename=f"{opts.json}{modules_str}_def.json")
    else:
        # Compare values:
        log.setLevel(0)
        from unittest import TestCase

        test_case_obj = TestCase()
        test_case_obj.maxDiff = None
        try:
            test_case_obj.assertEqual(gen_test_cfg, def_test_cfg)
        except Exception as e:
            print(e)
