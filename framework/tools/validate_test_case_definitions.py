#!/usr/bin/python3
"""
Validate test case definitions.

This script collects all the implemented test cases in the 'test/'
directory and verifies if a test case definition is present in the
'doc/' directory
"""
import glob
import os
from pathlib import Path


def main():
    fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
    stream = os.popen(rf"cd {fut_base_dir}/test && grep -rohP '(?<=test_)(?s).*(?=\(self, cfg\))'")
    test_cases = stream.read()
    test_case_list = test_cases.strip().split("\n")
    definition_list = []
    implementation_list = [test_case for test_case in test_case_list if not test_case.endswith("setup")]

    for file in glob.glob(f"{fut_base_dir}/doc/definitions/**/*.md", recursive=True):
        file_name = os.path.split(file)[1].split(".md")[0]
        definition_list.append(file_name)
        definition_list = [
            test_case
            for test_case in definition_list
            if not test_case.endswith("template") and not test_case.endswith("suite")
        ]

    # Check which tests have been implemented but are not defined
    implemented_but_not_defined = []
    for test in implementation_list:
        if test not in definition_list:
            implemented_but_not_defined.append(test)

    # Check which tests have been defined but are not implemented
    defined_but_not_implemented = []
    for test in definition_list:
        if test not in implementation_list:
            defined_but_not_implemented.append(test)

    if not implemented_but_not_defined:
        print("All implemented FUT tests have been defined.")
    else:
        print(
            f"The following tests have no definition in the fut_base/doc/definitions/ directory: {implemented_but_not_defined}",
        )

    if not defined_but_not_implemented:
        print("All defined FUT tests have been implemented.")
    else:
        print(
            f"The following defined in the fut_base/doc/definitions/ directory have not been implemented: {defined_but_not_implemented}",
        )


if __name__ == "__main__":
    main()
