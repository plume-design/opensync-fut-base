import concurrent.futures

import allure
import pytest

from framework.lib.fut_lib import read_md_description, step


@pytest.fixture(scope="module")
def pkim_check_supported(gw_handler):
    """Check if the PKI functionality is supported on the device."""
    with step("PKIM check supported"):
        if "PKIM" not in gw_handler.kconfig_managers:
            pytest.skip("PKIM not enabled on device, skipping test")
    yield


@pytest.fixture(scope="module")
def pkim_device_setup(gw_handler):
    """Configure fake persistent store using bind mounts on the target device."""
    with step("PKIM device setup"):
        assert gw_handler.execute_with_logging("tests/pkim/pkim_device_setup", "setup")[0] == 0

    yield

    with step("PKIM device cleanup"):
        assert gw_handler.execute_with_logging("tests/pkim/pkim_device_setup", "cleanup")[0] == 0


@allure.severity(allure.severity_level.NORMAL)
@allure.description(read_md_description("pkim_enroll"))
def test_pkim_enroll(pkim_check_supported, pkim_device_setup, server_handler, gw_handler):
    """Test regular enroll/re-enroll flow of the PKIM client."""
    with step("PKIM Enroll"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_enroll",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_enroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0

    with step("PKIM ReEnroll"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_reenroll",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_reenroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0


@allure.severity(allure.severity_level.NORMAL)
@allure.description(read_md_description("pkim_enroll_alt"))
def test_pkim_enroll_alt(pkim_check_supported, pkim_device_setup, server_handler, gw_handler):
    """Test enroll/re-enroll flow of an alternate certificate (label=fut)."""
    with step("PKIM Enroll Alt"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_enroll",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_enroll", "fut"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0

    with step("PKIM ReEnroll Alt"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_reenroll",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_reenroll", "fut"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0


@allure.severity(allure.severity_level.NORMAL)
@allure.description(read_md_description("pkim_enroll_overdue"))
def test_pkim_enroll_overdue(pkim_check_supported, pkim_device_setup, server_handler, gw_handler):
    """Test enroll/re-enroll flow of a certificate with short expiration dates."""
    with step("PKIM Enroll Overdue"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                ["--expire", "1", "test_enroll"],
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_enroll_overdue", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0

    with step("PKIM ReEnroll Overdue"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                ["--expire", "1", "test_reenroll"],
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_reenroll_overdue", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0


@allure.severity(allure.severity_level.NORMAL)
@allure.description(read_md_description("pkim_enroll_ra_int"))
def test_pkim_enroll_ra_int(pkim_check_supported, pkim_device_setup, server_handler, gw_handler):
    """Test enroll/re-enroll flow with a Retry-After header with an integer value."""
    with step("PKIM Enroll Retry-After (int)"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_enroll_ra_int",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_enroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0

    with step("PKIM ReEnroll Retry-After (int)"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_reenroll_ra_int",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_reenroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0


@allure.severity(allure.severity_level.NORMAL)
@allure.description(read_md_description("pkim_enroll_ra_str"))
def test_pkim_enroll_ra_str(pkim_check_supported, pkim_device_setup, server_handler, gw_handler):
    """Test enroll/re-enroll flow with a Retry-After header with an integer value."""
    with step("PKIM Enroll Retry-After (string)"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_enroll_ra_str",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_enroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0

    with step("PKIM ReEnroll Retry-After (string)"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            server = executor.submit(
                server_handler.execute,
                "tests/pkim/pkim_est_server",
                "test_reenroll_ra_str",
                suffix=".py",
            )
            device = executor.submit(
                gw_handler.execute_with_logging,
                "tests/pkim/pkim_fut",
                ["test_reenroll", "default"],
            )
            assert server.result()[0] == 0
            assert device.result()[0] == 0
