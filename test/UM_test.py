import base64
import random
import string
from pathlib import Path

import allure
import pytest

from framework.fut_configurator import FutConfigurator
from framework.lib.fut_lib import determine_required_devices, step
from lib_testbed.generic.util.logger import log


ExpectedShellResult = pytest.expected_shell_result
pytest.fut_configurator = FutConfigurator()
um_config = pytest.fut_configurator.get_test_config()


@pytest.fixture(scope="class", autouse=True)
def um_setup():
    test_class_name = ["TestUm"]
    nodes, clients = determine_required_devices(test_class_name)
    log.info(f"Required devices for UM: {nodes + clients}")
    try:
        server = pytest.server
        um_fw_name = um_config["um_image"][0]["fw_name"]
        um_fw_md5_path = f"{server.fut_base_dir}/resource/um/{um_fw_name}.md5"
        um_fw_path_local = f"{server.fut_base_dir}/resource/um/{um_fw_name}"
        um_fw_path_remote = f"{server.fut_dir}/resource/um/{um_fw_name}"
        if not Path(um_fw_path_local).is_file():
            pytest.skip(f"UM test FW image is missing in {um_fw_path_local}. Skipping UM test cases.")
        if not Path(um_fw_md5_path).is_file():
            # The um_fw_name should have been transferred during server setup
            assert server.execute("tools/server/um/create_md5_file", um_fw_path_remote)[0] == ExpectedShellResult
    except Exception as exception:
        raise RuntimeError(f"Unable to perform setup for the server device: {exception}")
    for device in nodes:
        if not hasattr(pytest, device):
            raise RuntimeError(f"{device.upper()} handler is not set up correctly.")
        try:
            device_handler = getattr(pytest, device)
            primary_wan_iface = device_handler.capabilities.get_primary_wan_iface()
            fw_download_path = device_handler.capabilities.get_fw_download_path()
            setup_args = device_handler.get_command_arguments(fw_download_path, primary_wan_iface)
            device_handler.fut_device_setup(test_suite_name="um", setup_args=setup_args)
        except Exception as exception:
            raise RuntimeError(f"Unable to perform setup for the {device} device: {exception}")


class TestUm:
    @staticmethod
    def generate_image_key():
        """Generate image key used in UM (Upgrade Manager) testcases.

        Used when image key is not provided in testcase configuration.

        Returns:
            (str): FW image key
        """
        letters_and_digits = string.ascii_lowercase + string.digits + string.ascii_uppercase
        image_key_pure = "".join(random.choice(letters_and_digits) for i in range(32))

        return str(base64.b64encode(image_key_pure.encode("ascii"))).replace("\"b'", "").replace("'", "")

    @staticmethod
    def get_um_fw_url(prefix=""):
        """Return URL to FW image file with optionally pre-pended prefix.

        Args:
            prefix (str, optional): prefix to FW image file name. Defaults to ''.

        Returns:
            str: URL to FW image file.
        """
        um_fw_name = um_config["um_image"][0]["fw_name"]
        curl_host = f"http://{pytest.fut_configurator.fut_test_hostname}:{pytest.fut_configurator.curl_port_rate_limit}"
        um_fw_url = f"{curl_host}/{pytest.server.fut_dir}/resource/um/{prefix}{um_fw_name}"

        return um_fw_url

    @staticmethod
    def duplicate_image(prefix=""):
        """Create duplicated FW image file with optionally pre-pended prefix.

        Args:
            prefix (str, optional): prefix to FW image file name. Defaults to "".

        Raises:
            RuntimeError: If the duplicated image cannot be created.

        Returns:
            bool: Returns True if FW image file is created, False otherwise.
        """
        server = pytest.server
        um_fw_name = um_config["um_image"][0]["fw_name"]
        # Set file names for original iamge and for duplicated image
        um_fw_path = f"{server.fut_dir}/resource/um/{um_fw_name}"
        um_fw_prefix_path = f"{server.fut_dir}/resource/um/{prefix}{um_fw_name}"
        try:
            res = server.device_api.run_raw(f"cp -r {um_fw_path} {um_fw_prefix_path}")
            if res[0] != 0:
                raise RuntimeError(f"Error creating duplicated image.\n{res[1]}\n{res[2]}")
        except Exception as exception:
            log.info(f"Encountered an exception while creating a duplicated image: {exception}")
            return False
        return True

    @staticmethod
    def remove_duplicate_image(prefix=""):
        """Remove duplicated FW image file with optionally pre-pended prefix.

        Args:
            prefix (str, optional): prefix to FW image file name. Defaults to ''.

        Returns:
            bool: Returns True if FW image file is removed, False otherwise.
        """
        server = pytest.server
        um_fw_name = um_config["um_image"][0]["fw_name"]
        um_fw_prefix_path = f"{server.fut_dir}/resource/um/{prefix}{um_fw_name}"
        res = server.device_api.run_raw(f"rm -f {um_fw_prefix_path}")
        if res[0] != 0:
            log.warning(msg=f"Unable to remove duplicated image.\n{res[1]}\n{res[2]}")
        return True

    @staticmethod
    def get_um_fw_path(prefix=""):
        """Return path to FW image file with optionally pre-pended prefix.

        Args:
            prefix (str, optional): prefix to FW image file name. Defaults to ''.

        Returns:
            str: Path to FW image file.
        """
        server = pytest.server
        um_fw_name = um_config["um_image"][0]["fw_name"]
        um_fw_path = f"{server.fut_dir}/resource/um/{prefix}{um_fw_name}"

        return um_fw_path

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_corrupt_image", []))
    def test_um_corrupt_image(self, cfg):
        server, gw = pytest.server, pytest.gw

        with step("Create corrupted image and MD5 files"):
            assert (
                server.execute("tools/server/um/create_corrupt_image_file", self.get_um_fw_path())[0]
                == ExpectedShellResult
            )
            assert (
                server.execute("tools/server/um/create_md5_file", self.get_um_fw_path(prefix="corrupt_"))[0]
                == ExpectedShellResult
            )
        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(prefix="corrupt_"),
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_corrupt_image", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_corrupt_md5_sum", []))
    def test_um_corrupt_md5_sum(self, cfg):
        server, gw = pytest.server, pytest.gw

        with step("Create corrupted MD5sum file and FW image file"):
            md5_fw_prefix = "corrupt_md5_sum_"
            assert self.duplicate_image(prefix=md5_fw_prefix)
            assert (
                server.execute("tools/server/um/create_corrupt_md5_file", self.get_um_fw_path(prefix=md5_fw_prefix))[0]
                == ExpectedShellResult
            )
        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(prefix=md5_fw_prefix),
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_corrupt_md5_sum", test_args)[0] == ExpectedShellResult
        with step("Cleanup"):
            assert self.remove_duplicate_image(prefix=md5_fw_prefix)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_download_image_while_downloading", []))
    def test_um_download_image_while_downloading(self, cfg):
        server, gw = pytest.server, pytest.gw

        with step("Create duplicate testcase image"):
            copied_prefix = "copied_"
            self.duplicate_image(prefix=copied_prefix)
            assert (
                server.execute("tools/server/um/create_md5_file", self.get_um_fw_path(prefix=copied_prefix))[0]
                == ExpectedShellResult
            )
        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            um_fw_url = self.get_um_fw_url()
            copied_um_fw_url = self.get_um_fw_url(prefix=copied_prefix)
            fw_dl_timer = cfg.get("fw_dl_timer")
            test_args = gw.get_command_arguments(
                fw_path,
                um_fw_url,
                copied_um_fw_url,
                fw_dl_timer,
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_download_image_while_downloading", test_args)[0] == ExpectedShellResult
        with step("Cleanup"):
            assert self.remove_duplicate_image(prefix=copied_prefix)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_missing_md5_sum", []))
    def test_um_missing_md5_sum(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())

            # Constant arguments
            md5_fw_prefix = "missing_md5_sum_"

            assert self.duplicate_image(prefix=md5_fw_prefix)
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(prefix=md5_fw_prefix),
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_missing_md5_sum", test_args)[0] == ExpectedShellResult
        with step("Cleanup"):
            assert self.remove_duplicate_image(prefix=md5_fw_prefix)

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_set_firmware_url", []))
    def test_um_set_firmware_url(self, cfg):
        gw = pytest.gw

        with step("Get UM firmware URL"):
            um_fw_url = self.get_um_fw_url()

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            test_args = gw.get_command_arguments(
                fw_path,
                um_fw_url,
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_set_firmware_url", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_set_invalid_firmware_pass", []))
    def test_um_set_invalid_firmware_pass(self, cfg):
        gw = pytest.gw

        with step("Generate invalid FW password"):
            fw_pass = self.generate_image_key() if "fw_pass" not in cfg else cfg.get("fw_pass")

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(),
                fw_pass,
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_set_invalid_firmware_pass", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_set_invalid_firmware_url", []))
    def test_um_set_invalid_firmware_url(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(prefix="non_existing_fw_url_"),
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_set_invalid_firmware_url", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_set_upgrade_dl_timer_end", []))
    def test_um_set_upgrade_dl_timer_end(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            fw_dl_timer = cfg.get("fw_dl_timer")
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(),
                fw_dl_timer,
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_set_upgrade_dl_timer_end", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_set_upgrade_timer", []))
    def test_um_set_upgrade_timer(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            fw_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())
            fw_up_timer = cfg.get("fw_up_timer")
            fw_name = um_config["um_image"][0]["fw_name"]
            test_args = gw.get_command_arguments(
                fw_path,
                self.get_um_fw_url(),
                fw_up_timer,
                fw_name,
            )
        with step("Test case"):
            assert gw.execute("tests/um/um_set_upgrade_timer", test_args)[0] == ExpectedShellResult

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("cfg", um_config.get("um_verify_firmware_url_length", []))
    def test_um_verify_firmware_url_length(self, cfg):
        gw = pytest.gw

        with step("Preparation of testcase parameters"):
            # Arguments from test case configuration
            url_max_length = cfg.get("url_max_length")
            fw_download_path = cfg.get("fw_path", gw.capabilities.get_fw_download_path())

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

            test_args = gw.get_command_arguments(
                fw_download_path,
                firmware_url,
            )

        with step("Test case"):
            assert gw.execute("tests/um/um_verify_firmware_url_length", test_args)[0] == ExpectedShellResult
