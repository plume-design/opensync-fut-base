"""
FUT helper functions.

This module contains functions that are necessary throughout the entire
FUT test suite but belong to no particular class.
"""

import hashlib
import json
import subprocess
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Literal

import allure  # type: ignore
import yaml

from config.defaults import all_bandwidth_list, radio_band_list
from lib_testbed.generic.util.logger import log


type fileDescriptorOrPathstr = int | str | bytes | PathLike[str] | PathLike[bytes]


def allure_attach_to_report(name: str | None, body: Any):
    """
    Create Allure report attachment.

    Args:
        name (str | None): Name of the attachment.
        body (Any): Body of the attachment.
    """
    try:
        allure.attach(name=name, body=body)
    except Exception as exception:
        log.warning(f"Failed to create the Allure report attachment: {exception}")


def multi_device_script_execution(devices: list, script: str, args: str = "", **kwargs) -> None:
    """
    Execute a script on all specified devices.

    Args:
        devices (list): List of NodeHandler or DeviceHandler objects.
        script (str):  Path to script.
        args (str): Optional script arguments. Defaults to empty string.

    Keyword Args:
        as_sudo (bool): Execute script with superuser privileges.
        suffix (str): Suffix of the script.
        folder (str): Name of the folder where the script is located.
    """
    try:
        for device in devices:
            assert device.execute(script, args, **kwargs)[0] == 0
    except AssertionError as assertion:
        raise RuntimeError(
            f"Unable to execute script on all specified devices {device}, assertion on {device}: {assertion}",
        )


def allure_script_execution_post_processing(function: Callable) -> Callable:
    """
    Wrap functions and methods for enhanced Allure output.

    Serves as a wrapper for functions and methods. Enables the test
    output to be split into steps when creating the Allure report.
    """

    def wrapper(*args, **kwargs):
        step_name = args[1].split("/")[-1]
        with allure.step(f"{step_name}:"):
            cmd_ec, cmd_std_out, cmd_std_err = function(*args, **kwargs)
        return cmd_ec, cmd_std_out, cmd_std_err

    return wrapper


def step(step_title: str) -> Callable:
    """
    Format step mark for Allure report and add colon to step title.

    Args:
        step_title (str): Step title.

    Returns:
        _type_: Allure step mark.
    """
    return allure.step(f"{step_title}:")


def print_allure(message: str) -> None:
    """
    Redirect a message.

    Directs the message to standard output and attaches it to the
    Allure report.

    Args:
        message (str): Message to be attached.
    """
    allure.attach(
        name="OUTPUT",
        body=message,
    )


def output_to_json(
    data: object,
    json_file: fileDescriptorOrPathstr = "fut_data.json",
    sort_keys: bool = True,
    indent: int = 4,
    convert_only: bool = False,
) -> str | None:
    """
    Output given data to JSON file.

    Args:
        data (JSON serializable data, dict(), list() etc.)
        json_file (FileDescriptorOrPathstr): Path to JSON file
        sort_keys (bool): sort output of dictionaries by key
        indent (int): pretty-print object members with specified indent level
        convert_only (bool): only convert data to JSON format without writing to file

    Raises:
        RuntimeError: Failed to output data to JSON file

    Returns:
        (str): JSON string if convert_only is set to True
    """
    try:
        if convert_only:
            json_string = json.dumps(data, sort_keys=sort_keys, indent=indent)
            return json_string
        with open(json_file, "w") as jsf:
            jsf.write(json.dumps({"data": data}, sort_keys=sort_keys, indent=indent))
            return None
    except PermissionError as exception:
        raise RuntimeError(f"Failed to output data to JSON file {exception}")
    except TypeError as exception:
        raise RuntimeError(f"Input data: {data} contains non-basic objects unsupported by json.dumps(): {exception}")


def check_if_dicts_match(dict1: dict, dict2: dict) -> list | Literal[True]:
    """
    Verify if dictionaries match.

    Verify if the keys and values of the first dictionary are contained
    in the second dictionary. The check is case-insensitive.

    Args:
        dict1 (dict): Dictionary.
        dict2 (dict): Dictionary.

    Returns:
        bool: True for success
        list: Logs warning and returns list of mismatching keys on
            failure.
    """
    mismatching_keys = []

    for key in dict1:
        if isinstance(dict1[key], str):
            if isinstance(dict2[key], list):
                list_len = len(dict2[key]) - 1
                for list_index, list_item in enumerate(dict2[key]):
                    if dict1[key].casefold() == list_item.casefold():
                        break
                    elif list_index == list_len:
                        mismatching_keys.append(key)
                        break
            elif key in dict2 and dict1[key].casefold() != dict2[key].casefold():
                mismatching_keys.append(key)
        elif key in dict2 and dict1[key] != dict2[key]:
            mismatching_keys.append(key)
    if mismatching_keys:
        log.warning(f"Dictionaries {dict1} and {dict2} do not match for the following keys: {mismatching_keys}")
        return mismatching_keys

    return True


def execute_locally(path: str, args: str = "", suffix=".sh", **kwargs) -> tuple[int, str, str]:
    """
    Execute the specified script locally with optional arguments.

    Args:
        path (str): Path to script.
        args (str): Optional script arguments. Defaults to empty string.
        suffix (str): File extension. Defaults to .sh

    Keyword Args:
        dir_path (str): Path to parent directory.

    Returns:
        list: List comprised of the exit code, standard output and standard error.
    """
    dir_path = kwargs.get("dir_path") if kwargs.get("dir_path") else Path(__file__).absolute().parents[2]

    cmd_list = [f"{dir_path}/{path}{suffix}"] + args.split()

    stream = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    cmd_std_out_bytes, cmd_std_err_bytes = stream.communicate()
    cmd_std_out, cmd_std_err = cmd_std_out_bytes.decode("utf-8").strip(), cmd_std_err_bytes.decode("utf-8").strip()
    cmd_ec = stream.returncode

    allure_attach_to_report(
        name="log_local",
        body=f"""
            {' '.join(cmd_list)}
            stdout:
            {cmd_std_out}
            stderr:
            {cmd_std_err}
        """,
    )

    return cmd_ec, cmd_std_out, cmd_std_err


def flatten_list(nested_list: list[list]) -> list[Any]:
    """
    Flatten a nested list.

    Args:
        nested_list (list): Nested list to be flattened.

    Returns:
        list: Flattened list.
    """
    return [
        item for sublist in nested_list for item in (flatten_list(sublist) if isinstance(sublist, list) else [sublist])
    ]


def determine_required_devices(test_suites: list[str]) -> tuple[list[str], list[str]]:
    """
    Determine required devices for the execution of the specified tests.

    Args:
        test_suites (list): List of requested test class names

    Returns:
        tuple: Required nodes, required clients.
    """
    filename = "test_suite_device_requirements.yaml"
    dirname = "config/rules"
    filepaths: list[PathLike] = []
    for parent_dir in [".", "internal"]:
        if Path(parent_dir).joinpath(dirname).is_dir():
            filepaths.append(*Path(parent_dir).joinpath(dirname).glob(filename))
    loaded_device_req_file = {}
    for file in filepaths:
        with open(file) as device_req_file:
            loaded_device_req_file.update(yaml.safe_load(device_req_file))

    required_nodes, required_clients = [], []

    for test_suite in test_suites:
        required_nodes.append(loaded_device_req_file[test_suite]["nodes"])
        required_clients.append(loaded_device_req_file[test_suite]["clients"])

    # Flatten the lists and remove duplicated values
    required_nodes, required_clients = (
        list(filter(None, set(flatten_list(required_nodes)))),
        list(filter(None, set(flatten_list(required_clients)))),
    )

    return required_nodes, required_clients


def map_dict_key_path(dictionary: dict, key_mem: str = "") -> list[Any]:
    """Map dictionary to list.

    Uses recursion if value of key in argument dictionary is a dictionary.

    Args:
        dictionary (dict): Dictionary to map.
        key_mem (str, optional): String to prepend. Defaults to "".

    Returns:
        (list): Distionary as mapped list of strings
    """
    result = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            result += map_dict_key_path(value, f"{key_mem}{key}_")
        else:
            result.append((f"{key_mem}{key}", value))
    return result


def load_reg_rule() -> dict:
    """Load regulatory rules from regulatory.yaml file.

    Returns:
        (dict): regulatory rules dictionary
    """
    full_path = f'{str(Path(__file__).absolute()).split("framework")[0]}/config/rules/regulatory.yaml'
    try:
        with open(full_path) as reg_rule_file:
            return yaml.safe_load(reg_rule_file)
    except yaml.YAMLError as exception:
        raise RuntimeError(f"Failed to load regulatory rules from YAML file {full_path}: {exception}") from exception
    except PermissionError as exception:
        raise RuntimeError(f"Failed to open file file {full_path}: {exception}") from exception


def validate_channel_ht_mode_band(
    channel: int,
    ht_mode: str = "HT20",
    radio_band: str = "",
    regulatory_rule: dict | None = None,
    reg_domain: str = "US",
    raise_broken: bool = False,
) -> bool:
    """Verify if the selected channel, ht_mode and radio_band are compatible with the regulatory domain.

    Args:
        channel (int): WiFi channel
        ht_mode (str): channel bandwidth
        radio_band (str): WiFi band.
        reg_domain (str): regulatory domain. Supported "US" (default), "EU", "GB".

    Returns:
        bool: True if the combination of band, channel, ht_mode, reg_domain is supported by the device, False otherwise.
    """
    if not regulatory_rule:
        log.warning("Regulatory rules not found, loading")
        regulatory_rule = load_reg_rule()
    try:
        assert ht_mode in all_bandwidth_list
        assert radio_band in radio_band_list
        if channel not in regulatory_rule[reg_domain.upper()]["band"][radio_band.lower()][ht_mode.upper()]:
            msg = f"Invalid combination of parameters: channel:{channel}, ht_mode:{ht_mode.upper()}, band:{radio_band.lower()}, regulatory domain: {reg_domain.upper()}"
            log.debug(msg)
            if raise_broken:
                raise RuntimeError(msg)
        else:
            return True
    except AssertionError:
        log.error(f"Invalid radio_band: {radio_band} and ht_mode:{ht_mode}")
    except RuntimeError as e:
        log.error(e)
    except KeyError:
        log.debug(
            f"Parameters unsupported by device. channel:{channel}, ht_mode:{ht_mode}, band:{radio_band}, regulatory domain: {reg_domain}",
        )
    return False


def get_str_hash(input_string: str, hash_length: int = 32) -> str:
    """Get a hash of the desired length from the input string.

    Args:
        input_string (str): Any input string that you wish to hash
        hash_length (int): length of the output hash in the range [4, 32]

    Returns:
        hash (str): The hashed input string of the desired length hash_length
    """
    hash_length = min(32, max(4, hash_length))
    return hashlib.md5(input_string.encode()).hexdigest()[:hash_length]


def find_filename_in_dir(directory: str, pattern: str) -> list[str]:
    """Recursively find files with a specific file name pattern in the directory tree.

    Args:
        directory (str): The directory to search for the files
        pattern (str): The pattern by which file names are searched

    Returns:
        list_of_files (list): A list containing paths to the found unit test files
    """
    list_of_files = [path.as_posix() for path in Path(directory).rglob(pattern)]
    if list_of_files:
        log.info(f"Found files: {list_of_files}")
    return list_of_files
