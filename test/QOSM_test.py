import pytest

from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.common import compare_fw_versions


@pytest.fixture(scope="module")
def qosm_setup(request: pytest.FixtureRequest):
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


def test_qosm_verify_linux_traffic_control_rules(qosm_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        ingress_action_args = f"{parametrized_test_config['ingress_action']} dev {lan_br_if_name}"
        egress_action_args = f"{parametrized_test_config['egress_action']} dev {lan_br_if_name}"
        test_args = get_command_arguments(
            parametrized_test_config["if_name"],
            parametrized_test_config["ingress_match"],
            ingress_action_args,
            parametrized_test_config["ingress_expected_str"],
            parametrized_test_config["egress_match"],
            egress_action_args,
            parametrized_test_config["egress_expected_str"],
            parametrized_test_config["priority"],
            parametrized_test_config["ingress_updated_match"],
            parametrized_test_config["ingress_expected_str_after_update"],
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/qosm/qosm_verify_linux_traffic_control_rules", test_args)[0] == 0


def test_qosm_verify_linux_traffic_control_template_rules(qosm_setup, parametrized_test_config, gw_handler):
    with step("Check bridge type"):
        if not gw_handler.bridge_type == "native_bridge":
            pytest.skip(
                "Test is applicable only when device is configured with Linux Native Bridge, skipping the test.",
            )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        lan_br_if_name = gw_handler.capabilities.get_lan_bridge_ifname()
        ingress_action_args = f"{parametrized_test_config['ingress_action']} dev {lan_br_if_name}"
        egress_action_args = f"{parametrized_test_config['egress_action']} dev {lan_br_if_name}"
        test_args = get_command_arguments(
            parametrized_test_config["if_name"],
            parametrized_test_config["ingress_match"],
            ingress_action_args,
            parametrized_test_config["ingress_tag_name"],
            parametrized_test_config["egress_match"],
            egress_action_args,
            parametrized_test_config["egress_match_with_tag"],
            parametrized_test_config["egress_expected_str"],
        )

    with step("Test Case"):
        assert (
            gw_handler.execute_with_logging("tests/qosm/qosm_verify_linux_traffic_control_template_rules", test_args)[0]
            == 0
        )


# Interface_QoS/Interface_Queue QoS testcase:
def test_qosm_verify_interface_queue(qosm_setup, parametrized_test_config, gw_handler):
    with step("Check test eligibility"):
        kconfig = dict(item.split("=", 1) for item in gw_handler.kconfig)

        if kconfig.get("CONFIG_OSN_LINUX_QOS") != "y":
            pytest.skip("CONFIG_OSN_LINUX_QOS kconfig not enabled, device not marked QoS capable")

    with step("Preparation of testcase parameters"):
        test_args = get_command_arguments(
            parametrized_test_config["test_if_name"],
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/qosm/qosm_verify_interface_queue", test_args)[0] == 0


# Interface_QoS/Linux_Queue QoS testcase:
def test_qosm_verify_linux_queue(qosm_setup, parametrized_test_config, gw_handler):
    with step("Check test eligibility"):
        kconfig = dict(item.split("=", 1) for item in gw_handler.kconfig)

        if kconfig.get("CONFIG_OSN_LINUX_QOS") != "y":
            pytest.skip("CONFIG_OSN_LINUX_QOS kconfig not enabled, device not marked QoS capable")

        if kconfig.get("CONFIG_OSN_BACKEND_QDISC_LINUX") != "y":
            pytest.skip("CONFIG_OSN_BACKEND_QDISC_LINUX kconfig not enabled, device not marked Linux-qdisc QoS capable")
        if kconfig.get("CONFIG_OSN_LINUX_QDISC") != "y":
            pytest.skip("CONFIG_OSN_LINUX_QDISC kconfig not enabled, device not marked Linux-qdisc QoS capable")

    with step("Preparation of testcase parameters"):
        test_args = get_command_arguments(
            parametrized_test_config["test_if_name"],
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/qosm/qosm_verify_linux_queue", test_args)[0] == 0


# Adaptive QoS testcase
def test_qosm_verify_adaptive_qos(qosm_setup, parametrized_test_config, gw_handler):
    with step("Check test eligibility"):
        kconfig = dict(item.split("=", 1) for item in gw_handler.kconfig)

        if kconfig.get("CONFIG_OSN_LINUX_QOS") != "y":
            pytest.skip("CONFIG_OSN_LINUX_QOS kconfig not enabled, device not marked QoS capable")

        if kconfig.get("CONFIG_OSN_BACKEND_QDISC_LINUX") != "y":
            pytest.skip("CONFIG_OSN_BACKEND_QDISC_LINUX kconfig not enabled, device not marked Linux-qdisc QoS capable")
        if kconfig.get("CONFIG_OSN_LINUX_QDISC") != "y":
            pytest.skip("CONFIG_OSN_LINUX_QDISC kconfig not enabled, device not marked Linux-qdisc QoS capable")

        if kconfig.get("CONFIG_OSN_BACKEND_ADAPTIVE_QOS_CAKE_AUTORATE") != "y":
            pytest.skip(
                "CONFIG_OSN_BACKEND_ADAPTIVE_QOS_CAKE_AUTORATE kconfig not enabled, device not Adaptive QoS with cake-autorate capable",
            )

        min_opensync_version = "6.7.0"
        opensync_version = gw_handler.opensync
        if compare_fw_versions(opensync_version, min_opensync_version, "<"):
            pytest.skip(f"Insufficient OpenSync version:{opensync_version}. Required {min_opensync_version} or higher.")

    with step("Preparation of testcase parameters"):
        test_args = get_command_arguments(
            parametrized_test_config["test_if_name_up"],
            parametrized_test_config["test_if_name_down"],
        )

    with step("Test Case"):
        assert gw_handler.execute_with_logging("tests/qosm/qosm_verify_adaptive_qos", test_args)[0] == 0
