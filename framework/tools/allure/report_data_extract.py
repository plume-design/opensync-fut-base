#!/usr/bin/env python3

import argparse
import datetime
import json
from pathlib import Path

# sudo pip3 install rich
from rich.pretty import pprint


class AllureDataExtract:
    def __init__(
        self,
        report_path,
    ):
        self.summary_path = Path(f"{report_path}/widgets/summary.json")
        self.environment_path = Path(f"{report_path}/widgets/environment.json")
        self.suites_path = Path(f"{report_path}/data/suites.json")
        self.test_cases_path = Path(f"{report_path}/data/test-cases")

        self.report_data = {
            "summary": {},
            "test_data": {},
        }
        self.process_summary()
        self.process_env_var()
        self.process_test_cases()

    @staticmethod
    def load_json_data(path):
        if not path.exists():
            raise FileNotFoundError(f"File {path} cannot be found.")
        with open(f"{path}") as json_file:
            data = json.load(json_file)
        return data

    def process_env_var(self):
        environment = self.load_json_data(self.environment_path)
        # Environment variables
        env_dict = {}
        for env in environment:
            if env["name"] != "[Global]":
                env_dict[env["name"]] = env["values"][0]
        self.report_data["summary"]["environment"] = env_dict

    def process_summary(self):
        # Execution times
        summary = self.load_json_data(self.summary_path)
        datetime_start = datetime.datetime.fromtimestamp(int(summary["time"]["start"] / 1000))
        datetime_stop = datetime.datetime.fromtimestamp(int(summary["time"]["stop"] / 1000))
        datetime_duration = datetime.timedelta(seconds=int(summary["time"]["duration"] / 1000))
        self.report_data["summary"]["times"] = {
            "start": datetime_start,
            "stop": datetime_stop,
            "duration": datetime_duration,
        }

    def process_test_cases(self):
        suites = self.load_json_data(self.suites_path)
        # Test details per each test configuration
        all_results = {}
        for suite in suites["children"][0]["children"]:
            suite_name = suite["name"]
            if suite_name not in all_results:
                all_results[suite_name] = {}
                all_results[suite_name]["all"] = 0
                all_results[suite_name]["tests"] = {}

            # Iterate over all tests in the suite
            for test in suite["children"]:
                uid = test["uid"]
                name = test["name"]
                status = test["status"]
                parameters = test["parameters"]
                try:
                    test_data = self.load_json_data(Path(f"{self.test_cases_path}/{uid}.json"))
                    test_attachments = test_data["testStage"]["attachments"]
                except Exception:
                    test_attachments = None

                if name not in all_results[suite_name]["tests"]:
                    all_results[suite_name]["tests"][name] = {
                        "status": status,
                        "parameters": parameters,
                        "attachments": test_attachments,
                    }
                if status not in all_results[suite_name]:
                    all_results[suite_name][status] = 0
                all_results[suite_name][status] += 1
                all_results[suite_name]["all"] += 1
        self.report_data["test_data"] = all_results


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Tool to extract Allure report data to Python Dictionary - PrettyPrints to Terminal",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "report_path",
        metavar="path",
        type=str,
        default=".",
        help="The path to the Allure report root folder. If not specified, current folder will be used.",
    )
    input_args = parser.parse_args()
    return input_args


def main():
    input_args = parse_arguments()
    report_path = input_args.report_path

    allure_data_extractor = AllureDataExtract(report_path=report_path)
    pprint(allure_data_extractor.report_data)


if __name__ == "__main__":
    main()
