import pytest

from config.defaults import sm_radio_types
from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.common import compare_fw_versions


@pytest.fixture(scope="module")
def sm_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = module_name.lower()
            if manager_name.upper() not in gw_handler.kconfig_managers:
                pytest.skip(f"{manager_name.upper()} not present on device")

            if gw_handler.node_service_status[manager_name]["status"] != "enabled":
                pytest.skip(f"{manager_name.upper()} not enabled on device")

        if "l1_handler" in fixturenames:
            l1_handler = request.getfixturevalue("l1_handler")
            handlers.append(l1_handler)

        if "l2_handler" in fixturenames:
            l2_handler = request.getfixturevalue("l2_handler")
            handlers.append(l2_handler)

        reboot_pods_and_wait_available(handlers)

        if "gw_handler" in fixturenames:
            gw_handler.device_test_setup(test_suite_name=manager_name)
    yield


def test_sm_dynamic_noise_floor(sm_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        mqtt_topic = parametrized_test_config.get("mqtt_topic")
        sm_radio_type = sm_radio_types.get(radio_band)
        sm_report_type = parametrized_test_config.get("sm_report_type")
        sm_reporting_count = parametrized_test_config.get("sm_reporting_count")
        sm_reporting_interval = parametrized_test_config.get("sm_reporting_interval")
        sm_sampling_interval = parametrized_test_config.get("sm_sampling_interval")
        sm_survey_type = parametrized_test_config.get("sm_survey_type")
        stats_type = parametrized_test_config.get("stats_type")
        noise_range_dbm = parametrized_test_config.get("noise_range_dbm")

        # Constant arguments
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        sm_gw_mqtt_cfg_args = get_command_arguments(
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
            assert gw_handler.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == 0
            assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0] == 0

    try:
        with step("Statistics collection preparation"):
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Restart MQTT broker on server"):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        with step("Test case"):
            assert server_handler.mqtt_trigger_and_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={
                    "noiseFloor": noise_range_dbm,
                },
                comparison_method="in_range",
            )
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0


def test_sm_leaf_report(sm_setup, parametrized_test_config, server_handler, gw_handler, l1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        encryption = parametrized_test_config["encryption"]
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        device_mode = parametrized_test_config.get("device_mode", "router")
        mqtt_topic = parametrized_test_config.get("mqtt_topic")
        sm_radio_type = sm_radio_types.get(gw_radio_band)
        sm_report_type = parametrized_test_config.get("sm_report_type")
        sm_reporting_count = parametrized_test_config.get("sm_reporting_count")
        sm_reporting_interval = parametrized_test_config.get("sm_reporting_interval")
        sm_sampling_interval = parametrized_test_config.get("sm_sampling_interval")
        sm_survey_type = parametrized_test_config.get("sm_survey_type")
        stats_type = parametrized_test_config.get("stats_type")

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_bhaul_sta_if_name = l1_handler.capabilities.get_bhaul_sta_ifname(freq_band=l1_radio_band)
        mac_list = l1_handler.iface.get_vif_mac(l1_bhaul_sta_if_name)
        assert mac_list, f"Can not get {l1_bhaul_sta_if_name} MAC on {l1_handler.nickname.upper()}"
        l1_mac = mac_list[0]

        # Constant arguments
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"

        sm_gw_mqtt_cfg_args = get_command_arguments(
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
            assert gw_handler.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == 0
            assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0] == 0

    try:
        with step("Statistics collection preparation"):
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
        with step(f"Put GW into {device_mode} mode"):
            gw_handler.configure_device_mode(device_mode=device_mode)
        with step("Backhaul configuration"):
            assert gw_handler.create_and_configure_backhaul(
                channel=channel,
                leaf_device=l1_handler,
                radio_band=gw_radio_band,
                ht_mode=ht_mode,
                encryption=encryption,
                mesh_type=None,
            )
        with step("Restart MQTT broker on server"):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        with step("Test case"):
            assert server_handler.mqtt_trigger_and_validate_message(
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
            gw_handler.interface["backhaul_ap"].vif_reset()
            l1_handler.interface["backhaul_sta"].vif_reset()
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0


def test_sm_neighbor_report(sm_setup, parametrized_test_config, server_handler, gw_handler, l1_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        encryption = parametrized_test_config["encryption"]
        ht_mode = parametrized_test_config.get("ht_mode")
        gw_radio_band = parametrized_test_config.get("radio_band")
        mqtt_topic = parametrized_test_config.get("mqtt_topic")
        sm_channel = parametrized_test_config.get("sm_channel")
        sm_radio_type = sm_radio_types.get(gw_radio_band)
        sm_report_type = parametrized_test_config.get("sm_report_type")
        sm_reporting_count = parametrized_test_config.get("sm_reporting_count")
        sm_reporting_interval = parametrized_test_config.get("sm_reporting_interval")
        sm_sampling_interval = parametrized_test_config.get("sm_sampling_interval")
        sm_survey_type = parametrized_test_config.get("sm_survey_type")
        survey_stats_type = parametrized_test_config.get("survey_stats_type")
        neighbors_stats_type = parametrized_test_config.get("neighbors_stats_type")

        # L1 specific arguments
        l1_radio_band = l1_handler.get_radio_band_from_remote_channel_and_band(channel, gw_radio_band)
        l1_home_ap_if_name = l1_handler.capabilities.get_home_ap_ifname(freq_band=l1_radio_band)

        # Constant arguments
        ssid, psk = gw_handler.base_ssid, gw_handler.base_psk
        gw_ssid, l1_ssid = f"gw_{ssid}", f"l1_{ssid}"
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"

        sm_gw_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
        )

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=gw_radio_band,
            encryption=encryption,
            interface_role="home_ap",
            ssid=gw_ssid,
            wpa_psks=psk,
        )

        # L1 interface creation
        l1_handler.create_interface_object(
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
            assert gw_handler.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == 0
            assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=survey_wifi_stats_config_args)[0] == 0
            assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=neighbor_wifi_stats_config_args)[0] == 0

    try:
        with step("Statistics collection preparation"):
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("L1 AP creation"):
            assert l1_handler.interface["home_ap"].configure_interface() == 0
        with step("Acquire L1 AP MAC"):
            mac_list = l1_handler.iface.get_vif_mac(l1_home_ap_if_name)
            assert mac_list, f"Can not get {l1_home_ap_if_name} MAC on {l1_handler.nickname.upper()}"
            l1_mac = mac_list[0]
        with step("Restart MQTT broker on server"):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        with step("Test case"):
            assert server_handler.mqtt_trigger_and_validate_message(
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
            gw_handler.interface["home_ap"].vif_reset()
            l1_handler.interface["home_ap"].vif_reset()
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0


def test_sm_survey_report(sm_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        mqtt_topic = parametrized_test_config.get("mqtt_topic")
        sm_channel = parametrized_test_config.get("sm_channel")
        sm_radio_type = sm_radio_types.get(radio_band)
        sm_report_type = parametrized_test_config.get("sm_report_type")
        sm_reporting_count = parametrized_test_config.get("sm_reporting_count")
        sm_reporting_interval = parametrized_test_config.get("sm_reporting_interval")
        sm_sampling_interval = parametrized_test_config.get("sm_sampling_interval")
        sm_survey_type = parametrized_test_config.get("sm_survey_type")
        stats_type = parametrized_test_config.get("stats_type")

        # GW specific arguments
        gw_phy_radio_name = gw_handler.capabilities.get_phy_radio_ifname(freq_band=radio_band)
        device_region = gw_handler.capabilities.get_regulatory_domain()

        # Constant arguments
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        sm_gw_mqtt_cfg_args = get_command_arguments(
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
                dfs_channels = gw_handler.iface.get_dfs_channels(radio_band.upper())
                if channel in dfs_channels:
                    pytest.skip(
                        f"Invalid configuration: off-chan survey is not allowed on DFS channel for '{device_region}' reg domain.",
                    )

        """
        Because dwell time must be less than the beacon interval on off-channel scanning, the
        survey interval is set to 10% of beacon interval
        """

        def _validate_and_set_bcn_int():
            beacon_interval = gw_handler.ovsdb.get_int(
                table="Wifi_Radio_State",
                select="bcn_int",
                where=f"if_name=={gw_phy_radio_name}",
            )
            assert beacon_interval is not None and beacon_interval != ""
            survey_interval = round(int(beacon_interval) * 0.1)

            return survey_interval

    try:
        with step("Statistics collection preparation"):
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("Validate and set beacon interval"):
            sm_survey_interval = _validate_and_set_bcn_int()
            wifi_stats_config_args["survey_interval_ms"] = sm_survey_interval
        with step("Restart MQTT broker on server"):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        with step("Test case"):

            def _trigger():
                assert gw_handler.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == 0
                assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0] == 0

            assert server_handler.mqtt_trigger_and_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={
                    "channel": sm_channel,
                },
            )
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0


def test_sm_latency_report(sm_setup, parametrized_test_config, server_handler, gw_handler, w1_handler):
    min_opensync_version = "6.7.1.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Put GW into bridge_mode"):
        gw_handler.configure_device_mode(device_mode="bridge")
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        channel = parametrized_test_config.get("channel")
        ht_mode = parametrized_test_config.get("ht_mode")
        radio_band = parametrized_test_config.get("radio_band")
        encryption = parametrized_test_config["encryption"]
        mqtt_topic = parametrized_test_config.get("mqtt_topic")

        sm_reporting_count = parametrized_test_config.get("sm_reporting_count")
        sm_reporting_interval = parametrized_test_config.get("sm_reporting_interval")
        sm_sampling_interval = parametrized_test_config.get("sm_sampling_interval")
        sm_sampling_policy = parametrized_test_config.get("sample_policy")
        stats_type = parametrized_test_config.get("stats_type")
        latency_dscp = parametrized_test_config.get("latency_dscp")
        latency_kinds = parametrized_test_config.get("latency_kinds")

        # Constant arguments
        mqtt_hostname = server_handler.MQTT_HOSTNAME
        mqtt_port = server_handler.MQTT_PORT
        location_id = "1000"
        node_id = "100"

        # GW interface creation
        gw_handler.create_interface_object(
            channel=channel,
            ht_mode=ht_mode,
            radio_band=radio_band,
            encryption=encryption,
            interface_role="home_ap",
        )

        mqtt_topics_key = "Latency"
        sm_gw_mqtt_cfg_args = get_command_arguments(
            mqtt_hostname,
            mqtt_port,
            location_id,
            node_id,
            mqtt_topic,
            mqtt_topics_key,
        )

        if_name = []
        if_name.append(gw_handler.capabilities.get_primary_wan_iface())
        if_name.append(gw_handler.interface["home_ap"].network_if_name)

        wifi_stats_config_args = {
            "if_name": if_name,
            "latency_dscp": latency_dscp,
            "latency_kinds": latency_kinds,
            "reporting_count": sm_reporting_count,
            "reporting_interval": sm_reporting_interval,
            "sample_policy": sm_sampling_policy,
            "sampling_interval": sm_sampling_interval,
            "stats_type": stats_type,
        }

    try:
        with step("Statistics collection preparation"):
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
        with step("GW AP creation"):
            assert gw_handler.interface["home_ap"].configure_interface() == 0
        with step("W1 client connection"):
            ssid = gw_handler.interface["home_ap"].ssid_raw
            psk = gw_handler.interface["home_ap"].psk_raw
            w1_handler.connect(ssid=ssid, psk=psk, node=gw_handler)
        with step("Verify W1 client connection"):
            assert w1_handler.get_mac(if_name=w1_handler.wlan_ifname) in gw_handler.get_wifi_associated_clients()
        with step("Restart MQTT broker on server"):
            assert server_handler.execute("tools/server/start_mqtt", "--restart")[0] == 0
        with step("Test case"):

            def _trigger():
                assert gw_handler.execute("tools/device/fut_configure_mqtt", sm_gw_mqtt_cfg_args)[0] == 0
                assert gw_handler.ovsdb.set_value(table="Wifi_Stats_Config", value=wifi_stats_config_args)[0] == 0
                import time

                time.sleep(3)
                assert w1_handler.execute("tools/server/run_iperf3_server", as_sudo=True)[0] == 0
                w1_client_ip = w1_handler.get_client_ips(interface=w1_handler.wlan_ifname)["ipv4"]
                port = 5201
                check_traffic_args = get_command_arguments(
                    w1_client_ip,
                    port,
                )
                assert (
                    server_handler.execute("tools/server/check_traffic_to_client", check_traffic_args, as_sudo=True)[0]
                    == 0
                )

            assert server_handler.mqtt_trigger_and_validate_message(
                topic=mqtt_topic,
                trigger=_trigger,
                expected_data={"ifName": if_name},
                unique_data=True,
                inorder=False,
            )
    finally:
        with step("Cleanup"):
            gw_handler.interface["home_ap"].vif_reset()
            assert gw_handler.execute_with_logging("tests/sm/sm_cleanup")[0] == 0
            gw_handler.configure_device_mode(device_mode="router")
