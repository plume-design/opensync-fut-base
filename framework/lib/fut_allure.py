import glob
import json
import os
import shutil
from pathlib import Path
from typing import Callable

import pytest

from lib_testbed.generic.pytest_plugins.allure_environment import get_osrt_snapshot
from lib_testbed.generic.util.allure_util import AllureUtil
from lib_testbed.generic.util.logger import log


@pytest.fixture(scope="session", autouse=True)
def allure_environment(request, setup):
    log.info("Adding environment variables to the Allure report.")
    cfg = request.config

    if not hasattr(cfg.option, "config_name"):
        cfg.option.config_name = "TestBed"

    # Docker env.list file
    envlist_filepath = Path(__file__).absolute().parents[2].joinpath("docker/env.list")
    if not envlist_filepath.is_file():
        envlist_filepath = envlist_filepath.parent.joinpath("env.list.base")
    with open(envlist_filepath, "r") as envlist_file:
        env_vars = [line.rstrip("\n").split("=")[0] for line in envlist_file.readlines()]
    for env_var in env_vars:
        env_value = os.getenv(env_var)
        AllureUtil(cfg).add_environment(env_var, env_value)

    fut_configurator = pytest.fut_configurator
    AllureUtil(cfg).add_environment("fut_base_dir", fut_configurator.fut_base_dir)
    AllureUtil(cfg).add_environment("testbed_name", fut_configurator.testbed_name)

    # Environment
    AllureUtil(cfg).add_environment("fut_release_version", fut_configurator.fut_release_version)

    # Device
    for device_nickname in ["server", "gw", "l1", "l2", "w1", "w2"]:
        try:
            device = getattr(pytest, device_nickname)
        except AttributeError:
            continue

        AllureUtil(cfg).add_environment(f"{device.name}_version", device.version)
        AllureUtil(cfg).add_environment(f"{device.name}_device_type", device.device_type)
        AllureUtil(cfg).add_environment(f"{device.name}_username", device.username)
        AllureUtil(cfg).add_environment(f"{device.name}_password", device.password)
        AllureUtil(cfg).add_environment(f"{device.name}_model", device.model)
        if device_nickname in ["gw", "l1", "l2"]:
            AllureUtil(cfg).add_environment(f"{device.name}_bridge_type", device.get_bridge_type())
        elif device_nickname in ["server"]:
            AllureUtil(cfg).add_environment("opensync_root", device.opensync_root)
            snapshot = get_osrt_snapshot(device.device_api)
            if snapshot:
                AllureUtil(cfg).add_environment("osrt_snapshot", snapshot)


def _create_backup_dir(src_path: str) -> None:
    try:
        dst_path = Path(src_path).parent.joinpath(f"{Path(src_path).name}_bak")
        shutil.copytree(src_path, dst_path)
        print(f"Directory '{src_path}' successfully copied to '{dst_path}'.")
    except shutil.Error as exception:
        raise exception(f"Error copying directory: {exception}")


def search_files(directory: str, search_strings: list[str]) -> list[str]:
    matching_files = []
    # Iterate over files in the target directory
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith("-result.json"):
                continue
            file_path = os.path.join(root, file)
            if any(search_string in open(file_path).read() for search_string in search_strings):
                matching_files.append(file_path)
    return matching_files


def create_processed_results(source_directory: str, removed_entries: list, create_backup: bool = True) -> None:
    """
    Process the test results directory based on the provided entries to be removed.

    Args:
        source_directory (str): Path of the source directory containing the results to be processed
        removed_entries (list): A list of tests from the current run that should be removed based on the status from the reference run
        create_backup (bool): Create a backup of the original results before modifying them
    """
    if create_backup:
        _create_backup_dir(source_directory)

    test_names = [test.get("name") for test in removed_entries]
    matching_files = search_files(source_directory, test_names)
    try:
        assert len(matching_files) == len(removed_entries)
        for file in matching_files:
            if Path(file).is_file():
                Path(file).unlink(missing_ok=False)
    except AssertionError:
        print(
            f"Number of entries to be removed ({len(removed_entries)}): {removed_entries} is not the same as the number of files containing these entries ({len(matching_files)}): {matching_files}.",
        )


def data_from_report(dct: dict) -> dict | None:
    data = None
    try:
        data = {key: dct[key] for key in ["name", "status", "parameterValues"]}
    except KeyError:
        pass
    return data


def data_from_results(dct: dict) -> dict | None:
    data = None
    try:
        assert all(key in dct.keys() for key in ["name", "status", "parameters"])
        assert isinstance(dct["parameters"][0], dict)
        data = {"parameterValues": [dct["parameters"][0].get("value")], **{key: dct[key] for key in ["name", "status"]}}
    except KeyError:
        pass
    return data


def determine_mismatches(common_entries: list[dict]) -> list[dict]:
    """
    Compare the status for common tests from the current and reference test runs.

    Args:
        common_entries (list): A list containing the common tests. Each list item is a dict with the following keys:
            'name': 'test_name[cfg2]',
            'name_ref': 'test_name[cfg3]',
            'parameterValues': {'param': 42, 'foo': 'bar'},
            'status': 'failed',
            'status_ref': 'passed',

    Returns:
        mismatches (list): A list containing tests from current test run whose status mismatch with the reference test run
    """
    mismatches = []
    for test_case in common_entries:
        if test_case.get("status") != test_case.get("status_ref"):
            mismatches.append(test_case)
    return mismatches


def read_data_from_report(source_directory: str) -> list:
    res_data = read_json_data_from_files(source_directory, "data/test-cases/*.json", data_from_report, None)
    return res_data


def read_data_from_results(source_directory: str) -> list:
    res_data = read_json_data_from_files(source_directory, "[0-9a-f-]*-result.json", None, data_from_results)
    return res_data


def read_json_data_from_files(
    source_directory: str,
    file_regex: str,
    object_hook: Callable | None,
    filter_function: Callable | None,
) -> list:
    """
    Extract the requested data from files in the source directory.

    Args:
        source_directory (str): Path of the source directory
        file_regex (str): Regular expression for finding source files
        object_hook (function pointer or None): Function executed on any object literal decoded (dict)
        filter_function (function pointer or None): Function executed on the entire object literal decoded (dict)

    Returns:
        (list): A list containing the filtered data
    """
    # Results file pattern
    res_json_pattern = os.path.join(source_directory, file_regex)
    res_json_files = glob.glob(res_json_pattern)

    # Empty list to hold result data
    res_data = []
    # Access the results.json files
    try:
        for file in res_json_files:
            with open(file, "r") as res_file:
                filtered_data = json.load(res_file, object_hook=object_hook)
                if filter_function:
                    filtered_data = filter_function(filtered_data)
                res_data.append(filtered_data)
    except FileNotFoundError:
        print(f"Unable to find JSON files {file_regex} in the specified source directory {source_directory}.")
    return res_data


def results_alignment(current_data: list, reference_data: list) -> tuple[list, list, list]:
    """
    Align the current data to the reference data in terms of name and parameter values.

    Args:
        current_data (list): A list containing the filtered data from the current test run
        reference_data (list): A list containing the filtered data from the reference test run

    Returns:
        (tuple): cur_data_specific_entries (list): Tests specific to the current test run
                 ref_data_specific_entries (list): Tests specific to the reference test run
                 common_entries (list): Tests from the current test run that appear in both test runs
    """
    sorted_current_data = sorted(current_data, key=lambda test: test["name"])
    sorted_reference_data = sorted(reference_data, key=lambda test: test["name"])

    common_entries = []
    current_data_specific_entries = []
    # shallow copy is enough, since items should not be changed, only popped
    reference_data_specific_entries = sorted_reference_data[:]
    for test_case in sorted_current_data:
        test_name = test_case["name"].split("[")[0]
        parameterValues = test_case.get("parameterValues")
        name_ref = None
        status_ref = None
        for ref_idx, ref_test in enumerate(reference_data_specific_entries):
            if not all(
                [ref_test["name"].split("[")[0] == test_name, ref_test.get("parameterValues") == parameterValues],
            ):
                continue
            name_ref = ref_test.get("name")
            status_ref = ref_test.get("status")
            if len(reference_data_specific_entries) > 0:
                reference_data_specific_entries.pop(ref_idx)
            break
        item_out = {
            **test_case,
            "name_ref": name_ref,
            "status_ref": status_ref,
        }
        if name_ref is None or status_ref is None:
            current_data_specific_entries.append(test_case)
        else:
            common_entries.append(item_out)

    return current_data_specific_entries, reference_data_specific_entries, common_entries


def split_common_entries(common_entries: list) -> tuple[list, list]:
    """
    Split the common tests based on the status of the reference test.

    There are five possible status values: [passed, failed, broken, skipped, unknown].
    If the statuses in the current test run and the reference test run are both one of [failed, broken], the test is
    removed from the processed entries and returned in a separate list.

    Args:
        common_entries (list): A list containing the common tests.

    Returns:
        (tuple) filtered_entries, removed_entries
        WHERE
        filtered_entries (list): A list containing tests from current test run whose status was corrected bn the reference test run
        removed_entries (list): A list containing tests from current test run whose status was corrected bn the reference test run
    """
    _statuses = ["failed", "broken"]
    removed_entries = []
    filtered_entries = []
    for test in common_entries:
        if test.get("status") in _statuses and test.get("status_ref") in _statuses:
            removed_entries.append(test)
        else:
            filtered_entries.append(test)
    return filtered_entries, removed_entries
