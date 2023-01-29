import sys

import allure

import framework.tools.logger
from config.model.generic.fut_gen import FutTestConfigGenClass

sys.path.append('../../../')

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def sm_gen_instance():
    return FutTestConfigGenClass("PP603X", "PP603X").test_generators


@allure.title("Validate SmGen generator")
class TestSmGen:
    @allure.title("Validate _parse_sm_inputs() method")
    def test_parse_sm_inputs_no_args_mapping_key(self):
        smgen = sm_gen_instance()
        inputs = {
            'key_1': 'value_1',
            'key_2': 'value_2',
        }
        expected = inputs
        actual = smgen._parse_sm_inputs(inputs)
        assert actual == expected

    @allure.title("Validate _parse_sm_inputs() method")
    def test_parse_sm_inputs(self):
        smgen = sm_gen_instance()
        inputs = {
            'TEST-NAME': {
                'args_mapping': [
                    "channel", "ht_mode", "radio_band", "if_name", "if_type",
                ],
                'inputs': [
                    [6, "HT20", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
                    [6, "HT20", "24g", 'FutGen|vif-bhaul-sta-by-band-and-type'],
                ],
            },
        }
        expected = inputs
        actual = smgen._parse_sm_inputs(inputs)
        assert actual == expected

    @allure.title("Validate gen_sm_leaf_report() method")
    def test_gen_sm_leaf_report(self):
        smgen = sm_gen_instance()
        inputs = {
            'TEST-NAME': {
                'args_mapping': [
                    "channel", "ht_mode", "radio_band", "if_name", "if_type",
                ],
                'inputs': [
                    [6, "HT20", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
                    [6, "HT20", "24g", 'FutGen|vif-bhaul-sta-by-band-and-type'],
                ],
            },
        }
        expected = smgen.default_gen(inputs)
        actual = smgen.gen_sm_leaf_report(inputs)
        assert actual == expected

    @allure.title("Validate gen_sm_neighbor_report() method")
    def test_gen_sm_neighbor_report(self):
        smgen = sm_gen_instance()
        inputs = {
            'TEST-NAME': {
                'args_mapping': [
                    "channel", "ht_mode", "radio_band", "if_name", "if_type",
                ],
                'inputs': [
                    [6, "HT20", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
                    [6, "HT20", "24g", 'FutGen|vif-bhaul-sta-by-band-and-type'],
                ],
            },
        }
        expected = smgen.default_gen(inputs)
        actual = smgen.gen_sm_neighbor_report(inputs)
        assert actual == expected
