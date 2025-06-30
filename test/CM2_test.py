import time

import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.common import compare_fw_versions


@pytest.fixture(scope="module")
def cm2_setup(request: pytest.FixtureRequest):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        handlers = []
        if "gw_handler" in fixturenames:
            gw_handler = request.getfixturevalue("gw_handler")
            handlers.append(gw_handler)

            manager_name = "cm"
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
            gw_handler.device_test_setup(test_suite_name=module_name.lower())
    yield


@pytest.mark.skip(reason="Flaky test")
def test_cm2_cloud_down(cm2_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        controller_ip = gw_handler.execute_with_logging("tools/device/get_connected_cloud_controller_ip")

        if controller_ip[0] != 0 or controller_ip[1] == "" or controller_ip[1] is None:
            RuntimeError("Failed to retrieve IP address of Cloud controller")

        redirector_hostname = gw_handler.execute_with_logging("tools/device/get_redirector_hostname")

        if redirector_hostname[0] != 0 or redirector_hostname[1] == "" or redirector_hostname[1] is None:
            raise RuntimeError("Failed to retrieve hostname of the redirector")

        counter = parametrized_test_config.get("unreachable_cloud_counter")
        cloud_recovered_args = get_command_arguments(
            gw_wan_iface,
            "0",
            "cloud_recovered",
        )
        cloud_check_counter_args = get_command_arguments(
            gw_wan_iface,
            counter,
            "check_counter",
        )
        cloud_block_args = get_command_arguments(
            redirector_hostname[1],
            controller_ip[1],
            "block",
        )
        cloud_unblock_args = get_command_arguments(
            redirector_hostname[1],
            controller_ip[1],
            "unblock",
        )

    try:
        with step("Test Case"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_recovered_args)[0] == 0
            assert (
                server_handler.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_block_args, as_sudo=True)[
                    0
                ]
                == 0
            )
            assert gw_handler.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_check_counter_args)[0] == 0
            assert (
                server_handler.execute(
                    "tools/server/cm/manipulate_cloud_ip_addresses",
                    cloud_unblock_args,
                    as_sudo=True,
                )[0]
                == 0
            )
            assert gw_handler.execute_with_logging("tests/cm2/cm2_cloud_down", cloud_recovered_args)[0] == 0
    finally:
        with step("Cleanup"):
            server_handler.execute("tools/server/cm/manipulate_cloud_ip_addresses", cloud_unblock_args, as_sudo=True)


@pytest.mark.skip(reason="Flaky test")
def test_cm2_dns_failure(cm2_setup, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]

        dns_blocked_args = get_command_arguments("dns_blocked")
        dns_unblocked_args = get_command_arguments("dns_recovered")
        gw_wan_inet_addr_blocked = get_command_arguments(gw_wan_inet_addr, "block")
        gw_wan_inet_addr_unblocked = get_command_arguments(gw_wan_inet_addr, "unblock")

    try:
        with step("Test Case"):
            assert gw_handler.execute("tests/cm2/cm2_dns_failure", dns_unblocked_args)[0] == 0
            assert (
                server_handler.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_blocked, as_sudo=True)[0]
                == 0
            )
            assert gw_handler.execute("tests/cm2/cm2_dns_failure", dns_blocked_args)[0] == 0
            assert (
                server_handler.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_unblocked, as_sudo=True)[0]
                == 0
            )
            assert gw_handler.execute("tests/cm2/cm2_dns_failure", dns_unblocked_args)[0] == 0
    finally:
        with step("Cleanup"):
            assert (
                server_handler.execute("tools/server/cm/address_dns_man", gw_wan_inet_addr_unblocked, as_sudo=True)[0]
                == 0
            )


@pytest.mark.skip(reason="Flaky test")
def test_cm2_internet_lost(cm2_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]

        counter = parametrized_test_config.get("unreachable_internet_counter")
        internet_blocked_args = get_command_arguments(gw_wan_iface, counter, "check_counter")
        internet_recovered_args = get_command_arguments(gw_wan_iface, "0", "internet_recovered")
        cloud_block_args = get_command_arguments(gw_wan_inet_addr, "block")
        cloud_unblock_args = get_command_arguments(gw_wan_inet_addr, "unblock")

    try:
        with step("Test Case"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_internet_lost", internet_recovered_args)[0] == 0
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", cloud_block_args, as_sudo=True)[0] == 0
            )
            time.sleep(3)
            assert gw_handler.execute_with_logging("tests/cm2/cm2_internet_lost", internet_blocked_args)[0] == 0
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)[0] == 0
            )
            time.sleep(3)
            assert gw_handler.execute_with_logging("tests/cm2/cm2_internet_lost", internet_recovered_args)[0] == 0
    finally:
        with step("Cleanup"):
            assert server_handler.restart_cloud()
            server_handler.execute("tools/server/cm/address_internet_man", cloud_unblock_args, as_sudo=True)


@pytest.mark.skip(reason="Flaky test")
def test_cm2_link_lost(cm2_setup, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        test_args = get_command_arguments(gw_wan_iface)

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cm2/cm2_link_lost", test_args)[0] == 0


@pytest.mark.skip(reason="Flaky test")
def test_cm2_ssl_check(cm2_setup, server_handler, gw_handler):
    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cm2/cm2_ssl_check")[0] == 0


@pytest.mark.skip(reason="Flaky test")
def test_cm2_network_outage_link(cm2_setup, server_handler, gw_handler):
    min_opensync_version = "6.5.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        test_args = get_command_arguments(gw_wan_iface)

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/cm2/cm2_network_outage_link", test_args)[0] == 0
    with step("Wait 60s to make sure gw fully recovers"):
        time.sleep(60)


@pytest.mark.skip(reason="Flaky test")
def test_cm2_network_outage_router(cm2_setup, server_handler, gw_handler):
    min_opensync_version = "6.5.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]

        block_args_device = get_command_arguments("router_blocked")
        block_args_server = get_command_arguments(gw_wan_inet_addr, "block")
        unblock_args_device = get_command_arguments("router_unblocked")
        unblock_args_server = get_command_arguments(gw_wan_inet_addr, "unblock")

    try:
        with step("Run arping manipuation script - BLOCK"):
            assert server_handler.execute("tools/server/cm/arping_man", block_args_server, as_sudo=True)[0] == 0

        with step("Run address_internet_man script - BLOCK"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", block_args_server, as_sudo=True)[0] == 0
            )

        with step("Run cm2_network_outage_router script - BLOCK"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_network_outage_router", block_args_device)[0] == 0

        with step("Run arping manipuation script - UNBLOCK"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", unblock_args_server, as_sudo=True)[0]
                == 0
            )

        with step("Run address_internet_man script - UNBLOCK"):
            assert server_handler.execute("tools/server/cm/arping_man", unblock_args_server, as_sudo=True)[0] == 0

        with step("Run cm2_network_outage_router script - UNBLOCK"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_network_outage_router", unblock_args_device)[0] == 0

    finally:
        with step("Cleanup"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", unblock_args_server, as_sudo=True)[0]
                == 0
            )
            assert server_handler.execute("tools/server/cm/arping_man", unblock_args_server, as_sudo=True)[0] == 0


@pytest.mark.skip(reason="Flaky test")
def test_cm2_network_outage_internet(cm2_setup, server_handler, gw_handler):
    min_opensync_version = "6.5.0.0"
    opensync_version = gw_handler.opensync

    if compare_fw_versions(opensync_version, min_opensync_version, "<"):
        pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        # GW specific arguments
        gw_wan_iface = gw_handler.capabilities.get_primary_wan_iface()
        gw_wan_inet_addr = gw_handler.get_ips(iface=gw_wan_iface)["ipv4"]

        block_args_device = get_command_arguments("internet_blocked")
        block_args_server = get_command_arguments(gw_wan_inet_addr, "block")
        unblock_args_device = get_command_arguments("internet_unblocked")
        unblock_args_server = get_command_arguments(gw_wan_inet_addr, "unblock")

    try:
        with step("Run address_internet_man script - BLOCK"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", block_args_server, as_sudo=True)[0] == 0
            )

        with step("Run cm2_network_outage_internet script - BLOCK"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_network_outage_internet", block_args_device)[0] == 0

        with step("Run address_internet_man script - UNBLOCK"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", unblock_args_server, as_sudo=True)[0]
                == 0
            )

        with step("Run cm2_network_outage_internet script - UNBLOCK"):
            assert gw_handler.execute_with_logging("tests/cm2/cm2_network_outage_internet", unblock_args_device)[0] == 0

    finally:
        with step("Cleanup"):
            assert (
                server_handler.execute("tools/server/cm/address_internet_man", unblock_args_server, as_sudo=True)[0]
                == 0
            )
