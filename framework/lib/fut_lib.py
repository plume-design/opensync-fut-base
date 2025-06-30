"""
FUT helper functions.

This module contains functions that are necessary throughout the entire
FUT test suite but belong to no particular class.
"""

import hashlib
import json
import os
import subprocess
from concurrent.futures import as_completed, ThreadPoolExecutor
from os import PathLike
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, List, Literal

import allure  # type: ignore
import yaml
from mergedeep import merge, Strategy

from config.defaults import all_bandwidths, all_radio_bands
from lib_testbed.generic.util.logger import log
from lib_testbed.generic.util.ssh.common import EXECUTE_CMD_TIMEOUT


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


def check_if_dicts_match(dict1: dict, dict2: dict, inorder: bool) -> list | Literal[True]:
    """
    Verify if dictionaries match.

    Verify if the keys and values of the first dictionary are contained
    in the second dictionary. The check is case-insensitive.

    Args:
        dict1 (dict): Dictionary.
        dict2 (dict): Dictionary.
        inorder (bool): If values are iterables, check them in order

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
        elif key in dict2:
            if inorder and dict1[key] != dict2[key]:
                mismatching_keys.append(key)
            else:
                try:
                    if set(dict1[key]) != set(dict2[key]):
                        mismatching_keys.append(key)
                except TypeError:
                    if dict1[key] != dict2[key]:
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
        assert ht_mode in all_bandwidths
        assert radio_band in all_radio_bands
        if channel not in regulatory_rule[reg_domain.upper()]["band"][radio_band.lower()][ht_mode.upper()]:
            msg = f"Invalid combination of parameters: channel:{channel}, ht_mode:{ht_mode.upper()}, band:{radio_band.lower()}, regulatory domain: {reg_domain.upper()}"
            log.error(msg)
            if raise_broken:
                raise RuntimeError(msg)
        else:
            return True
    except AssertionError:
        log.error(f"Invalid radio_band: {radio_band} and ht_mode:{ht_mode}")
    except RuntimeError as e:
        log.error(e)
    except KeyError:
        log.error(
            f"Parameters unsupported by device. channel:{channel}, ht_mode:{ht_mode}, band:{radio_band}, regulatory domain: {reg_domain}",
        )
    return False


def get_chanspec(region: str, band: str, only_dfs=False):
    regulatory = load_reg_rule()[region]
    if only_dfs:
        spectrum_specifier = "dfs"
        dfs_regulatory = merge(
            regulatory[spectrum_specifier]["standard"][band],
            regulatory[spectrum_specifier]["weather"][band],
            strategy=Strategy.ADDITIVE,
        )
        return dfs_regulatory
    else:
        return regulatory["band"][band]


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


def sanitize_arg(arg: str) -> str:
    """
    Sanitize the argument of selected characters.

    Args:
        arg (str): Argument to be sanitized.
    Returns:
        (str): Sanitized argument.
    """
    if (arg[0] == '"' and arg[-1] == '"') or (arg[0] == "'" and arg[-1] == "'") or (arg[0] == "-"):
        # Argument is already surrounded by "" or '' or starts with -
        pass
    elif " " in arg:
        arg = f'"{arg}"'
    return arg


def get_command_arguments(*args) -> str:
    """
    Return command arguments.

    Returns command arguments as a string to feed the script.
    Command arguments are separated by a space and with escaped "
    or ' characters if present in arguments. Uses recursion if
    argument is a list.
    Returns:
        (str): Command arguments as a string.
    """
    command = ""
    for arg in args:
        if isinstance(arg, list | tuple | set):
            command = str(command) + get_command_arguments(*arg)
        else:
            if isinstance(arg, int):
                arg = str(arg)
            if isinstance(arg, str):
                arg = arg.strip()
            command = str(command) + " " + str(sanitize_arg(arg))
    return command


def get_testbed_name() -> str:
    """
    Get the testbed name.

    Returns:
        (str): Testbed name.
    """
    testbed_name = subprocess.run(["cat", "/etc/hostname"], stdout=subprocess.PIPE)

    return testbed_name.stdout.decode("utf-8").strip()


def fut_release_version() -> str | None:
    """
    Return the release version of the FUT sources.

    Returns:
        version (str): FUT release version.
    """
    version_file = Path(".version")
    if not version_file.is_file():
        return None
    with open(version_file, "r") as version_fd:
        version = version_fd.read().strip()
    return version


def read_md_description(test_name):
    """
    Read the Markdown file containing the description for a test case.

    Args:
        test_name (str): The name of the test case (without the `.md` extension),
                          which is used to locate the corresponding Markdown file.

    Returns:
        str: The content of the Markdown file as the test description, or a
             fallback message if the file is not found.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, "../../doc/definitions"))
    md_file = os.path.join(base_dir, f"{test_name}.md")

    try:
        with open(md_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Description not available."


def execute_on_pods(pods: List[Any], pod_method: str, timeout: int = None, *args, **kwargs) -> Dict[str, Any]:
    """
    Execute a method on multiple pod instances in parallel.

    This function takes a list of pod handler instances and executes a specified method on each of them
    concurrently. It returns a dictionary mapping each pod's nickname to the result of the method call.
    If a method call fails, the error is captured and returned in the results dictionary.

    Args:
        pods (List[Any]): List of pod instances (PodHandler objects) on which to execute the method.
        pod_method (str): Name of the method to execute on each pod.
        timeout (int, optional): Maximum time in seconds to wait for each method call to complete.
            If None, the method will wait indefinitely. Defaults to None.
        *args: Variable length argument list to pass to the pod method.
        **kwargs: Arbitrary keyword arguments to pass to the pod method.

    Returns:
        Dict[str, Any]: A dictionary where keys are pod nicknames and values are the results
            of the method calls. If a method call fails, the value will be a dictionary with
            an "ERROR" key containing the error message.
    """

    def _call_method(pod):
        try:
            method = getattr(pod, pod_method)
            return pod.nickname, method(*args, **kwargs)
        except Exception as exception:
            return pod.nickname, {
                "ERROR": str(exception),
            }

    results: Dict[str, Any] = {}

    with ThreadPoolExecutor(max_workers=len(pods)) as executor:
        futures = {executor.submit(_call_method, pod): pod for pod in pods}
        for future in as_completed(futures, timeout=timeout):
            pod = futures[future]
            try:
                pod_name, result = future.result(timeout=timeout)
                results[pod_name] = {"RESULT": result, "CMD": pod_method}
            except Exception as exception:
                results[pod.nickname] = {"ERROR": str(exception)}

    log.info(f"Results of {pod_method} on pods:\n{json.dumps(results, indent=2)}")

    return results


def reboot_pods_and_wait_available(pods: List[Any]) -> Dict[str, Any]:
    """
    Reboot multiple pods and wait for them to become available again.

    This function performs a complete reboot cycle on a list of pods:
    1. First checks if all pods are available
    2. Reboots all pods in parallel
    3. Waits for a fixed time to allow pods to complete the reboot process
    4. Verifies that all pods are available again after reboot

    Args:
        pods (List[Any]): List of pod instances (PodHandler objects) to reboot.

    Returns:
        Dict[str, Any]: A dictionary where keys are pod nicknames and values are the results
            of the final availability check. If a pod fails to become available after reboot,
            the value will be a dictionary with an "ERROR" key containing the error message.
    """
    if not pods:
        return
    execute_on_pods(pods, pod_method="wait_available", timeout=EXECUTE_CMD_TIMEOUT)
    execute_on_pods(pods, pod_method="reboot", timeout=EXECUTE_CMD_TIMEOUT)
    # Hardcoded delay to ensure pods are rebooted, do not optimize
    sleep(20)
    reboot_time = max(pod.reboot_time for pod in pods)
    execute_on_pods(pods, pod_method="wait_available", timeout=reboot_time)


def _find_target_path_in_root_dir(target_path: str, root_dirs: list[str] = None, **kwargs) -> list:
    """
    Return a list of paths to the target path, contained within any root_dir present in the current or any subdirectory.

    Args:
        target_path (str): The name or partial path of the target directory or file.
        root_dir (list[str]): List of root directory paths within which to search for the target_path.

    Returns:
        paths (list): List of paths to all target_path found.
    """
    follow_symlinks = kwargs.pop("follow_symlinks", True)
    if not root_dirs:
        root_dirs = ["."]
    paths = [
        root.joinpath(target_path)
        for root_dir in root_dirs
        for root, _, _ in Path(root_dir).walk(follow_symlinks=follow_symlinks)
        if root.joinpath(target_path).exists()
    ]
    return paths
