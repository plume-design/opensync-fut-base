#!/usr/bin/env python3

"""Tool to process pytest results from FUT runs based on the provided reference results or a report."""

import argparse
from pathlib import Path

from framework.lib.fut_allure import (
    create_processed_results,
    read_data_from_report,
    read_data_from_results,
    results_alignment,
    split_common_entries,
)


def parse_arguments():
    """Standalone method to parse script input arguments."""
    parser = argparse.ArgumentParser(
        description="Parse and extract data from test results or reports",
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
        "--backup",
        "-b",
        action="store_true",
        required=False,
        help="Create a backup folder of the current test results",
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


if __name__ == "__main__":
    input_args = parse_arguments()
    if input_args.quiet:
        import logging
        from lib_testbed.generic.util.logger import LOGGER_NAME

        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.ERROR)

    # Assert that current data are Pytest results
    assert not Path(input_args.current).joinpath("index.html").is_file()
    extracted_current_data = read_data_from_results(source_directory=input_args.current)

    # Detect if reference data are Pytest results or Allure report
    if Path(input_args.current).joinpath("index.html").is_file():
        _read_data = read_data_from_report
    else:
        _read_data = read_data_from_results
    extracted_reference_data = _read_data(source_directory=input_args.reference)

    aligned_results = results_alignment(current_data=extracted_current_data, reference_data=extracted_reference_data)
    common_entries = aligned_results[2]
    split_entries = split_common_entries(common_entries)
    removed_entries = split_entries[1]
    create_processed_results(input_args.current, removed_entries, input_args.backup)
