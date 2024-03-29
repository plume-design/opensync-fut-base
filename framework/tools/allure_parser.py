#!/usr/bin/env python3

"""Tool to parse, extract, and compare data from test reports."""

import argparse
import signal
import sys
from pathlib import Path

from framework.lib.fut_allure import (
    determine_mismatches,
    read_data_from_report,
    read_data_from_results,
    results_alignment,
    split_common_entries,
)
from framework.lib.fut_lib import output_to_json


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description="Parse and extract data from test reports",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--current",
        "-c",
        type=str,
        required=True,
        help="Name of the current test directory containing pytest results",
    )
    parser.add_argument(
        "--reference",
        "-r",
        type=str,
        required=True,
        help="Name of the reference test directory containing either pytest results or Allure report",
    )
    parser.add_argument(
        "--output_file",
        "-o",
        type=str,
        required=False,
        help="Output extracted data to specified file instead of stdout",
    )
    parser.add_argument(
        "--sort_keys",
        "-s",
        action="store_true",
        default=False,
        help="Sort keys when storing information from python dicts to JSON format",
    )
    parser.add_argument(
        "--hide_common",
        "-H",
        action="store_true",
        default=False,
        help="Hide tests common in the current and reference runs, with matching status, from stdout",
    )
    parser.add_argument(
        "--hide_current_specific",
        "-C",
        action="store_true",
        required=False,
        help="Hide tests specific to the current run, not present in the reference run, from stdout",
    )
    parser.add_argument(
        "--hide_reference_specific",
        "-R",
        action="store_true",
        required=False,
        help="Hide tests specific to the reference run, not present in the current run, from stdout",
    )
    parser.add_argument(
        "--hide_filtered",
        "-F",
        action="store_true",
        required=False,
        help="Hide filtered tests from stdout",
    )
    parser.add_argument(
        "--hide_removed",
        "-D",
        action="store_true",
        required=False,
        help="Hide removed tests from stdout",
    )
    parser.add_argument(
        "--hide_mismatched",
        "-M",
        action="store_true",
        required=False,
        help="Hide mismatched tests from stdout",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        required=False,
        help="Mute logging from stdout",
    )
    input_args = parser.parse_args()
    return input_args


def signal_handler(sig, frame):
    """Handle the signal.

    Args:
        sig (_type_): Not used
        frame (_type_): Not used
    """
    sys.exit(0)


def create_report(
    cur_data_specific_entries: list or None,
    ref_data_specific_entries: list or None,
    common_entries: list or None,
    filtered_entries: list or None,
    removed_entries: list or None,
    mismatch_entries: list or None,
    **kwargs,
):
    """
    Create a JSON printable report from the extracted and processed data.

    Args:
        cur_data_specific_entries (list): Tests specific to the current test run
        ref_data_specific_entries (list): Tests specific to the reference test run
        common_entries (list): Tests from the current test run that appear in both runs
        filtered_entries (list): Tests from the current test run that appear in both runs, filtered by status
        removed_entries (list): Tests removed from the current test run based on the reference status
        mismatch_entries (list): Tests from current run whose status mismatch with the reference run
    Kwargs:
        sort_keys (bool): sort dict keys when outputting to JSON
    Returns:
        json_report (string): A printable JSON format report of the input data
    """
    sort_keys = kwargs.get("sort_keys", False)
    json_report_list = []
    if cur_data_specific_entries:
        json_report_list.extend(
            [
                "Test cases specific to the current test run:",
                f"{output_to_json(cur_data_specific_entries, sort_keys=sort_keys, convert_only=True)}",
            ],
        )
    if ref_data_specific_entries:
        json_report_list.extend(
            [
                "Test cases specific to the reference test run:",
                f"{output_to_json(ref_data_specific_entries, sort_keys=sort_keys, convert_only=True)}",
            ],
        )
    if common_entries:
        json_report_list.extend(
            [
                "Test cases common to both test runs:",
                f"{output_to_json(common_entries, sort_keys=sort_keys, convert_only=True)}",
            ],
        )
    if filtered_entries:
        json_report_list.extend(
            [
                "Test cases common to both test runs filtered by status:",
                f"{output_to_json(filtered_entries, sort_keys=sort_keys, convert_only=True)}",
                "",
            ],
        )
    if removed_entries:
        json_report_list.extend(
            [
                "Test cases removed from common tests based on the status:",
                f"{output_to_json(removed_entries, sort_keys=sort_keys, convert_only=True)}",
                "",
            ],
        )
    if mismatch_entries:
        json_report_list.extend(
            [
                "Mismatch report:",
                f"{output_to_json(mismatch_entries, sort_keys=sort_keys, convert_only=True)}",
                "",
            ],
        )
    json_report_list.extend([""])
    json_report = "\n".join(json_report_list)
    return json_report


def create_stats(
    cur_data_specific_entries: list,
    ref_data_specific_entries: list,
    common_entries: list,
    filtered_entries: list,
    removed_entries: list,
    mismatch_entries: list,
):
    """
    Create a printable statistics report from the extracted and processed data.

    Args:
        cur_data_specific_entries (list): Tests specific to the current test run
        ref_data_specific_entries (list): Tests specific to the reference test run
        common_entries (list): Tests from the current test run that appear in both runs
        filtered_entries (list): Tests from the current test run that appear in both runs, filtered by status
        removed_entries (list): Tests removed from the current test run based on the reference status
        mismatch_entries (list): Tests from current run whose status mismatch with the reference run
    Returns:
        stats_report (string): A stats report of the input data
    """
    stats_report = "\n".join(
        [
            "Stats report:",
            f"\t{len(cur_data_specific_entries)}\tCurrent only",
            f"\t{len(ref_data_specific_entries)}\tReference only",
            f"\t{len(common_entries)}\tCommon",
            f"\t{len(filtered_entries)}\tFiltered",
            f"\t{len(removed_entries)}\tRemoved",
            f"\t{len(mismatch_entries)}\tMismatches",
            "",
        ],
    )
    return stats_report


if __name__ == "__main__":
    # Accept Ctrl+C as a signal interrupt
    signal.signal(signal.SIGINT, signal_handler)

    # Parse input arguments
    input_args = parse_arguments()
    output_file = input_args.output_file
    sort_keys = input_args.sort_keys

    if input_args.quiet:
        import logging
        from lib_testbed.generic.util.logger import LOGGER_NAME

        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.ERROR)

    # Assert that current data are Pytest results
    assert not Path(input_args.current).joinpath("index.html").is_file()
    extracted_current_data = read_data_from_results(source_directory=input_args.current)

    # Detect if reference data are Pytest results or Allure report
    if Path(input_args.reference).joinpath("index.html").is_file():
        _read_data = read_data_from_report
    else:
        _read_data = read_data_from_results
    extracted_reference_data = _read_data(source_directory=input_args.reference)

    cur_data_specific_entries, ref_data_specific_entries, common_entries = results_alignment(
        current_data=extracted_current_data,
        reference_data=extracted_reference_data,
    )

    mismatch_entries = determine_mismatches(common_entries)

    filtered_entries, removed_entries = split_common_entries(common_entries)

    json_report = create_report(
        [] if input_args.hide_current_specific else cur_data_specific_entries,
        [] if input_args.hide_reference_specific else ref_data_specific_entries,
        [] if input_args.hide_common else common_entries,
        [] if input_args.hide_filtered else filtered_entries,
        [] if input_args.hide_removed else removed_entries,
        [] if input_args.hide_mismatched else mismatch_entries,
        sort_keys=sort_keys,
    )
    stats_report = create_stats(
        cur_data_specific_entries,
        ref_data_specific_entries,
        common_entries,
        filtered_entries,
        removed_entries,
        mismatch_entries,
    )

    if output_file:
        full_report = {
            "specific_to_current": cur_data_specific_entries,
            "specific_to_reference": ref_data_specific_entries,
            "common": common_entries,
            "filtered": filtered_entries,
            "removed": removed_entries,
            "mismatches": mismatch_entries,
        }
        output_to_json(full_report, output_file, sort_keys=sort_keys)
    else:
        # Write the filtered test report comparison results to standard output
        sys.stdout.write(json_report)
        sys.stdout.write(stats_report)
