import allure
import pytest

from config.defaults import sm_radio_types
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
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "SM" not in node_handler.get_kconfig_managers():
            pytest.skip("SM not present on device")
        wireless_manager_name = node_handler.get_wireless_manager_name()
        phy_radio_ifnames = node_handler.capabilities.get_phy_radio_ifnames(return_type=list)
        setup_args = node_handler.get_command_arguments(wireless_manager_name, *phy_radio_ifnames)
        node_handler.fut_device_setup(test_suite_name="sm", setup_args=setup_args)
        service_status = node_handler.get_node_services_and_status()
        if service_status["sm"]["status"] != "enabled":
            pytest.skip("SM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestSm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_dynamic_noise_floor", []))
    def test_sm_dynamic_noise_floor(self, cfg: dict, update_baseline_os_pids):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            mqtt_topic = cfg.get("mqtt_topic")
            sm_radio_type = sm_radio_types.get(radio_band)
            sm_report_type = cfg.get("sm_report_type")
            sm_reporting_count = cfg.get("sm_reporting_count")
            sm_reporting_interval = cfg.get("sm_reporting_interval")
            sm_sampling_interval = cfg.get("sm_sampling_interval")
            sm_survey_type = cfg.get("sm_survey_type")
            stats_type = cfg.get("stats_type")
            noise_range_dbm = cfg.get("noise_range_dbm")

            # Constant arguments
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            wifi_stats_config_args = {
                "radio_type": sm_radio_type,
                "report_type": sm_report_type,
                "reporting_count": sm_reporting_count,
                "reporting_interval": sm_reporting_interval,
                "sampling_interval": sm_sampling_interval,
                "stats_type": stats_type,
                "survey_type": sm_survey_type,
            }

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
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
                gw.interfaces["home_ap"].vif_reset()
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_leaf_report", []))
    def test_sm_leaf_report(self, cfg: dict, update_baseline_os_pids):
        server, gw, l1 = pytest.server, pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            encryption = cfg["encryption"]
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            device_mode = cfg.get("device_mode", "router")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_radio_type = sm_radio_types.get(gw_radio_band)
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

            wifi_stats_config_args = {
                "radio_type": sm_radio_type,
                "report_type": sm_report_type,
                "reporting_count": sm_reporting_count,
                "reporting_interval": sm_reporting_interval,
                "sampling_interval": sm_sampling_interval,
                "stats_type": stats_type,
                "survey_type": sm_survey_type,
            }

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step(f"Put GW into {device_mode} mode"):
                assert gw.configure_device_mode(device_mode=device_mode)
            with step("Backhaul configuration"):
                assert gw.create_and_configure_backhaul(
                    channel=channel,
                    leaf_device=l1,
                    radio_band=gw_radio_band,
                    ht_mode=ht_mode,
                    encryption=encryption,
                    mesh_type=None,
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
                gw.interfaces["backhaul_ap"].vif_reset()
                l1.interfaces["backhaul_sta"].vif_reset()
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_neighbor_report", []))
    def test_sm_neighbor_report(self, cfg: dict, update_baseline_os_pids):
        fut_configurator, server, gw, l1 = pytest.fut_configurator, pytest.server, pytest.gw, pytest.l1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            encryption = cfg["encryption"]
            ht_mode = cfg.get("ht_mode")
            gw_radio_band = cfg.get("radio_band")
            mqtt_topic = cfg.get("mqtt_topic")
            sm_channel = cfg.get("sm_channel")
            sm_radio_type = sm_radio_types.get(gw_radio_band)
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

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=gw_radio_band,
                encryption=encryption,
                interface_role="home_ap",
                ssid=gw_ssid,
                wpa_psks=psk,
            )

            # L1 interface creation
            l1.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=l1_radio_band,
                encryption=encryption,
                interface_role="home_ap",
                ssid=l1_ssid,
                wpa_psks=psk,
            )

            survey_wifi_stats_config_args = {
                "channel_list": sm_channel,
                "radio_type": sm_radio_type,
                "report_type": sm_report_type,
                "reporting_count": sm_reporting_count,
                "reporting_interval": sm_reporting_interval,
                "sampling_interval": sm_sampling_interval,
                "stats_type": survey_stats_type,
                "survey_type": sm_survey_type,
            }

            neighbor_wifi_stats_config_args = {
                "channel_list": sm_channel,
                "radio_type": sm_radio_type,
                "report_type": sm_report_type,
                "reporting_count": sm_reporting_count,
                "reporting_interval": sm_reporting_interval,
                "sampling_interval": sm_sampling_interval,
                "stats_type": neighbors_stats_type,
                "survey_type": sm_survey_type,
            }

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.ovsdb.set_value(table="Wifi_Stats_Config", value=survey_wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )
                assert (
                    gw.ovsdb.set_value(table="Wifi_Stats_Config", value=neighbor_wifi_stats_config_args)[0]
                    == ExpectedShellResult
                )

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("L1 AP creation"):
                assert l1.interfaces["home_ap"].configure_interface() == ExpectedShellResult
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
                gw.interfaces["home_ap"].vif_reset()
                l1.interfaces["home_ap"].vif_reset()
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", nm2_config.get("sm_survey_report", []))
    def test_sm_survey_report(self, cfg: dict, update_baseline_os_pids):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            mqtt_topic = cfg.get("mqtt_topic")
            sm_channel = cfg.get("sm_channel")
            sm_radio_type = sm_radio_types.get(radio_band)
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
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"

            # GW interface creation
            gw.create_interface_object(
                channel=channel,
                ht_mode=ht_mode,
                radio_band=radio_band,
                encryption=encryption,
                interface_role="home_ap",
            )

            sm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                mqtt_topic,
            )

            wifi_stats_config_args = {
                "channel_list": sm_channel,
                "radio_type": sm_radio_type,
                "report_type": sm_report_type,
                "reporting_count": sm_reporting_count,
                "reporting_interval": sm_reporting_interval,
                "sampling_interval": sm_sampling_interval,
                "stats_type": stats_type,
                "survey_type": sm_survey_type,
            }

            if sm_survey_type == "off-chan" and device_region == "US" and "5g" in radio_band:
                with step("Validate testcase configurations for off-chan survey"):
                    # Checking if the device is on a non-DFS channel while performing off-channel scan
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
                beacon_interval = gw.ovsdb.get_int(
                    table="Wifi_Radio_State",
                    select="bcn_int",
                    where=f"if_name=={gw_phy_radio_name}",
                )
                assert beacon_interval is not None and beacon_interval != ""
                survey_interval = round(int(beacon_interval) * 0.1)

                return survey_interval

        try:
            with step("Statistics collection preparation"):
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
            with step("GW AP creation"):
                assert gw.interfaces["home_ap"].configure_interface() == ExpectedShellResult
            with step("Validate and set beacon interval"):
                sm_survey_interval = _validate_and_set_bcn_int()
                wifi_stats_config_args["survey_interval_ms"] = sm_survey_interval
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):

                def _trigger():
                    assert gw.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                    assert (
                        gw.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0]
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
                gw.interfaces["home_ap"].vif_reset()
                assert gw.execute_with_logging("tests/sm/sm_cleanup")[0] == ExpectedShellResult
