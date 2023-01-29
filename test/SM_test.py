import json

import allure
import pytest

import framework.tools.logger
from framework.tools.configure_ap_interface import configure_ap_interface
from framework.tools.create_gre_bhaul import create_and_configure_bhaul_connection_gw_leaf
from framework.tools.functions import check_if_dicts_match, FailedException, get_command_arguments, output_to_json, print_allure, step
from framework.tools.fut_mqtt_tool import extract_mqtt_data_as_dict
from framework.tools.set_device_mode import configure_device_mode
from framework.tools.validate_off_chan_survey import check_off_chan_scan_on_non_dfs_channel
from .globals import ExpectedShellResult, SERVER_HANDLER_GLOBAL

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


sm_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='SM')


@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="sm_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_sm_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='sm')
    server_handler.recipe.clear_full()
    with step('SM setup'):
        assert dut_handler.run('tests/sm/sm_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    with step('Put device into ROUTER mode'):
        assert configure_device_mode(device_name='dut', device_mode='router')
    server_handler.recipe.mark_setup()


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ref_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="sm_fut_setup_ref", depends=["compat_ref_ready", "sm_fut_setup_dut"], scope='session')
def test_sm_fut_setup_ref():
    server_handler, ref_handler = pytest.server_handler, pytest.ref_handler
    with step('Transfer'):
        assert ref_handler.clear_tests_folder()
        assert ref_handler.transfer(manager='sm')
    server_handler.recipe.clear()
    with step('SM setup'):
        assert ref_handler.run('tests/sm/sm_setup', ref_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.add_setup()


########################################################################################################################
test_sm_dynamic_noise_floor_inputs = sm_config.get("sm_dynamic_noise_floor", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_sm_dynamic_noise_floor_inputs)
@pytest.mark.dependency(depends=["sm_fut_setup_dut"], scope='session')
def test_sm_dynamic_noise_floor(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        mqtt_timeout = test_config.get("mqtt_timeout")
        mqtt_topic = test_config.get("mqtt_topic")
        sm_radio_type = test_config.get('sm_radio_type')
        sm_report_type = test_config.get('sm_report_type')
        sm_reporting_count = test_config.get('sm_reporting_count')
        sm_reporting_interval = test_config.get('sm_reporting_interval')
        sm_sampling_interval = test_config.get('sm_sampling_interval')
        sm_survey_type = test_config.get('sm_survey_type')
        stats_type = test_config.get("stats_type")

        noise_range_dbm = test_config.get("noise_range_dbm")

        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"
        noise_range_dbm_lower, noise_range_dbm_upper = noise_range_dbm[0], noise_range_dbm[1]

        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_max_message_count = 1
        location_id = "1000"
        node_id = "100"

        sm_dut_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        sm_server_mqtt_args = get_command_arguments(
            f'--hostname {mqtt_hostname}',
            f'--port {mqtt_port}',
            f'--topic {mqtt_topic}',
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f'--max_message_count {mqtt_max_message_count}',
            f'--timeout {mqtt_timeout}',
            f'--collect_messages {True}',
            f'--stdout_output {True}',
            f'--json_output {True}',
        )

        wifi_stats_config_args = get_command_arguments(
            'Wifi_Stats_Config',
            '-i', 'radio_type', f'{sm_radio_type}',
            '-i', 'report_type', f'{sm_report_type}',
            '-i', 'reporting_count', f'{sm_reporting_count}',
            '-i', 'reporting_interval', f'{sm_reporting_interval}',
            '-i', 'sampling_interval', f'{sm_sampling_interval}',
            '-i', 'stats_type', f'{stats_type}',
            '-i', 'survey_type', f'{sm_survey_type}',
        )

    with step('Statistics collection preparation'):
        # Remove any previous entries from the Wifi_Stats_Config table
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
    with step('Home AP creation'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
            device_name='dut',
            reset_vif=True,
        )
    with step('MQTT connection establishment and message collection'):
        assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/fut_configure_mqtt', sm_dut_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', wifi_stats_config_args, do_mqtt_log=True) == ExpectedShellResult
        sm_survey_result_ec, std_out, std_err = server_handler.run_raw('tools/fut_mqtt_tool', sm_server_mqtt_args, folder='framework', ext='.py')
        if sm_survey_result_ec != ExpectedShellResult or std_out == '' or std_out is None:
            raise FailedException('Failed to collect MQTT messages')
    with step('Data extraction'):
        # Access collected MQTT messages
        with open('/tmp/mqtt_messages.json', 'r') as mqtt_file:
            sm_mqtt_messages = json.load(mqtt_file)
        # Extract required data from MQTT messages
        extracted_data = extract_mqtt_data_as_dict(sm_mqtt_messages, ['noiseFloor'], simplify=True)
        extracted_noise_floor_value = extracted_data['noiseFloor']
        print_allure(f'The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}')
    with step('Testcase'):
        if noise_range_dbm_lower <= extracted_noise_floor_value <= noise_range_dbm_upper:
            print_allure(f'The extracted noise floor: \n{output_to_json(extracted_data, convert_only=True)}\n is within the specified range: {noise_range_dbm}')
        else:
            raise FailedException(f'The noise floor value {extracted_noise_floor_value} in not in the specified range: [{noise_range_dbm_lower}, {noise_range_dbm_upper}]')
    with step('Cleanup'):
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult


########################################################################################################################
test_sm_leaf_report_inputs = sm_config.get("sm_leaf_report", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_sm_leaf_report_inputs)
@pytest.mark.dependency(depends=["sm_fut_setup_dut", "sm_fut_setup_ref"], scope='session')
def test_sm_leaf_report(test_config):
    server_handler, dut_handler, ref_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get("channel")
        encryption = test_config.get("encryption", "WPA2")
        ht_mode = test_config.get("ht_mode")
        gw_radio_band = test_config.get("radio_band")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        device_mode = test_config.get("device_mode", "router")
        leaf_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, gw_radio_band)

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, gw_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, leaf_radio_band)

        mqtt_timeout = test_config.get("mqtt_timeout")
        mqtt_topic = test_config.get("mqtt_topic")
        sm_radio_type = test_config.get('sm_radio_type')
        sm_report_type = test_config.get('sm_report_type')
        sm_reporting_count = test_config.get('sm_reporting_count')
        sm_reporting_interval = test_config.get('sm_reporting_interval')
        sm_sampling_interval = test_config.get('sm_sampling_interval')
        sm_survey_type = test_config.get('sm_survey_type')
        stats_type = test_config.get("stats_type")

        gw_bhaul_ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_max_message_count = 1
        location_id = "1000"
        node_id = "100"

        sm_dut_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        sm_server_mqtt_args = get_command_arguments(
            f'--hostname {mqtt_hostname}',
            f'--port {mqtt_port}',
            f'--topic {mqtt_topic}',
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f'--max_message_count {mqtt_max_message_count}',
            f'--timeout {mqtt_timeout}',
            f'--collect_messages {True}',
            f'--stdout_output {True}',
            f'--json_output {True}',
        )

        wifi_stats_config_args = get_command_arguments(
            'Wifi_Stats_Config',
            '-i', 'radio_type', f'{sm_radio_type}',
            '-i', 'report_type', f'{sm_report_type}',
            '-i', 'reporting_count', f'{sm_reporting_count}',
            '-i', 'reporting_interval', f'{sm_reporting_interval}',
            '-i', 'sampling_interval', f'{sm_sampling_interval}',
            '-i', 'stats_type', f'{stats_type}',
            '-i', 'survey_type', f'{sm_survey_type}',
        )

    try:
        with step('VIF clean'):
            assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
        with step('Statistics collection preparation'):
            # Remove any previous entries from the Wifi_Stats_Config table
            assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
        with step(f'Put device into {device_mode.upper()} mode'):
            # 2. Configure device in device_mode mode
            assert configure_device_mode(device_name='dut', device_mode='router')
        with step('GW AP and LEAF STA creation, configuration and GW GRE configuration'):
            # On DUT - Create and configure GW bhaul AP interface
            # On REF - Create and configure LEAF bhaul STA interfaces
            # On DUT - Configure GRE tunnel
            assert create_and_configure_bhaul_connection_gw_leaf(channel, gw_radio_band, leaf_radio_band, ht_mode, wifi_security_type, encryption)
        with step('Determine REF MAC remotely at runtime'):
            ref_mac_args = get_command_arguments(
                'Wifi_VIF_State', 'mac', '-w', 'ssid', gw_bhaul_ssid,
            )
            leaf_mac_res = ref_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', ref_mac_args, print_out=True)
            assert leaf_mac_res[1] is not None and leaf_mac_res[1] != '' and leaf_mac_res[0] == ExpectedShellResult
        with step('MQTT connection establishment and message collection'):
            assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/fut_configure_mqtt', sm_dut_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
            assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', wifi_stats_config_args, do_mqtt_log=True) == ExpectedShellResult
            sm_survey_result_ec, std_out, std_err = server_handler.run_raw('tools/fut_mqtt_tool', sm_server_mqtt_args, folder='framework', ext='.py')
            if sm_survey_result_ec != ExpectedShellResult or std_out == '' or std_out is None:
                raise FailedException('Failed to collect MQTT messages')
        with step('Data extraction'):
            # Access collected MQTT messages
            with open('/tmp/mqtt_messages.json', 'r') as mqtt_file:
                sm_mqtt_messages = json.load(mqtt_file)
            # Extract required data from MQTT messages
            extracted_data = extract_mqtt_data_as_dict(sm_mqtt_messages, ['channel', 'connected', 'macAddress'], simplify=True)
            print_allure(f'The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}')
        with step('testcase'):
            # Compare extracted data to expected data
            expected_data = {
                'channel': channel,
                'connected': True,
                'macAddress': leaf_mac_res[1],
            }
            data_comparison = check_if_dicts_match(expected_data, extracted_data)
            if data_comparison is True:
                print_allure(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \nmatches the expected data: \n{output_to_json(expected_data, convert_only=True)}')
            else:
                raise FailedException(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \n does not match the expected data \n{output_to_json(expected_data, convert_only=True)} \nfor the following keys: {data_comparison}')
    finally:
        with step('Cleanup'):
            assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
            assert ref_handler.run('tools/device/vif_reset', disable_fut_exception=True) == ExpectedShellResult


########################################################################################################################
test_sm_neighbor_report_inputs = sm_config.get("sm_neighbor_report", [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.require_ref()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_sm_neighbor_report_inputs)
@pytest.mark.dependency(depends=["sm_fut_setup_dut", "sm_fut_setup_ref"], scope='session')
def test_sm_neighbor_report(test_config):
    server_handler, dut_handler, ref_handler = pytest.server_handler, pytest.dut_handler, pytest.ref_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        dut_radio_band = test_config.get('radio_band')
        ref_radio_band = ref_handler.get_radio_band_from_channel_and_band(channel, dut_radio_band)

        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, dut_radio_band)
            assert ref_handler.validate_channel_ht_mode_band(channel, ht_mode, ref_radio_band)

        mqtt_timeout = test_config.get("mqtt_timeout")
        mqtt_topic = test_config.get("mqtt_topic")
        sm_channel = test_config.get('sm_channel')
        sm_radio_type = test_config.get('sm_radio_type')
        sm_report_type = test_config.get('sm_report_type')
        sm_reporting_count = test_config.get('sm_reporting_count')
        sm_reporting_interval = test_config.get('sm_reporting_interval')
        sm_sampling_interval = test_config.get('sm_sampling_interval')
        sm_survey_type = test_config.get('sm_survey_type')
        survey_stats_type = test_config.get("survey_stats_type")
        neighbors_stats_type = test_config.get("neighbors_stats_type")

        # Constant arguments
        interface_type = 'home_ap'
        # Derived arguments
        dut_ssid = f"FUT_dut_ssid_{server_handler.get_ssid_unique_postfix()}"
        ref_ssid = f"FUT_ngh_ssid_{server_handler.get_ssid_unique_postfix()}"
        # Arguments from device capabilities
        ref_home_ap_if_name = ref_handler.capabilities.get_or_raise(f'interfaces.{interface_type}.{ref_radio_band}')
        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_max_message_count = 1
        location_id = "1000"
        node_id = "100"

        sm_dut_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        sm_server_mqtt_args = get_command_arguments(
            f'--hostname {mqtt_hostname}',
            f'--port {mqtt_port}',
            f'--topic {mqtt_topic}',
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f'--max_message_count {mqtt_max_message_count}',
            f'--timeout {mqtt_timeout}',
            f'--collect_messages {True}',
            f'--stdout_output {True}',
            f'--json_output {True}',
        )

        survey_wifi_stats_config_args = get_command_arguments(
            'Wifi_Stats_Config',
            '-i', 'channel_list', f'{sm_channel}',
            '-i', 'radio_type', f'{sm_radio_type}',
            '-i', 'report_type', f'{sm_report_type}',
            '-i', 'reporting_count', f'{sm_reporting_count}',
            '-i', 'reporting_interval', f'{sm_reporting_interval}',
            '-i', 'sampling_interval', f'{sm_sampling_interval}',
            '-i', 'stats_type', f'{survey_stats_type}',
            '-i', 'survey_type', f'{sm_survey_type}',
        )

        neighbor_wifi_stats_config_args = get_command_arguments(
            'Wifi_Stats_Config',
            '-i', 'channel_list', f'{sm_channel}',
            '-i', 'radio_type', f'{sm_radio_type}',
            '-i', 'report_type', f'{sm_report_type}',
            '-i', 'reporting_count', f'{sm_reporting_count}',
            '-i', 'reporting_interval', f'{sm_reporting_interval}',
            '-i', 'sampling_interval', f'{sm_sampling_interval}',
            '-i', 'stats_type', f'{neighbors_stats_type}',
            '-i', 'survey_type', f'{sm_survey_type}',
        )

    with step('Statistics collection preparation'):
        # Remove any previous entries from the Wifi_Stats_Config table
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
    with step('Configure GW Home AP interface'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=dut_radio_band,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=dut_ssid,
            device_name='dut',
        )
    with step('Configure NEIGHBOR Home AP interface'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=dut_radio_band,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ref_ssid,
            device_name='ref',
        )
    with step('Determine REF MAC remotely at runtime'):
        vif_mac_args = get_command_arguments(f'if_name=={ref_home_ap_if_name}')
        rc, neighbor_mac_str, std_err = ref_handler.run_raw('tools/device/ovsdb/get_vif_mac_from_ovsdb', vif_mac_args, print_out=True)
        assert neighbor_mac_str is not None and neighbor_mac_str != '' and rc == ExpectedShellResult
    with step('MQTT connection establishment and message collection'):
        assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/fut_configure_mqtt', sm_dut_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', survey_wifi_stats_config_args, do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', neighbor_wifi_stats_config_args, do_mqtt_log=True) == ExpectedShellResult
        sm_survey_result_ec, std_out, std_err = server_handler.run_raw('tools/fut_mqtt_tool', sm_server_mqtt_args, folder='framework', ext='.py')
        if sm_survey_result_ec != ExpectedShellResult or std_out == '' or std_out is None:
            raise FailedException('Failed to collect MQTT messages')
    with step('Data extraction'):
        # Access collected MQTT messages
        with open('/tmp/mqtt_messages.json', 'r') as mqtt_file:
            sm_mqtt_messages = json.load(mqtt_file)
        # Extract required data from MQTT messages
        extracted_data = extract_mqtt_data_as_dict(sm_mqtt_messages, ['channel', 'ssid', 'bssid'], simplify=True)
        print_allure(f'The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}')
    with step('Testcase'):
        # Compare extracted data to expected data
        expected_data = {
            'channel': channel,
            'ssid': ref_ssid,
            'bssid': neighbor_mac_str,
        }
        data_comparison = check_if_dicts_match(expected_data, extracted_data)
        if data_comparison is True:
            print_allure(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \nmatches the expected data: \n{output_to_json(expected_data, convert_only=True)}')
        else:
            raise FailedException(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \n does not match the expected data \n{output_to_json(expected_data, convert_only=True)} \nfor the following keys: {data_comparison}')
    with step('Cleanup'):
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult


########################################################################################################################
test_sm_survey_report_inputs = sm_config.get("sm_survey_report", [])
test_sm_survey_report_scenarios = []
for g in test_sm_survey_report_inputs.copy():
    if 'sm_channels' in g:
        for ch in g.pop('sm_channels'):
            d = g.copy()
            d['sm_channel'] = ch
            test_sm_survey_report_scenarios.append(d)
    else:
        test_sm_survey_report_scenarios.append(g)


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_sm_survey_report_scenarios)
@pytest.mark.dependency(depends=["sm_fut_setup_dut"], scope='session')
def test_sm_survey_report(test_config):
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler

    with step('Preparation'):
        # Test arguments from testcase config
        channel = test_config.get('channel')
        ht_mode = test_config.get('ht_mode')
        radio_band = test_config.get('radio_band')
        encryption = test_config.get("encryption", "WPA2")
        wifi_security_type = test_config.get("wifi_security_type", "wpa")
        with step('Validate radio parameters'):
            assert dut_handler.validate_channel_ht_mode_band(channel, ht_mode, radio_band)

        mqtt_timeout = test_config.get("mqtt_timeout")
        mqtt_topic = test_config.get("mqtt_topic")
        sm_channel = test_config.get('sm_channel')
        sm_radio_type = test_config.get('sm_radio_type')
        sm_report_type = test_config.get('sm_report_type')
        sm_reporting_count = test_config.get('sm_reporting_count')
        sm_reporting_interval = test_config.get('sm_reporting_interval')
        sm_sampling_interval = test_config.get('sm_sampling_interval')
        sm_survey_type = test_config.get('sm_survey_type')
        stats_type = test_config.get("stats_type")

        # Derived arguments
        ssid = f"FUT_ssid_{server_handler.get_ssid_unique_postfix()}"

        # Arguments from device capabilities
        phy_radio_name = dut_handler.capabilities.get_or_raise(f'interfaces.phy_radio_name.{radio_band}')
        device_region = dut_handler.get_region()

        # MQTT configuration
        mqtt_hostname = server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.hostname')
        mqtt_port = int(server_handler.testbed_cfg.get_or_raise('server.mqtt_settings.port'))
        mqtt_max_message_count = 1
        location_id = "1000"
        node_id = "100"

        sm_dut_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        sm_server_mqtt_args = get_command_arguments(
            f'--hostname {mqtt_hostname}',
            f'--port {mqtt_port}',
            f'--topic {mqtt_topic}',
            "--ca_cert '/etc/mosquitto/certs/fut/ca.pem'",
            f'--max_message_count {mqtt_max_message_count}',
            f'--timeout {mqtt_timeout}',
            f'--collect_messages {True}',
            f'--stdout_output {True}',
            f'--json_output {True}',
        )

        wifi_stats_config_args_base = [
            'Wifi_Stats_Config',
            '-i', 'channel_list', f'{sm_channel}',
            '-i', 'radio_type', f'{sm_radio_type}',
            '-i', 'report_type', f'{sm_report_type}',
            '-i', 'reporting_count', f'{sm_reporting_count}',
            '-i', 'reporting_interval', f'{sm_reporting_interval}',
            '-i', 'sampling_interval', f'{sm_sampling_interval}',
            '-i', 'stats_type', f'{stats_type}',
            '-i', 'survey_type', f'{sm_survey_type}',
        ]

    if sm_survey_type == 'off-chan':
        with step('Validate testcase configurations for off-chan survey'):
            # Checking if device is on non-DFS channel while performing off-channel scan
            check_config = check_off_chan_scan_on_non_dfs_channel(channel, ht_mode, radio_band, device_region.upper())
            if not check_config:
                pytest.skip(f"Invalid configuration: off-chan survey is not allowed on DFS channel for '{device_region}' reg domain")

        """
        Because dwell time must be less than the beacon interval on off-channel scanning, the
        survey interval is set to 10% of beacon interval
        """
        beacon_interval_args = get_command_arguments(
            'Wifi_Radio_State', 'bcn_int', '-w', 'if_name', phy_radio_name,
        )
        beacon_interval_ec, beacon_interval, std_err = dut_handler.run_raw('tools/device/ovsdb/get_ovsdb_entry_value', beacon_interval_args, print_out=True)
        assert beacon_interval is not None and beacon_interval != '' and beacon_interval_ec == ExpectedShellResult
        sm_survey_interval = round(int(beacon_interval) * 0.1)
        wifi_stats_config_args_base += [
            '-i', 'survey_interval_ms', f'{sm_survey_interval}',
        ]

    with step('VIF clean'):
        assert dut_handler.run('tools/device/vif_reset') == ExpectedShellResult
    with step('Statistics collection preparation'):
        # Remove any previous entries from the Wifi_Stats_Config table
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
    with step('Home AP creation'):
        assert configure_ap_interface(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            wifi_security_type=wifi_security_type,
            encryption=encryption,
            ssid=ssid,
            device_name='dut',
        )
    with step('MQTT connection establishment and message collection'):
        wifi_stats_config_args = get_command_arguments(*wifi_stats_config_args_base)
        assert server_handler.run('tools/server/start_mqtt', '--restart', do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/fut_configure_mqtt', sm_dut_mqtt_cfg_args, do_mqtt_log=True) == ExpectedShellResult
        assert dut_handler.run('tools/device/ovsdb/insert_ovsdb_entry', wifi_stats_config_args, do_mqtt_log=True) == ExpectedShellResult
        sm_survey_result_ec, std_out, std_err = server_handler.run_raw('tools/fut_mqtt_tool', sm_server_mqtt_args, folder='framework', ext='.py')
        if sm_survey_result_ec != ExpectedShellResult or std_out == '' or std_out is None:
            raise FailedException('Failed to collect MQTT messages')
    with step('Data extraction'):
        # Access collected MQTT messages
        with open('/tmp/mqtt_messages.json', 'r') as mqtt_file:
            sm_mqtt_messages = json.load(mqtt_file)
        # Extract required data from MQTT messages
        extracted_data = extract_mqtt_data_as_dict(sm_mqtt_messages, ['channel'], simplify=True)
        print_allure(f'The following data was extracted: \n{output_to_json(extracted_data, convert_only=True)}')
    with step('Testcase'):
        # Compare extracted data to expected data
        expected_data = {
            'channel': sm_channel,
        }
        data_comparison = check_if_dicts_match(expected_data, extracted_data)
        if data_comparison is True:
            print_allure(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \nmatches the expected data: \n{output_to_json(expected_data, convert_only=True)}')
        else:
            raise FailedException(f'The gathered data: \n{output_to_json(extracted_data, convert_only=True)} \n does not match the expected data \n{output_to_json(expected_data, convert_only=True)} \nfor the following keys: {data_comparison}')
    with step('Cleanup'):
        assert dut_handler.run('tests/sm/sm_cleanup') == ExpectedShellResult
