import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
ltem_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def ltem_setup():
    test_class_name = ["TestLtem"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for LTEM: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "LTEM" not in node_handler.get_kconfig_managers():
            pytest.skip("LTEM not present on device")
        setup_args = node_handler.get_command_arguments("wwan0", "data.icore.name", "true")
        node_handler.fut_device_setup(test_suite_name="ltem", setup_args=setup_args)
        service_status = node_handler.get_node_services_and_status()
        if service_status["ltem"]["status"] != "enabled":
            pytest.skip("LTEM not enabled on device")
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestLtem:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", ltem_config.get("ltem_force_lte", []))
    def test_ltem_force_lte(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            lte_if_name = cfg.get("lte_if_name")
            test_args = gw.get_command_arguments(
                lte_if_name,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/ltem/ltem_force_lte", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", ltem_config.get("ltem_validation", []))
    def test_ltem_validation(self, cfg: dict):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            access_point_name = cfg.get("access_point_name")
            has_l2 = cfg.get("has_l2")
            has_l3 = cfg.get("has_l3")
            if_type = cfg.get("if_type")
            lte_if_name = cfg.get("lte_if_name")
            metric = cfg.get("metric")
            route_tool_path = cfg.get("route_tool_path")

            # Keep the same order of arguments if making any adjustments
            test_args = gw.get_command_arguments(
                lte_if_name,
                if_type,
                access_point_name,
                has_l2,
                has_l3,
                metric,
                route_tool_path,
            )

        with step("Test Case"):
            assert gw.execute_with_logging("tests/ltem/ltem_validation", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", ltem_config.get("ltem_verify_table_exists", []))
    def test_ltem_verify_table_exists(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/ltem/ltem_verify_table_exists")[0] == ExpectedShellResult
