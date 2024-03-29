from datetime import datetime

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, execute_locally, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
onbrd_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def onbrd_setup():
    test_class_name = ["TestOnbrd"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for ONBRD: {nodes + clients}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            phy_radio_ifnames = device_handler.capabilities.get_phy_radio_ifnames(return_type=list)
            setup_args = device_handler.get_command_arguments(*phy_radio_ifnames)
            device_handler.fut_device_setup(test_suite_name="dm", setup_args=setup_args)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestOnbrd:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_set_and_verify_bridge_mode", []))
    def test_onbrd_set_and_verify_bridge_mode(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        try:
            with step("Test case"):
                assert gw.configure_device_mode(device_mode="bridge")
        finally:
            with step("Restore connection"):
                assert gw.execute_with_logging("tests/dm/onbrd_setup")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_client_certificate_files", []))
    def test_onbrd_verify_client_certificate_files(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            cert_file = cfg.get("cert_file")
            test_args = gw.get_command_arguments(
                cert_file,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_client_certificate_files", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_client_tls_connection", []))
    def test_onbrd_verify_client_tls_connection(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            tls_ver = cfg.get("tls_ver")

        with step("Cloud preparation"):
            assert server.start_cloud()
            assert server.change_fut_cloud_tls_ver(tls_ver)
            assert server.restart_cloud()

        with step("Test case"):
            assert gw.execute_with_logging("tests/dm/onbrd_verify_client_tls_connection")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_dhcp_dry_run_success", []))
    def test_onbrd_verify_dhcp_dry_run_success(self, cfg: dict):
        gw = pytest.gw

        with step("Check device if WANO enabled"):
            check_kconfig_wano_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            check_kconfig_wano_ec = gw.execute("tools/device/check_kconfig_option", check_kconfig_wano_args)[0]
            if check_kconfig_wano_ec == 0:
                pytest.skip("Testcase not applicable to WANO enabled devices")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            if_name = cfg.get("if_name")
            test_args = gw.get_command_arguments(
                if_name,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_dhcp_dry_run_success", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_dut_client_certificate_file_on_server", []))
    def test_onbrd_verify_dut_client_certificate_file_on_server(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Acquire certificate details"):
            eth_wan_name = gw.capabilities.get_primary_wan_iface()
            cert_file_path_args = gw.get_command_arguments("cert_file", "full_path")
            ca_file_path_args = gw.get_command_arguments("ca_file", "full_path")
            cert_file_args = gw.get_command_arguments("cert_file", "file_name")
            ca_file_args = gw.get_command_arguments("ca_file", "file_name")
            cert_full_path = gw.execute("tools/device/get_client_certificate", cert_file_path_args)

            if cert_full_path[0] != ExpectedShellResult or cert_full_path[1] == "" or cert_full_path[1] is None:
                raise RuntimeError("Failed to retrieve client certificate path from device")

            ca_full_path = gw.execute("tools/device/get_client_certificate", ca_file_path_args)

            if ca_full_path[0] != ExpectedShellResult or ca_full_path[1] == "" or ca_full_path[1] is None:
                raise RuntimeError("Failed to retrieve CA certificate path from device")

            cert_file = gw.execute("tools/device/get_client_certificate", cert_file_args)

            if cert_file[0] != ExpectedShellResult or cert_file[1] == "" or cert_file[1] is None:
                raise RuntimeError("Failed to retrieve client certificate from device")

            ca_file = gw.execute("tools/device/get_client_certificate", ca_file_args)

            if ca_file[0] != ExpectedShellResult or ca_file[1] == "" or ca_file[1] is None:
                raise RuntimeError("Failed to retrieve CA certificate from device")

        with step("Copy certificates from GW to server"):
            cert_location = "tools/server/files"
            gw.device_api.get_file(cert_full_path[1], cert_location)
            gw.device_api.get_file(ca_full_path[1], cert_location)
            cert_verify_args = server.get_command_arguments(
                f"{cert_location}/{gw.name}/{cert_file[1]}",
                f"{cert_location}/{gw.name}/{ca_file[1]}",
            )
            common_name_args = server.get_command_arguments(f"{cert_location}/{gw.name}/{cert_file[1]}")

        with step("Get common name from certificate"):
            common_name = execute_locally(
                "shell/tools/server/get_common_name_from_certificate",
                common_name_args,
            )
            if common_name[0] != ExpectedShellResult or common_name[1] == "" or common_name[1] is None:
                raise RuntimeError("Failed to retrieve Common Name of certificate")

            cert_cn_verify_args = server.get_command_arguments(common_name[1], eth_wan_name)

        with step("Test case"):
            assert (
                execute_locally(
                    "shell/tools/server/verify_dut_client_certificate_file_on_server",
                    cert_verify_args,
                )[0]
                == ExpectedShellResult
            )

        try:
            with step("Test case - optional"):
                gw.execute("tools/device/verify_dut_client_certificate_common_name", cert_cn_verify_args)
        finally:
            pass

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_dut_system_time_accuracy", []))
    def test_onbrd_verify_dut_system_time_accuracy(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            time_accuracy = cfg.get("time_accuracy")

            time_sec_since_epoch = int(datetime.utcnow().strftime("%s"))
            test_args = gw.get_command_arguments(time_sec_since_epoch, time_accuracy)

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_dut_system_time_accuracy", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_fw_version_awlan_node", []))
    def test_onbrd_verify_fw_version_awlan_node(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            search_rule = cfg.get("search_rule")

            test_args = gw.get_command_arguments(
                search_rule,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_fw_version_awlan_node", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_id_awlan_node", []))
    def test_onbrd_verify_id_awlan_node(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()
            gw_mac = "".join(gw.device_api.iface.get_inet_mac(lan_br_if_name))
            test_args = gw.get_command_arguments(
                gw_mac,
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/dm/onbrd_verify_id_awlan_node", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_manager_hostname_resolved", []))
    def test_onbrd_verify_manager_hostname_resolved(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            device_type = gw.capabilities.get_device_type()
            is_extender = "true" if device_type == "extender" else "false"
            test_args = gw.get_command_arguments(
                is_extender,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_manager_hostname_resolved", test_args)[0]
                == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_model_awlan_node", []))
    def test_onbrd_verify_model_awlan_node(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            model = gw.model.upper()
            test_args = gw.get_command_arguments(
                model,
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_model_awlan_node", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_model_awlan_node", []))
    def test_onbrd_verify_number_of_radios(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # GW specific arguments
            radio_bands = gw.capabilities.get_radio_antennas()
            test_args = gw.get_command_arguments(
                len(radio_bands),
            )

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_number_of_radios", test_args)[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_redirector_address_awlan_node", []))
    def test_onbrd_verify_redirector_address_awlan_node(self, cfg: dict):
        gw = pytest.gw

        with step("Test case"):
            assert (
                gw.execute_with_logging("tests/dm/onbrd_verify_redirector_address_awlan_node")[0] == ExpectedShellResult
            )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_router_mode", []))
    def test_onbrd_verify_router_mode(self, cfg: dict, update_baseline_os_pids):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            dhcp_start_pool = cfg.get("dhcp_start_pool")
            dhcp_end_pool = cfg.get("dhcp_end_pool")
            gateway_inet_addr = cfg.get("gateway_inet_addr")

            # GW specific arguments
            device_type = gw.capabilities.get_device_type()
            wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args)[0] == ExpectedShellResult

            if has_wano or device_type == "residential_gateway":
                wan_if_name = gw.capabilities.get_primary_wan_iface()
            else:
                wan_if_name = gw.capabilities.get_wan_bridge_ifname()

            if not wan_if_name:
                raise RuntimeError("Could not determine WAN interface name from device configuration.")

            lan_br_if_name = gw.capabilities.get_lan_bridge_ifname()

            if not lan_br_if_name:
                raise RuntimeError("Could not determine LAN bridge interface name from device configuration.")

            test_args = gw.get_command_arguments(
                wan_if_name,
                lan_br_if_name,
                dhcp_start_pool,
                dhcp_end_pool,
                gateway_inet_addr,
            )

        try:
            with step("Test case"):
                assert gw.execute_with_logging("tests/dm/onbrd_verify_router_mode", test_args)[0] == ExpectedShellResult
        finally:
            with step("Restore connection"):
                gw.execute("tests/dm/onbrd_setup")

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_wan_iface_mac_addr", []))
    def test_onbrd_verify_wan_iface_mac_addr(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            wan_if_name = gw.capabilities.get_primary_wan_iface()
            test_args = gw.get_command_arguments(
                wan_if_name,
            )

        with step("Check if WANO is enabled on device"):
            wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
            has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args)[0] == ExpectedShellResult

        with step("Test case"):
            if has_wano:
                assert gw.execute_with_logging("tests/dm/onbrd_verify_wan_iface_mac_addr")[0] == ExpectedShellResult
            else:
                assert (
                    gw.execute_with_logging("tests/dm/onbrd_verify_wan_iface_mac_addr", test_args)[0]
                    == ExpectedShellResult
                )

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", onbrd_config.get("onbrd_verify_wan_ip_address", []))
    def test_onbrd_verify_wan_ip_address(self, cfg: dict):
        server, gw = pytest.server, pytest.gw

        with step("Preparation of testcase parameters"):
            gw_wan_inet_addr = server.wan_ip_dict.get("gw")

            if "if_name" in cfg:
                if_name = cfg.get("if_name")
            else:
                device_type = gw.capabilities.get_device_type()
                wan_handling_args = gw.get_command_arguments("CONFIG_MANAGER_WANO", "y")
                has_wano = gw.execute("tools/device/check_kconfig_option", wan_handling_args)[0] == ExpectedShellResult
                if has_wano or device_type == "residential_gateway":
                    if_name = gw.capabilities.get_primary_wan_iface()
                else:
                    if_name = gw.capabilities.get_wan_bridge_ifname()

            test_args = gw.get_command_arguments(
                if_name,
                gw_wan_inet_addr,
            )

        with step("Test case"):
            assert gw.execute_with_logging("tests/dm/onbrd_verify_wan_ip_address", test_args)[0] == ExpectedShellResult
