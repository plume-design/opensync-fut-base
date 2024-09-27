import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
cpm_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def cpm_setup():
    test_class_name = ["TestCpm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for CPM: {nodes + clients}")
    for node in nodes:
        if not hasattr(pytest, node):
            raise RuntimeError(f"{node.upper()} handler is not set up correctly.")
        node_handler = getattr(pytest, node)
        if "CAPTIVEPORTAL" not in node_handler.get_kconfig_managers():
            pytest.skip("CPM not present on device")
        node_handler.fut_device_setup(test_suite_name="cpm")
        service_status = node_handler.get_node_services_and_status()
        if service_status["cpm"]["status"] != "enabled":
            node_handler.ovsdb.set_value(table="Node_Services", where="service==cpm", value={"status": "enabled"})
    # Set the baseline OpenSync PIDs used for reboot detection
    pytest.session_baseline_os_pids = pytest.gw.opensync_pid_retrieval(tracked_node_services=pytest.tracked_managers)


class TestCpm:
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cpm_config.get("cpm_default_listen_ip_port", []))
    def test_cpm_default_listen_ip_port(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cpm/cpm_default_listen_ip_port")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cpm_config.get("cpm_delete_while_restarting", []))
    def test_cpm_delete_while_restarting(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cpm/cpm_delete_while_restarting")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cpm_config.get("cpm_restart_crashed", []))
    def test_cpm_restart_crashed(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cpm/cpm_restart_crashed")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cpm_config.get("cpm_same_ip_port", []))
    def test_cpm_same_ip_port(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cpm/cpm_same_ip_port")[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", cpm_config.get("cpm_spawn_three_update_one", []))
    def test_cpm_spawn_three_update_one(self, cfg: dict):
        gw = pytest.gw

        with step("Test Case"):
            assert gw.execute_with_logging("tests/cpm/cpm_spawn_three_update_one")[0] == ExpectedShellResult
