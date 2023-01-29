#!/usr/bin/env python3

import argparse
import glob
import importlib.util
import json
import os
import re
import shutil
import sys
from copy import deepcopy
from pathlib import Path

topdir_path = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(topdir_path)


object_open_regex = re.compile(r'(\")(.*?)(\")(\s*):(\s*){')
list_key_regex = re.compile(r'(\")(.*?)(\")(\s*):(\s*)\[')
INDENT = 4


def get_comment_block(cfg_lines, start_from):
    """Return list of strings containing comments."""
    cfg_lines_count = len(cfg_lines)
    comment_block = []
    for cfg_line_index in range(start_from, cfg_lines_count):
        current_cfg_line = cfg_lines[cfg_line_index]
        first_char = list(current_cfg_line)[len(current_cfg_line) - len(current_cfg_line.lstrip())]
        if first_char == "#":
            comment_block.append(current_cfg_line)
        else:
            break
    return comment_block


def get_comment_from_map(line_with_comment, comment_map):
    if line_with_comment in ['before_test_cfg', 'after_test_cfg']:
        comment_id = line_with_comment
    elif "_comment_object_identifier" in line_with_comment:
        comment_id = re.search(r'(comment_object_identifier_).*(?=")', line_with_comment).group()
    else:
        comment_id = re.search(r'(comment_identifier_).*(?=")', line_with_comment).group()

    for comment_info in comment_map:
        if comment_info['comment_id'] == comment_id:
            return comment_info['comment_block']
    return ""


def get_comment_location(cfg_lines, comment_index, var_name):
    lists_opened = 0
    lists_closed = 0
    objects_opened = 0
    objects_closed = 0
    cfg_line_index = 0

    for cfg_line_index in reversed(range(0, comment_index)):
        current_cfg_line = cfg_lines[cfg_line_index]
        first_char = current_cfg_line[len(current_cfg_line) - len(current_cfg_line.lstrip())]
        current_cfg_line_strip = current_cfg_line.strip()
        if first_char != "#":
            if current_cfg_line_strip in ["]", "],"]:
                lists_closed += 1
            elif re.search(object_open_regex, current_cfg_line) or current_cfg_line_strip == "{":
                objects_opened += 1
            elif re.search(list_key_regex, current_cfg_line) or current_cfg_line_strip == "[":
                lists_opened += 1
            elif current_cfg_line_strip in ["}", "},"]:
                objects_closed += 1

            if lists_opened > lists_closed:
                return 'array'
            elif (objects_opened > objects_closed) or (
                first_char == "{" and objects_closed == 0 and "}" not in current_cfg_line_strip) or (
                    var_name + " = {" in current_cfg_line):
                return 'object'

    return "after_test_cfg"


def insert_trailing_comma(sorted_cfg_lines):
    """ Insert trailing comma to dicts and lists.
    Doing this manually, one would, for example:
      find:     (^(?![\}])((?![\[\{,]).)*$)
      replace:  $1,
    Known limitation: does not support adding trailing comma to empty dict
    Known limitation: does not support adding trailing comma to dict value containing square braces
    """  # noqa
    if isinstance(sorted_cfg_lines, str):
        # Majority of lines
        sorted_cfg_lines_with_comma = re.sub(
            r'(^(?!\})((?![\[\{,]).)*$)',
            r'\1,',
            sorted_cfg_lines,
        )
        # Empty dicts on single line
        sorted_cfg_lines_with_comma = re.sub(
            r'(^.*)([ ]{1,})(\{\})$',
            r'\1\2\3,',
            sorted_cfg_lines_with_comma,
        )
        # Dict or list values containing special characters, if they are quoted
        sorted_cfg_lines_with_comma = re.sub(
            r'(^[ ]{1,})(["\'].*["\'])(?![,])$',
            r'\1\2,',
            sorted_cfg_lines_with_comma,
        )
    elif isinstance(sorted_cfg_lines, list):
        sorted_cfg_lines_with_comma = []
        for line in sorted_cfg_lines:
            sorted_cfg_lines_with_comma.append(insert_trailing_comma(line))
    else:
        raise ValueError
    return sorted_cfg_lines_with_comma


def map_comments_to_lines(cfg_lines, var_name):
    mapped_cfg_lines = []
    comment_map = []
    skip_n_lines = 0
    comment_id = 1000
    for cfg_line_index, current_cfg_line in enumerate(cfg_lines):
        # skip lines if there are comments ahead
        if skip_n_lines > 1:
            skip_n_lines -= 1
            continue

        first_char = current_cfg_line[len(current_cfg_line) - len(current_cfg_line.lstrip())]
        if first_char != "#":
            # Use original line if not comment
            mapped_cfg_lines.append(current_cfg_line)
            continue

        comment_block = get_comment_block(cfg_lines=cfg_lines, start_from=cfg_line_index)
        skip_n_lines = len(comment_block)

        if cfg_line_index == 0:
            # comments before test_cfg dictionary
            comment_id_string = 'before_test_cfg'
        elif cfg_line_index + skip_n_lines >= len(cfg_lines):
            # comments after test_cfg dictionary
            comment_id_string = 'after_test_cfg'
        else:
            # Transform comment into sortable cfg line entry and append to config
            comment_location = get_comment_location(cfg_lines=cfg_lines, comment_index=cfg_line_index, var_name=var_name)
            if comment_location == 'array':
                # Inside lists, comments are represented only by key
                comment_id_string = f'comment_identifier_{comment_id}'
                identifier_key_line = f'"{comment_id_string}",\n'
            elif comment_location == 'object':
                # Inside dictionaries comments get key and value pair
                comment_id_string = f'comment_object_identifier_{comment_id}'
                next_line = cfg_lines[cfg_line_index + skip_n_lines]
                if next_line and re.search(r'(\")(.*?)(\")(\s*)(\:)', next_line):
                    next_key_value = re.search(r'(\")(.*?)(\")(\s*)(\:)', next_line)
                    # If there is a next key value, use its name for the comment token, so sorting will work
                    sort_str = next_key_value.group().replace('\"', '').replace(':', '')[:-1]
                else:
                    # If there is no next key value inside the object, use "zzz" to ensure it is sorted last
                    sort_str = "zzz"
                identifier_key_line = f'"{sort_str}_comment_object_identifier":"{comment_id_string}",\n'

            last_mapped_line = mapped_cfg_lines[-1]
            if last_mapped_line and last_mapped_line.strip()[-1] not in ['[', '{', ',']:
                identifier_key_line = f',{identifier_key_line}'
            mapped_cfg_lines.append(identifier_key_line)
            comment_id += 1

        # Append comment block to comment_map in all cases where first character is "#"
        comment_map.append({'comment_id': comment_id_string, "comment_block": comment_block})

    return mapped_cfg_lines, comment_map


def sort_configuration(opts, cfg_file_path):
    cfg_file_path_split = cfg_file_path.split('/')
    cfg_module_name = cfg_file_path_split[-1].replace('.py', '')

    # Read raw configuration
    with open(cfg_file_path) as f:
        cfg_lines_raw = f.readlines()
    # Remove empty newlines from configuration
    cfg_lines_initial = [line for line in cfg_lines_raw if line != '\n']
    # Replace comments with sortable string entries and write to file for subsequent import
    cfg_lines_mapped, comment_map = map_comments_to_lines(cfg_lines=deepcopy(cfg_lines_initial), var_name=opts.variable)
    mapped_cfg_filename = cfg_file_path.replace('.py', '.mapped.py')
    with open(mapped_cfg_filename, "w") as mapped_cfg_file:
        mapped_cfg_file.writelines(cfg_lines_mapped)

    # Import file so it can be sorted as python structure
    spec = importlib.util.spec_from_file_location(cfg_module_name, mapped_cfg_filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[cfg_module_name] = module
    spec.loader.exec_module(module)  # module contents come into namespace
    cfg = eval(f'module.{opts.variable}')

    # Sort list of lines as JSON dumps:
    sorted_cfg_file_lines = json.dumps(cfg, sort_keys=True, indent=INDENT, ensure_ascii=False).split("\n")
    # Trailing commas are optimized out:
    sorted_cfg_file_lines = insert_trailing_comma(sorted_cfg_lines=sorted_cfg_file_lines)
    # Insert comments back
    sorted_cfg_file_with_comments_lines = write_comments_back(
        sorted_cfg_lines=sorted_cfg_file_lines,
        comment_map=comment_map,
    )
    # Convert json syntax to python syntax
    for idx, line in enumerate(sorted_cfg_file_with_comments_lines):
        for repl_src, repl_dst in [('true', 'True'), ('false', 'False'), ('null', 'None')]:
            if repl_src in line and f'\"{repl_src}\"' not in line:
                sorted_cfg_file_with_comments_lines[idx] = re.sub(fr"\b{repl_src}\b", repl_dst, line)

    try:
        test_cfg_file = open(cfg_file_path, "w")
        for line in sorted_cfg_file_with_comments_lines:
            test_cfg_file.write(line)
        test_cfg_file.close()
        print(f'Configuration successfully sorted: {cfg_file_path}')
        os.remove(mapped_cfg_file.name)
    except Exception as error:
        print('Errors encountered')
        if opts.backup:
            shutil.copy2(f'{absolute_path}.orig', absolute_path)
        print(error)


def write_comments_back(sorted_cfg_lines, comment_map):
    commented_cfg_lines = []
    for sorted_line in sorted_cfg_lines:
        if "comment_identifier_" in sorted_line:
            comment_block_to_insert = get_comment_from_map(
                line_with_comment=sorted_line,
                comment_map=comment_map,
            )
            for comment_line in comment_block_to_insert:
                commented_cfg_lines.append(comment_line)
        elif "zzz_comment_object_identifier" in sorted_line:
            comment_block_to_insert = get_comment_from_map(
                line_with_comment=sorted_line,
                comment_map=comment_map,
            )
            for comment_line in comment_block_to_insert:
                commented_cfg_lines.append(comment_line)
        elif "_comment_object_identifier" in sorted_line:
            comment_block_to_insert = get_comment_from_map(
                line_with_comment=sorted_line,
                comment_map=comment_map,
            )
            last_line_index = len(commented_cfg_lines) - 1
            if commented_cfg_lines[last_line_index].strip() in ['],', ']']:
                commented_cfg_lines = commented_cfg_lines + comment_block_to_insert
            else:
                comment_line_number = 1
                for comment_line in comment_block_to_insert:
                    commented_cfg_lines.insert(last_line_index + comment_line_number, comment_line)
                    comment_line_number += 1
        else:
            commented_cfg_lines.append(sorted_line + "\n")

    pre_post_commented_cfg_lines = write_pre_post_cfg_comments_back(commented_cfg_lines, comment_map)

    return pre_post_commented_cfg_lines


def write_pre_post_cfg_comments_back(commented_cfg_lines, comment_map):
    pre_test_cfg_comments = get_comment_from_map(line_with_comment='before_test_cfg', comment_map=comment_map)
    comment_line_number = 0
    for line in pre_test_cfg_comments:
        commented_cfg_lines.insert(0 + comment_line_number, line)
        comment_line_number += 1

    post_test_cfg_comments = get_comment_from_map(line_with_comment='after_test_cfg', comment_map=comment_map)
    for line in post_test_cfg_comments:
        commented_cfg_lines.append(line)

    if len(commented_cfg_lines) == 1:
        commented_cfg_lines[comment_line_number] = opts.variable + " = {}\n"
    else:
        commented_cfg_lines[comment_line_number] = opts.variable + " = {\n"

    return commented_cfg_lines


if __name__ == '__main__':
    tool_description = """
    Sort FUT testcase configuration file
    Before sorting the config file, make sure the following requirements are met:
      file contains variable "test_cfg"
      if the variable name that contains content intended for sorting is different, see optional arguments

    Example of usage:
    python3 cfg_sort.py --cfg ~/config.py -var custom_variable_name'
    """

    # Instantiate the parser
    parser = argparse.ArgumentParser(
        description=tool_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Define options
    parser.add_argument(
        '--cfg',
        required=True,
        type=str,
        help='Full/absolute path to configuration file',
    )
    parser.add_argument(
        '--backup',
        required=False,
        default=False,
        action="store_true",
        help='Create backup of original config file in <cfgname>.orig',
    )
    parser.add_argument(
        '--variable',
        required=False,
        type=str,
        default='test_cfg',
        help='Name of variable value to sort',
    )
    parser.add_argument(
        '--recursive',
        required=False,
        type=str,
        default=False,
        help='Recursive sort all files within given directory, matching filename\n'
             'Example: python3 cfg_sort.py --cfg config/model/ --recursive _config.py',
    )
    opts = parser.parse_args()

    if bool(opts.recursive) == Path(opts.cfg).is_file():
        print('Recursion can be done for folders, not files!')
        sys.exit(1)
    if not any([Path(opts.cfg).is_dir(), Path(opts.cfg).is_file()]):
        print(f'Argument "cfg":{opts.cfg} has to be path to dir or file!')
        sys.exit(1)

    configs_to_sort = []
    if bool(opts.recursive):
        for absolute_path in glob.iglob(opts.cfg + '/**/*' + opts.recursive, recursive=True):
            if not Path(absolute_path).is_file():
                print(f'Error: {absolute_path} is not file, skipping.')
                continue
            configs_to_sort.append(absolute_path)
        if not configs_to_sort:
            print(f'No files gathered in {opts.cfg} for {opts.recursive}')
            sys.exit(0)
    else:
        configs_to_sort.append(opts.cfg)

    for absolute_path in configs_to_sort:
        if opts.backup:
            shutil.copy2(absolute_path, f'{absolute_path}.orig')
        try:
            sort_configuration(opts=opts, cfg_file_path=absolute_path)
        except Exception as e:
            print(f'--- Failed to sort configuration {absolute_path}\n{e}')

    sys.exit(0)
