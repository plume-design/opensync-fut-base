from pathlib import Path
from urllib.parse import urlparse

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
fsm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def fsm_setup():
    test_class_name = ["TestFsm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for FSM: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            if device_handler.device_type == "node":
                phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
                setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
                device_handler.fut_device_setup(test_suite_name="fsm", setup_args=setup_args)
            else:
                device_handler.fut_device_setup(test_suite_name="fsm")
        except Exception as exception:
            RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestFsm:
    @staticmethod
    def fsm_content_filtering_test_procedure(cfg, validation_parameters):
        fut_configurator, server, gw, w1 = pytest.fut_configurator, pytest.server, pytest.gw, pytest.w1

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            channel = cfg.get("channel")
            ht_mode = cfg.get("ht_mode")
            radio_band = cfg.get("radio_band")
            encryption = cfg["encryption"]
            wifi_security_type = cfg.get("wifi_security_type", "wpa")
            client_retry = cfg.get("client_retry", 3)
            test_client_cmd = cfg.get("test_client_cmd")

            # Constant arguments
            ssid, psk = fut_configurator.base_ssid, fut_configurator.base_psk
            mqtt_hostname = server.mqtt_hostname
            mqtt_port = server.mqtt_port
            location_id = "1000"
            node_id = "100"
            fsm_mqtt_topic = "fsm_test_topic"

            # Server arguments
            server_mac = server.device_api.get_mac(ifname="eth0")
            assert server_mac is not None and server_mac != ""

            # GW arguments
            lan_bridge_if_name = gw.capabilities.get_lan_bridge_ifname()
            tap_interface_args = gw.get_command_arguments(
                lan_bridge_if_name,
            )
            gw_ap_if_name = gw.capabilities.get_home_ap_ifname(radio_band)

            # W1 arguments
            w1_mac = w1.device_api.get_mac(ifname=w1.device_config.get("wlan_if_name"))
            assert w1_mac is not None and w1_mac != ""

            # GW AP arguments
            gw_ap_vif_args = {
                "channel": channel,
                "ht_mode": ht_mode,
                "radio_band": radio_band,
                "wpa_psk": psk,
                "wifi_security_type": wifi_security_type,
                "encryption": encryption,
                "ssid": ssid,
                "interface_type": "home_ap",
                "reset_vif": True,
            }
            gw.ap_args = gw_ap_vif_args

            openflow_rules_args = gw.get_command_arguments(
                lan_bridge_if_name,
            )

            configure_dpi_sni_plugin_args = gw.get_command_arguments(
                fsm_mqtt_topic,
            )

            fsm_gw_mqtt_cfg_args = gw.get_command_arguments(
                mqtt_hostname,
                mqtt_port,
                location_id,
                node_id,
                fsm_mqtt_topic,
            )

            fsm_cleanup_args = gw.get_command_arguments(
                f"{gw_ap_if_name}",
                f"{lan_bridge_if_name}",
                f"{lan_bridge_if_name}.dpi",
            )

            def _trigger():
                assert gw.execute("tools/device/fut_configure_mqtt", fsm_gw_mqtt_cfg_args)[0] == ExpectedShellResult
                assert (
                    gw.execute("tools/device/configure_dpi_sni_plugin", configure_dpi_sni_plugin_args)[0]
                    == ExpectedShellResult
                )
                # Ensure gatekeeper service is running in docker
                gk_host = f"https://{pytest.fut_configurator.fut_test_hostname}:8443/gatekeeper"
                cmd = f"curl --silent --http2 --cacert {server.fut_dir}/shell/tools/server/certs/ca.pem {gk_host}"
                assert server.execute_in_docker(cmd)[0] == ExpectedShellResult
                assert w1.device_api.run_raw(test_client_cmd)[0] == ExpectedShellResult

        try:
            with step("Ensure WAN connectivity"):
                assert gw.check_wan_connectivity()
            with step("Put GW into router mode"):
                assert gw.configure_device_mode(device_mode="router")
            with step("Configure Home AP interface"):
                assert gw.configure_radio_vif_and_network()
            with step("Determine GW MAC"):
                gw_mac = "".join(gw.device_api.iface.get_vif_mac(gw_ap_if_name))
            with step("Client connection"):
                security_args = gw.configure_wifi_security(return_as_dict=True)
                w1.device_api.connect(
                    ssid=ssid,
                    psk=psk,
                    key_mgmt=security_args["key_mgmt_mapping"],
                    retry=client_retry,
                )
            with step("Verify client connection"):
                assert w1_mac in gw.device_api.get_wifi_associated_clients()[0]
            with step("Create tap interface"):
                assert (
                    gw.execute("tools/device/configure_dpi_tap_interface", tap_interface_args)[0] == ExpectedShellResult
                )
            with step("Configure Openflow rules"):
                assert (
                    gw.execute("tools/device/configure_dpi_openflow_rules", openflow_rules_args)[0]
                    == ExpectedShellResult
                )
            with step("Configure Openflow tags"):
                openflow_tags_args = gw.get_command_arguments(
                    gw_mac,
                    w1_mac,
                    server_mac,
                )
                assert (
                    gw.execute("tools/device/configure_sni_openflow_tags", openflow_tags_args)[0] == ExpectedShellResult
                )
            with step("Configure FSM policy"):
                assert gw.execute("tools/device/configure_gatekeeper_policy")[0] == ExpectedShellResult
            with step("Restart MQTT broker on server"):
                assert server.execute("tools/server/start_mqtt", "--restart")[0] == ExpectedShellResult
            with step("Test case"):
                validation_parameters.update({"deviceMac": w1_mac.upper()})
                assert server.mqtt_trigger_and_validate_message(
                    topic=fsm_mqtt_topic,
                    trigger=_trigger,
                    expected_data=validation_parameters,
                    node_filter=node_id,
                )
        finally:
            with step("Restart OpenSync"):
                assert gw.execute("tools/device/restart_opensync")[0] == ExpectedShellResult
            with step("Cleanup"):
                gw.execute("tools/device/remove_tap_interfaces", tap_interface_args)
                gw.execute("tests/fsm/fsm_cleanup", fsm_cleanup_args)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", fsm_config.get("fsm_configure_fsm_tables", []))
    def test_fsm_configure_fsm_tables(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            tap_name_postfix = cfg.get("tap_name_postfix")
            handler = cfg.get("handler")
            plugin = cfg.get("plugin")

            # GW specific arguments
            opensync_rootdir = gw.capabilities.get_opensync_rootdir()
            lan_bridge_if_name = gw.capabilities.get_lan_bridge_ifname()

            fsm_plugin_path = Path(plugin) if Path(plugin).is_absolute() else Path(f"{opensync_rootdir}/lib/{plugin}")
            test_args = gw.get_command_arguments(
                lan_bridge_if_name,
                tap_name_postfix,
                handler,
                fsm_plugin_path,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/fsm/fsm_configure_fsm_tables", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", fsm_config.get("fsm_configure_openflow_rules", []))
    def test_fsm_configure_openflow_rules(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            action = cfg.get("action")
            rule = cfg.get("rule")
            token = cfg.get("token")

            # GW specific arguments
            lan_bridge_if_name = gw.capabilities.get_lan_bridge_ifname()

            test_args = gw.get_command_arguments(
                lan_bridge_if_name,
                action,
                rule,
                token,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/fsm/fsm_configure_of_rules", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", fsm_config.get("fsm_configure_test_dpi_http_request", []))
    def test_fsm_configure_test_dpi_http_request(self, cfg: dict, update_baseline_os_pids):
        expected_action = cfg.get("expected_action")
        test_client_cmd = cfg.get("test_client_cmd")
        validation_parameters = {
            "action": expected_action,
            "httpUrl": f"{test_client_cmd.split()[1]}/",
        }
        self.fsm_content_filtering_test_procedure(cfg, validation_parameters)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", fsm_config.get("fsm_configure_test_dpi_https_sni_request", []))
    def test_fsm_configure_test_dpi_https_sni_request(self, cfg: dict, update_baseline_os_pids):
        expected_action = cfg.get("expected_action")
        test_client_cmd = cfg.get("test_client_cmd")
        netloc = urlparse(test_client_cmd.split()[1]).netloc
        validation_parameters = {
            "action": expected_action,
            "httpsSni": netloc,
        }
        self.fsm_content_filtering_test_procedure(cfg, validation_parameters)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", fsm_config.get("fsm_configure_test_dpi_http_url_request", []))
    def test_fsm_configure_test_dpi_http_url_request(self, cfg: dict, update_baseline_os_pids):
        expected_action = cfg.get("expected_action")
        test_client_cmd = cfg.get("test_client_cmd")
        validation_parameters = {
            "action": expected_action,
            "httpUrl": test_client_cmd.split()[1],
        }
        self.fsm_content_filtering_test_procedure(cfg, validation_parameters)
