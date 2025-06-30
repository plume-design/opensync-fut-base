from datetime import datetime

import pytest

from framework.lib.fut_lib import (
    execute_locally,
    get_command_arguments,
    reboot_pods_and_wait_available,
    step,
)


@pytest.fixture(scope="module")
def onbrd_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "dm"
            if manager_name.upper() not in gw_handler.kconfig_managers:
                pytest.skip(f"{manager_name.upper()} not present on device")

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


def test_onbrd_set_and_verify_bridge_mode(onbrd_setup, gw_handler):
    try:
        with step("Test case"):
            gw_handler.configure_device_mode(device_mode="bridge")
    finally:
        with step("Restore connection"):
            gw_handler.configure_device_mode(device_mode="router")


def test_onbrd_verify_client_certificate_files(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        cert_file = parametrized_test_config.get("cert_file")
        test_args = get_command_arguments(
            cert_file,
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_client_certificate_files", test_args)[0] == 0


def test_onbrd_verify_client_tls_connection(onbrd_setup, server_handler, gw_handler):
    with step("Cloud preparation"):
        assert server_handler.restart_cloud()

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_client_tls_connection")[0] == 0


def test_onbrd_verify_dhcp_dry_run_success(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Check device if WANO enabled"):
        if "WANO" in gw_handler.kconfig_managers:
            pytest.skip("Testcase not applicable to WANO enabled devices")

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        if_name = parametrized_test_config.get("if_name")
        test_args = get_command_arguments(
            if_name,
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_dhcp_dry_run_success", test_args)[0] == 0


def test_onbrd_verify_dut_client_certificate_file_on_server(onbrd_setup, server_handler, gw_handler):
    with step("Acquire certificate details"):
        eth_wan_name = gw_handler.capabilities.get_primary_wan_iface()
        cert_file_path_args = get_command_arguments("cert_file", "full_path")
        ca_file_path_args = get_command_arguments("ca_file", "full_path")
        cert_file_args = get_command_arguments("cert_file", "file_name")
        ca_file_args = get_command_arguments("ca_file", "file_name")
        cert_full_path = gw_handler.execute("tools/device/get_client_certificate", cert_file_path_args)

        if cert_full_path[0] != 0 or cert_full_path[1] == "" or cert_full_path[1] is None:
            raise RuntimeError("Failed to retrieve client certificate path from device")

        ca_full_path = gw_handler.execute("tools/device/get_client_certificate", ca_file_path_args)

        if ca_full_path[0] != 0 or ca_full_path[1] == "" or ca_full_path[1] is None:
            raise RuntimeError("Failed to retrieve CA certificate path from device")

        cert_file = gw_handler.execute("tools/device/get_client_certificate", cert_file_args)

        if cert_file[0] != 0 or cert_file[1] == "" or cert_file[1] is None:
            raise RuntimeError("Failed to retrieve client certificate from device")

        ca_file = gw_handler.execute("tools/device/get_client_certificate", ca_file_args)

        if ca_file[0] != 0 or ca_file[1] == "" or ca_file[1] is None:
            raise RuntimeError("Failed to retrieve CA certificate from device")

    with step("Copy certificates from GW to server"):
        cert_location = "tools/server/files"
        gw_handler.get_file(cert_full_path[1], cert_location)
        gw_handler.get_file(ca_full_path[1], cert_location)
        cert_verify_args = get_command_arguments(
            f"{cert_location}/{gw_handler.nickname}/{cert_file[1]}",
            f"{cert_location}/{gw_handler.nickname}/{ca_file[1]}",
        )
        common_name_args = get_command_arguments(f"{cert_location}/{gw_handler.nickname}/{cert_file[1]}")

    with step("Get common name from certificate"):
        common_name = execute_locally(
            "shell/tools/server/get_common_name_from_certificate",
            common_name_args,
        )
        if common_name[0] != 0 or common_name[1] == "" or common_name[1] is None:
            raise RuntimeError("Failed to retrieve Common Name of certificate")

        cert_cn_verify_args = get_command_arguments(common_name[1], eth_wan_name)

    with step("Test case"):
        assert (
            execute_locally(
                "shell/tools/server/verify_dut_client_certificate_file_on_server",
                cert_verify_args,
            )[0]
            == 0
        )

    try:
        with step("Test case - optional"):
            gw_handler.execute("tools/device/verify_dut_client_certificate_common_name", cert_cn_verify_args)
    finally:
        pass


def test_onbrd_verify_dut_system_time_accuracy(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        time_accuracy = parametrized_test_config.get("time_accuracy")

        time_sec_since_epoch = int(datetime.utcnow().strftime("%s"))
        test_args = get_command_arguments(time_sec_since_epoch, time_accuracy)

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_dut_system_time_accuracy", test_args)[0] == 0


def test_onbrd_verify_fw_version_awlan_node(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        search_rule = parametrized_test_config.get("search_rule")

        test_args = get_command_arguments(
            search_rule,
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_fw_version_awlan_node", test_args)[0] == 0


def test_onbrd_verify_id_awlan_node(onbrd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        gw_mac = "".join(gw_handler.iface.get_inet_mac(lan_br_if_name))
        test_args = get_command_arguments(
            gw_mac,
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_id_awlan_node", test_args)[0] == 0


def test_onbrd_verify_manager_hostname_resolved(onbrd_setup, gw_handler):
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_manager_hostname_resolved")[0] == 0


def test_onbrd_verify_model_awlan_node(onbrd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments - use original unchanged model string
        test_args = get_command_arguments(gw_handler.model_org)

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_model_awlan_node", test_args)[0] == 0


def test_onbrd_verify_number_of_radios(onbrd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        radio_bands = gw_handler.capabilities.get_radio_antennas()
        test_args = get_command_arguments(
            len(radio_bands),
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_number_of_radios", test_args)[0] == 0


def test_onbrd_verify_redirector_address_awlan_node(onbrd_setup, gw_handler):
    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_redirector_address_awlan_node")[0] == 0


def test_onbrd_verify_router_mode(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        dhcp_start_pool = parametrized_test_config.get("dhcp_start_pool")
        dhcp_end_pool = parametrized_test_config.get("dhcp_end_pool")
        gateway_inet_addr = parametrized_test_config.get("gateway_inet_addr")

        # GW specific arguments
        wan_link_selection = gw_handler.capabilities.is_wan_link_selection_enabled()
        if "WANO" in gw_handler.kconfig_managers or not wan_link_selection:
            wan_if_name = gw_handler.capabilities.get_primary_wan_iface()
        else:
            wan_if_name = gw_handler.capabilities.get_wan_bridge_ifname()

        if not wan_if_name:
            raise RuntimeError("Could not determine WAN interface name from device configuration.")

        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()

        if not lan_br_if_name:
            raise RuntimeError("Could not determine LAN bridge interface name from device configuration.")

        test_args = get_command_arguments(
            wan_if_name,
            lan_br_if_name,
            dhcp_start_pool,
            dhcp_end_pool,
            gateway_inet_addr,
        )

    try:
        with step("Test case"):
            assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_router_mode", test_args)[0] == 0
    finally:
        with step("Restore connection"):
            gw_handler.execute("tests/dm/onbrd_setup")


def test_onbrd_verify_wan_iface_mac_addr(onbrd_setup, gw_handler):
    with step("Preparation of testcase parameters"):
        wan_if_name = gw_handler.capabilities.get_primary_wan_iface()
        test_args = get_command_arguments(
            wan_if_name,
        )

    with step("Test case"):
        if "WANO" in gw_handler.kconfig_managers:
            assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_wan_iface_mac_addr")[0] == 0
        else:
            assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_wan_iface_mac_addr", test_args)[0] == 0


def test_onbrd_verify_wan_ip_address(onbrd_setup, parametrized_test_config, gw_handler):
    with step("Preparation of testcase parameters"):
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]

        if "if_name" in parametrized_test_config:
            if_name = parametrized_test_config.get("if_name")
        else:
            wan_link_selection = gw_handler.capabilities.is_wan_link_selection_enabled()
            if "WANO" in gw_handler.kconfig_managers or not wan_link_selection:
                if_name = gw_handler.capabilities.get_primary_wan_iface()
            else:
                if_name = gw_handler.capabilities.get_wan_bridge_ifname()

        test_args = get_command_arguments(
            if_name,
            gw_wan_inet_addr,
        )

    with step("Test case"):
        assert gw_handler.execute_with_logging("tests/dm/onbrd_verify_wan_ip_address", test_args)[0] == 0
