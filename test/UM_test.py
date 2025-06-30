import base64
import random
import string
from pathlib import Path

import pytest

from framework.handlers.server_handler import ServerHandler
from framework.lib.fut_lib import get_command_arguments, reboot_pods_and_wait_available, step
from lib_testbed.generic.util.logger import log


# Global FW name variable. Seto to the correct value during um_setup()
um_fw_name: str = ""


@pytest.fixture(scope="module")
def um_setup(request: pytest.FixtureRequest, full_test_config, server_handler):
    module_name = request.module.__name__.split(".")[1].split("_")[0]
    fixturenames = {fixturename for item in request.session.items for fixturename in item.fixturenames}
    with step(f"{module_name} module setup"):
        global um_fw_name
        um_fw_name = full_test_config["um_image"][0]["fw_name"]
        um_fw_md5_path = f"{server_handler.FUT_BASE_DIR}/resource/um/{um_fw_name}.md5"
        um_fw_path_local = f"{server_handler.FUT_BASE_DIR}/resource/um/{um_fw_name}"
        um_fw_path_remote = f"{server_handler.FUT_DIR}/resource/um/{um_fw_name}"

        if not Path(um_fw_path_local).is_file():
            pytest.skip(f"UM: test FW image is missing in {um_fw_path_local}, skipping test cases.")

        if not Path(um_fw_md5_path).is_file():
            # The um_fw_name should have been transferred during server setup
            assert server_handler.execute("tools/server/um/create_md5_file", um_fw_path_remote)[0] == 0

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
            fw_download_path = gw_handler.capabilities.get_fw_download_path()
            setup_args = get_command_arguments(fw_download_path)
            gw_handler.device_test_setup(test_suite_name=manager_name, setup_args=setup_args)
    yield


def _generate_image_key():
    """Generate image key used in UM (Upgrade Manager) testcases.

    Used when image key is not provided in testcase configuration.

    Returns:
        (str): FW image key
    """
    letters_and_digits = string.ascii_lowercase + string.digits + string.ascii_uppercase
    image_key_pure = "".join(random.choice(letters_and_digits) for _ in range(32))

    return str(base64.b64encode(image_key_pure.encode("ascii"))).replace("\"b'", "").replace("'", "")


def _get_um_fw_url(server: ServerHandler, prefix: str = ""):
    """Return URL to FW image file with optionally pre-pended prefix.

    Args:
        server (ServerHandler): Server handler object.
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        str: URL to FW image file.
    """
    curl_host = "http://fut.opensync.io:8000"
    um_fw_url = f"{curl_host}/{server.FUT_DIR}/resource/um/{prefix}{um_fw_name}"

    return um_fw_url


def _duplicate_image(server: ServerHandler, prefix: str = ""):
    """Create duplicated FW image file with optionally pre-pended prefix.

    Args:
        server (ServerHandler): Server handler object.
        prefix (str, optional): prefix to FW image file name. Defaults to "".

    Raises:
        OSError: If the duplicated image cannot be created.

    Returns:
        bool: Returns True if FW image file is created, False otherwise.
    """
    # Set file names for original image and for duplicated image
    um_fw_path = f"{server.FUT_DIR}/resource/um/{um_fw_name}"
    um_fw_prefix_path = f"{server.FUT_DIR}/resource/um/{prefix}{um_fw_name}"
    res = server.run_raw(f"cp -r {um_fw_path} {um_fw_prefix_path}")
    if res[0] != 0:
        raise OSError(f"Unable to duplicate image.\n{res[1]}\n{res[2]}")
    return True


def _remove_duplicate_image(server: ServerHandler, prefix: str = ""):
    """Remove duplicated FW image file with optionally pre-pended prefix.

    Args:
        server (ServerHandler): Server handler object.
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        bool: Returns True if FW image file is removed, False otherwise.
    """
    um_fw_prefix_path = f"{server.FUT_DIR}/resource/um/{prefix}{um_fw_name}"
    res = server.run_raw(f"rm -f {um_fw_prefix_path}")
    if res[0] != 0:
        log.warning(msg=f"Unable to remove duplicated image.\n{res[1]}\n{res[2]}")
    return True


def _get_um_fw_path(fut_dir: str, prefix: str = ""):
    """Return path to FW image file with optionally pre-pended prefix.

    Args:
        fut_dir (str): FUT directory where FW image file is located.
        prefix (str, optional): prefix to FW image file name. Defaults to ''.

    Returns:
        str: Path to FW image file.
    """
    um_fw_path = f"{fut_dir}/resource/um/{prefix}{um_fw_name}"

    return um_fw_path


def test_um_corrupt_image(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Create corrupted image and MD5 files"):
        assert (
            server_handler.execute(
                "tools/server/um/create_corrupt_image_file",
                _get_um_fw_path(fut_dir=server_handler.FUT_DIR),
            )[0]
            == 0
        )
        assert (
            server_handler.execute(
                "tools/server/um/create_md5_file",
                _get_um_fw_path(fut_dir=server_handler.FUT_DIR, prefix="corrupt_"),
            )[0]
            == 0
        )
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler, prefix="corrupt_"),
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_corrupt_image", test_args)[0] == 0


def test_um_corrupt_md5_sum(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Create corrupted MD5sum file and FW image file"):
        md5_fw_prefix = "corrupt_md5_sum_"
        assert _duplicate_image(server=server_handler, prefix=md5_fw_prefix)
        assert (
            server_handler.execute(
                "tools/server/um/create_corrupt_md5_file",
                _get_um_fw_path(fut_dir=server_handler.FUT_DIR, prefix=md5_fw_prefix),
            )[0]
            == 0
        )
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler, prefix=md5_fw_prefix),
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_corrupt_md5_sum", test_args)[0] == 0
    with step("Cleanup"):
        assert _remove_duplicate_image(server=server_handler, prefix=md5_fw_prefix)


def test_um_download_image_while_downloading(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Create duplicate testcase image"):
        copied_prefix = "copied_"
        _duplicate_image(server=server_handler, prefix=copied_prefix)
        assert (
            server_handler.execute(
                "tools/server/um/create_md5_file",
                _get_um_fw_path(fut_dir=server_handler.FUT_DIR, prefix=copied_prefix),
            )[0]
            == 0
        )
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        um_fw_url = _get_um_fw_url(server=server_handler)
        copied_um_fw_url = _get_um_fw_url(server=server_handler, prefix=copied_prefix)
        fw_dl_timer = parametrized_test_config.get("fw_dl_timer")
        test_args = get_command_arguments(
            fw_path,
            um_fw_url,
            copied_um_fw_url,
            fw_dl_timer,
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_download_image_while_downloading", test_args)[0] == 0
    with step("Cleanup"):
        assert _remove_duplicate_image(server=server_handler, prefix=copied_prefix)


def test_um_missing_md5_sum(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())

        # Constant arguments
        md5_fw_prefix = "missing_md5_sum_"

        assert _duplicate_image(server=server_handler, prefix=md5_fw_prefix)
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler, prefix=md5_fw_prefix),
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_missing_md5_sum", test_args)[0] == 0
    with step("Cleanup"):
        assert _remove_duplicate_image(server=server_handler, prefix=md5_fw_prefix)


def test_um_set_firmware_url(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Get UM firmware URL"):
        um_fw_url = _get_um_fw_url(server=server_handler)

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        test_args = get_command_arguments(
            fw_path,
            um_fw_url,
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_set_firmware_url", test_args)[0] == 0


def test_um_set_invalid_firmware_pass(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Generate invalid FW password"):
        fw_pass = (
            _generate_image_key()
            if "fw_pass" not in parametrized_test_config
            else parametrized_test_config.get("fw_pass")
        )

    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler),
            fw_pass,
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_set_invalid_firmware_pass", test_args)[0] == 0


def test_um_set_invalid_firmware_url(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler, prefix="non_existing_fw_url_"),
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_set_invalid_firmware_url", test_args)[0] == 0


def test_um_set_upgrade_dl_timer_end(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        fw_dl_timer = parametrized_test_config.get("fw_dl_timer")
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler),
            fw_dl_timer,
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_set_upgrade_dl_timer_end", test_args)[0] == 0


def test_um_set_upgrade_timer(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        fw_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())
        fw_up_timer = parametrized_test_config.get("fw_up_timer")
        test_args = get_command_arguments(
            fw_path,
            _get_um_fw_url(server=server_handler),
            fw_up_timer,
            um_fw_name,
        )
    with step("Test case"):
        assert gw_handler.execute("tests/um/um_set_upgrade_timer", test_args)[0] == 0


def test_um_verify_firmware_url_length(um_setup, parametrized_test_config, server_handler, gw_handler):
    with step("Preparation of testcase parameters"):
        # Arguments from test case configuration
        url_max_length = parametrized_test_config.get("url_max_length")
        fw_download_path = parametrized_test_config.get("fw_path", gw_handler.capabilities.get_fw_download_path())

        # Constant arguments
        firmware_url_base = "http://fut.opensync.io:8000/fut-base/resource/um/"
        firmware_url_suffix = ".img"
        url_mid_length = url_max_length - len(firmware_url_base) - len(firmware_url_suffix)
        # Make sure there is space for middle part of URL
        assert url_mid_length > 0
        # Create middle part of the URL from random characters and insert it in FW URL
        firmware_url_mid = "".join(
            random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=url_mid_length),
        )
        firmware_url = f"{firmware_url_base}{firmware_url_mid}{firmware_url_suffix}"
        # Make sure total length of firmware URL is exactly max length
        assert len(firmware_url) == url_max_length

        test_args = get_command_arguments(
            fw_download_path,
            firmware_url,
        )

    with step("Test case"):
        assert gw_handler.execute("tests/um/um_verify_firmware_url_length", test_args)[0] == 0
