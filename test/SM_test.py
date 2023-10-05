import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
nm2_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def sm_setup():
    test_class_name = ["TestSm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for SM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
            setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
            device_handler.fut_device_setup(test_suite_name="sm", setup_args=setup_args)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestSm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_dynamic_noise_floor", []))
    def test_sm_dynamic_noise_floor(self, cfg):
        fut_configurator, server, gw = pytest.fut_configurator, pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_radio_type = cfg.get("sm_radio_type")
            sm_report_type = cfg.get("sm_report_type")
            sm_reporting_count = cfg.get("sm_reporting_count")
            sm_reporting_interval = cfg.get("sm_reporting_interval")
            sm_sampling_interval = cfg.get("sm_sampling_interval")
            sm_survey_type = cfg.get("sm_survey_type")
            stats_type = cfg.get("stats_type")
            noise_range_dbm = cfg.get("noise_range_dbm")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            wifi_stats_config_args = gw.get_command_arguments(
                "Wifi_Stats_Config",
                "-i",
                "radio_type",
                f"{sm_radio_type}",
                "-i",
                "report_type",
                f"{sm_report_type}",
                "-i",
                "reporting_count",
                f"{sm_reporting_count}",
                "-i",
                "reporting_interval",
                f"{sm_reporting_interval}",
                "-i",
                "sampling_interval",
                f"{sm_sampling_interval}",
                "-i",
                "stats_type",
                f"{stats_type}",
                "-i",
                "survey_type",
                f"{sm_survey_type}",
            )

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.execute("tools/device/ovsdb/insert_ovsdb_entry", wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):
                assert server.mqtt_trigger_and_validate_message(
                    topic=mqtt_topic,
                    trigger=_trigger,
                    expected_data={
                        "noiseFloor": noise_range_dbm,
                    },
                    comparison_method="in_range",
                )
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_leaf_report", []))
    def test_sm_leaf_report(self, cfg):
        server, gw, l1 = pytest.server, pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            encryption = cfg.get("encryption", "WPA2")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            device_mode = cfg.get("device_mode", "router")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_radio_type = cfg.get("sm_radio_type")
            sm_report_type = cfg.get("sm_report_type")
            sm_reporting_count = cfg.get("sm_reporting_count")
            sm_reporting_interval = cfg.get("sm_reporting_interval")
            sm_sampling_interval = cfg.get("sm_sampling_interval")
            sm_survey_type = cfg.get("sm_survey_type")
            stats_type = cfg.get("stats_type")

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_bhaul_sta_if_name = l1.device_api.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
            l1_mac = "".join(l1.device_api.iface.get_vif_mac(l1_bhaul_sta_if_name))
            # Constant arguments
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            wifi_stats_config_args = gw.get_command_arguments(
                "Wifi_Stats_Config",
                "-i",
                "radio_type",
                f"{sm_radio_type}",
                "-i",
                "report_type",
                f"{sm_report_type}",
                "-i",
                "reporting_count",
                f"{sm_reporting_count}",
                "-i",
                "reporting_interval",
                f"{sm_reporting_interval}",
                "-i",
                "sampling_interval",
                f"{sm_sampling_interval}",
                "-i",
                "stats_type",
                f"{stats_type}",
                "-i",
                "survey_type",
                f"{sm_survey_type}",
            )

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.execute("tools/device/ovsdb/insert_ovsdb_entry", wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("VIF clean"):
                assert gw.execute("tools/device/vif_reset")[0] == ExpectedShellResult
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("GW AP and L1 STA creation"):
                assert gw.create_and_configure_bhaul_connection_gw_leaf(
                    channel=channel,
                    leaf_device=l1,
                    gw_radio_band=gw_radio_band,
                    leaf_radio_band=l1_radio_band,
                    ht_mode=ht_mode,
                    wifi_security_type=wifi_security_type,
                    encryption=encryption,
                    skip_gre=True,
                )
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):
                assert server.mqtt_trigger_and_validate_message(
                    topic=mqtt_topic,
                    trigger=_trigger,
                    expected_data={
                        "channel": channel,
                        "connected": True,
                        "macAddress": l1_mac,
                    },
                )
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
                assert l1.execute_with_logging("tools/device/vif_reset")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_neighbor_report", []))
    def test_sm_neighbor_report(self, cfg):
        fut_configurator, server, gw, l1 = pytest.fut_configurator, pytest.server, pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            encryption = cfg.get("encryption", "WPA2")
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_channel = cfg.get("sm_channel")
            sm_radio_type = cfg.get("sm_radio_type")
            sm_report_type = cfg.get("sm_report_type")
            sm_reporting_count = cfg.get("sm_reporting_count")
            sm_reporting_interval = cfg.get("sm_reporting_interval")
            sm_sampling_interval = cfg.get("sm_sampling_interval")
            sm_survey_type = cfg.get("sm_survey_type")
            survey_stats_type = cfg.get("survey_stats_type")
            neighbors_stats_type = cfg.get("neighbors_stats_type")

            # L1 specific arguments
            l1_radio_band = l1.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
            l1_home_ap_if_name = l1.device_api.capabilities.get_home_ap_ifname(freq_band=l1_radio_band)

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            gw_ssid, l1_ssid = f"gw_{ssid}", f"l1_{ssid}"
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": gw_radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": gw_ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            # L1 AP arguments
            l1_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": l1_radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": l1_ssid,
                "reset_vif": True,
            }

            l1.ap_args = l1_ap_vif_args

            survey_wifi_stats_config_args = gw.get_command_arguments(
                "Wifi_Stats_Config",
                "-i",
                "channel_list",
                f"{sm_channel}",
                "-i",
                "radio_type",
                f"{sm_radio_type}",
                "-i",
                "report_type",
                f"{sm_report_type}",
                "-i",
                "reporting_count",
                f"{sm_reporting_count}",
                "-i",
                "reporting_interval",
                f"{sm_reporting_interval}",
                "-i",
                "sampling_interval",
                f"{sm_sampling_interval}",
                "-i",
                "stats_type",
                f"{survey_stats_type}",
                "-i",
                "survey_type",
                f"{sm_survey_type}",
            )

            neighbor_wifi_stats_config_args = gw.get_command_arguments(
                "Wifi_Stats_Config",
                "-i",
                "channel_list",
                f"{sm_channel}",
                "-i",
                "radio_type",
                f"{sm_radio_type}",
                "-i",
                "report_type",
                f"{sm_report_type}",
                "-i",
                "reporting_count",
                f"{sm_reporting_count}",
                "-i",
                "reporting_interval",
                f"{sm_reporting_interval}",
                "-i",
                "sampling_interval",
                f"{sm_sampling_interval}",
                "-i",
                "stats_type",
                f"{neighbors_stats_type}",
                "-i",
                "survey_type",
                f"{sm_survey_type}",
            )

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.execute("tools/device/ovsdb/insert_ovsdb_entry", survey_wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.execute("tools/device/ovsdb/insert_ovsdb_entry", neighbor_wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("L1 AP creation"):
                assert l1.configure_radio_vif_and_network()
            with step("Acquire L1 AP MAC"):
                l1_mac = "".join(l1.device_api.iface.get_vif_mac(l1_home_ap_if_name))
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):
                assert server.mqtt_trigger_and_validate_message(
                    topic=mqtt_topic,
                    trigger=_trigger,
                    expected_data={
                        "channel": channel,
                        "ssid": l1_ssid,
                        "bssid": l1_mac,
                    },
                )
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_survey_report", []))
    def test_sm_survey_report(self, cfg):
        fut_configurator, server, gw = pytest.fut_configurator, pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg.get("encryption", "WPA2")
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_channel = cfg.get("sm_channel")
            sm_radio_type = cfg.get("sm_radio_type")
            sm_report_type = cfg.get("sm_report_type")
            sm_reporting_count = cfg.get("sm_reporting_count")
            sm_reporting_interval = cfg.get("sm_reporting_interval")
            sm_sampling_interval = cfg.get("sm_sampling_interval")
            sm_survey_type = cfg.get("sm_survey_type")
            stats_type = cfg.get("stats_type")

            # GW specific arguments
            gw_phy_radio_name = gw.capabilities.get_phy_radio_ifname(freq_band=radio_band)
            device_region = gw.capabilities.get_regulatory_domain()

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "reset_vif": True,
            }

            gw.ap_args = gw_ap_vif_args

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            wifi_stats_config_args_base = [
                "Wifi_Stats_Config",
                "-i",
                "channel_list",
                f"{sm_channel}",
                "-i",
                "radio_type",
                f"{sm_radio_type}",
                "-i",
                "report_type",
                f"{sm_report_type}",
                "-i",
                "reporting_count",
                f"{sm_reporting_count}",
                "-i",
                "reporting_interval",
                f"{sm_reporting_interval}",
                "-i",
                "sampling_interval",
                f"{sm_sampling_interval}",
                "-i",
                "stats_type",
                f"{stats_type}",
                "-i",
                "survey_type",
                f"{sm_survey_type}",
            ]

            if sm_survey_type == "off-chan" and device_region == "US" and "5g" in radio_band:
                with step("Validate testcase configurations for off-chan survey"):
                    # Checking if device is on non-DFS channel while performing off-channel scan
                    dfs_channels = gw.device_api.iface.get_dfs_channels(radio_band.upper())
                    if channel in dfs_channels:
                        pytest.skip(
                            f"Invalid configuration: off-chan survey is not allowed on DFS channel for '{device_region}' reg domain.",
                        )

            """
            Because dwell time must be less than the beacon interval on off-channel scanning, the
            survey interval is set to 10% of beacon interval
            """

            def _validate_and_set_bcn_int():
                beacon_interval_args = gw.get_command_arguments(
                    "Wifi_Radio_State",
                    "bcn_int",
                    "-w",
                    "if_name",
                    gw_phy_radio_name,
                )
                beacon_interval_ec, beacon_interval, std_err = gw.execute(
                    "tools/device/ovsdb/get_ovsdb_entry_value",
                    beacon_interval_args,
                )
                assert (
                    beacon_interval is not None and beacon_interval != "" and beacon_interval_ec == ExpectedShellResult
                )
                survey_interval = round(int(beacon_interval) * 0.1)

                return survey_interval

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.configure_radio_vif_and_network()
            with step("Validate and set beacon interval"):
                sm_survey_interval = _validate_and_set_bcn_int()
                wifi_stats_config_args_base += [
                    "-i",
                    "survey_interval_ms",
                    f"{sm_survey_interval}",
                ]
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):

                def _trigger():
                    wifi_stats_config_args = gw.get_command_arguments(*wifi_stats_config_args_base)
                    assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                    assert (
                        gw.execute("tools/device/ovsdb/insert_ovsdb_entry", wifi_stats_config_args)[0]
                        == ExpectedShellResult
                    )

                assert server.mqtt_trigger_and_validate_message(
                    topic=mqtt_topic,
                    trigger=_trigger,
                    expected_data={
                        "channel": sm_channel,
                    },
                )
        finally:
            with step("Cleanup"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
