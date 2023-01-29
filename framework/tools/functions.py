"""Module provides auxiliary functions for testcase execution and reports."""

import base64
import json
import random
import string
from pathlib import Path

import allure
import yaml

import framework.tools.logger


global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


class BrokenException(Exception):
    """BrokenException class."""

    pass


class FailedException(AssertionError):
    """FailedException class."""

    pass


def check_if_dicts_match(dict1, dict2):
    """Verify if the keys and values of the first dictionary are contained in the second dictionary. The check is case-insensitive.

    Args:
        dict1 (dict): dictionary
        dict2 (dict): dictionary

    Returns:
        bool: True for success
        list: logs warning and returns list of mismatching keys on failure.
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
        log.warning(f'Dictionaries {dict1} and {dict2} do not match for the following keys: {mismatching_keys}')
        return mismatching_keys
    return True


def generate_image_key():
    """Generate image key used in UM (Upgrade Manager) testcases.

    Used when image key is not provided in testcase configuration.

    Returns:
        (str): FW image key
    """
    letters_and_digits = string.ascii_lowercase + string.digits + string.ascii_uppercase
    image_key_pure = ''.join(random.choice(letters_and_digits) for i in range(32))

    return str(base64.b64encode(image_key_pure.encode('ascii'))).replace('"b\'', '').replace('\'', '')


def get_command_arguments(*args):
    """Return command arguments.

    Return command arguments as string to feed the script.
    Command arguments are separated by a space and
    with escaped " or ' characters if present in arguments.
    Uses recursion if argument is a list.

    Returns:
        (str): Command arguments as string
    """
    command = ""
    for arg in args:
        if isinstance(arg, list):
            return get_command_arguments(arg)
        else:
            command = str(command) + ' ' + str(sanitize_arg(arg))
    return command


# A list of configuration options that control the execution of the test cases.
# Used with get_config_opts function.
fut_test_config_opts = [
    'test_script_timeout',
    'skip',
    'skip_msg',
    'xfail',
    'xfail_msg',
    'ignore_collect',
]


def get_config_opts(config):
    """Iterate over test configurations and return dictionary of options.

    Dictionary is made of present test options from fut_test_config_opts list.

    Args:
        config (dict): Dictionary to iterate through

    Returns:
        (dict): _description_
    """
    if not isinstance(config, dict):
        return {}
    try:
        fut_opts = {}
        for topt in fut_test_config_opts:
            if topt in config:
                fut_opts[topt] = config[topt]
        return fut_opts
    except Exception:
        return {}


def get_info_dump(std_out):
    """Get INFO-DUMP log section of the report.

    Function returns the INFO-DUMP section as a list of strings.

    Args:
        std_out (str): Text to generate INFO-DUMP from.

    Returns:
        (list): INFO-DUMP as a list of strings
    """
    info_dump = []
    if isinstance(std_out, str):
        std_out = std_out.split('\n')

    try:
        info_dump_indices = [i for i, x in enumerate(std_out) if 'FUT-INFO-DUMP' in x]
        info_dump_pairs = []
        for i in range(0, len(info_dump_indices), 2):
            info_dump_pairs.append((info_dump_indices[i], info_dump_indices[i + 1]))

        for info_dump_s_e in info_dump_pairs:
            start_i = info_dump_s_e[0]
            end_i = info_dump_s_e[1]
            info_dump += std_out[start_i:end_i]
            for i in range(start_i, end_i):
                std_out[i] = None
        std_out = [i for i in std_out if i]
    except Exception as e:
        log.warning(f'Failed to generate INFO-DUMP section\n{e}')
    try:
        std_out = '\n'.join(std_out)
    except Exception:
        pass
    try:
        info_dump = '\n'.join(info_dump)
    except Exception:
        pass
    return std_out, info_dump


def get_section_line(d_name='', cmd='', out_type='', out_time=''):
    """Get section line.

    Function returns section line with provided markers as string.

    Args:
        d_name (str, optional): Device name. Defaults to ''.
        cmd (str, optional): Command executed. Defaults to ''.
        out_type (str, optional): Output type. Defaults to ''.
        out_time (str, optional): Output time. Defaults to ''.

    Returns:
        (str): Section line as string
    """
    d_name = f' - {d_name}' if d_name != '' else d_name
    out_type = f' - {out_type}' if out_type != '' else out_type
    out_time = f' - {out_time}' if out_time != '' else out_time
    cmd = f' - {cmd}' if cmd != '' else cmd
    l_bang_n = 10
    r_bang_n = 9 if out_type == 'stop' else 10
    return f'{l_bang_n * "#"} {d_name}{cmd}{out_type}{out_time} {r_bang_n * "#"}'


def load_reg_rule():
    """Load regulatory rules from regulatory.yaml file.

    Returns:
        (dict): regulatory rules dictionary
        (None): on exception or failure
    """
    full_path = f'{str(Path(__file__).absolute()).split("framework")[0]}/config/rules/regulatory.yaml'
    try:
        with open(full_path) as reg_rule_file:
            return yaml.safe_load(reg_rule_file)
    except Exception as e:
        log.warning(f'Failed to load regulatory domain rules from {full_path}\n{e}')
    return None


def map_dict_key_path(dictionary, key_mem=""):
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
            result += map_dict_key_path(value, f'{key_mem}{key}_')
        else:
            result.append((f'{key_mem}{key}', value))
    return result


def output_to_json(data, json_file=None, sort_keys=True, indent=4, convert_only=False):
    """Output given data to JSON file.

    Args:
        data (JSON serializable data, dict(), list() etc.)
        json_file (str): Path to JSON file
        sort_keys (bool): sort output of dictionaries by key
        indent (int): pretty-print object members with specified indent level
        convert_only (bool): only convert data to JSON format without writing to file

    Raises:
        Exception: Failed to output data to JSON file

    Returns:
        (bool): True
        (str): JSON string if convert_only is set to True
    """
    try:
        if convert_only:
            json_string = json.dumps(data, indent=indent)
            return json_string
        with open(json_file, 'w') as jsf:
            jsf.write(json.dumps({'data': data}, sort_keys=sort_keys, indent=indent))
    except Exception as e:
        raise Exception(f'Failed to output data to JSON file {e}')
    return True


def print_allure(message):
    """Direct the message to standard output and attach it to the Allure report.

    Args:
        message (str): Message to be attached
    """
    print(message)
    allure.attach(
        name='OUTPUT',
        body=message,
    )


def sanitize_arg(arg):
    """Sanitize the argument of selected characters.

    Note:
    Could use quote() from pipes but suspecting at test execution instability
    so just escape args that contain spaces.

    Args:
        arg (str): Argument to be cleared

    Returns:
        (str): Cleared argument
    """
    try:
        # Argument is surronuded by "" or '' or starts with -
        if (arg[0] == '"' and arg[-1] == '"') or (arg[0] == "'" and arg[-1] == "'") or (arg[0] == '-'):
            arg = arg
        elif " " in arg:
            if '"' in arg:
                arg = arg.replace('"', '\"')
            arg = f'"{arg}"'
        else:
            arg = arg
    except Exception:
        arg = arg
    return arg


def step(step_title):
    """Get step mark.

    Formats step mark for Allure report.
    Adds colon to step title.

    Args:
        step_title (str): Step title

    Returns:
        _type_: Allure step mark
    """
    return allure.step(f'{step_title}:')


def validate_channel_ht_mode_band(channel, ht_mode='HT20', radio_band=None, regulatory_rule=None, reg_domain='US', raise_broken=False):
    """Verify if the selected channel, ht_mode and radio_band are configured regulatory domain.

    Args:
        channel (int): WiFi channel
        ht_mode (str): supported "HT20", "HT2040", "HT40", "HT40+", "HT40-", "HT80", "HT160", "HT80+80"
        radio_band (str): supported "24g", "5g", "6g", "5gl" and "5gu" are transformed into "5g"
        reg_domain (str): supported "US", "EU", "GB", "JP" defaulted to US

    Returns:
        bool: True for success, raises exception otherwise.
    """
    assert ht_mode in ["HT20", "HT2040", "HT40", "HT40+", "HT40-", "HT80", "HT160", "HT80+80"]
    if not regulatory_rule:
        log.warning('Regulatory rules not found, loading')
        regulatory_rule = load_reg_rule()
    try:
        if channel not in regulatory_rule[reg_domain.upper()]['band'][radio_band.lower()][ht_mode.upper()]:
            msg = f'Incorrect combination of parameters: channel:{channel}, ht_mode:{ht_mode.upper()}, band:{radio_band.lower()}, regulatory domain: {reg_domain.upper()}'
            log.warning(msg)
            if raise_broken:
                raise BrokenException(msg)
        else:
            return True
    except BrokenException as e:
        log.error(e)
    except Exception as e:
        log.warning(f'Failed to validate channel {channel}[{ht_mode}] for {radio_band} against regulatory rules for {reg_domain.upper()}\n{e}')
    return False
