from pathlib import Path

from framework.lib.fut_lib import allure_script_execution_post_processing
from lib_testbed.generic.client.models.generic.client_api import ClientApi


class ClientHandler(ClientApi):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.FUT_BASE_DIR = Path(__file__).absolute().parents[2].as_posix()
        self.FUT_DIR = "/tmp/fut-base"
        self.TEST_SCRIPT_TIMEOUT = 180
        self.transfer_folders = ["shell"]
        self.transfers = list(zip(self.transfer_folders, self.transfer_folders))

    def _run_raw(self, path, args="", as_sudo=False, **kwargs):
        ext = ".sh" if "suffix" not in kwargs else kwargs["suffix"]
        folder = "shell" if "folder" not in kwargs else kwargs["folder"]

        if isinstance(args, list):
            args = " ".join(args)

        cmd = f"{self.FUT_DIR}/{folder}/{path}{ext} {args}"

        if ext == ".py":
            cmd = f"python3 -u {cmd}"

        if as_sudo:
            cmd = f"sudo {cmd}"

        timeout = self.TEST_SCRIPT_TIMEOUT if "timeout" not in kwargs else kwargs["timeout"]
        cmd_res = self.run_raw(cmd, timeout=timeout)

        cmd_ec = cmd_res[0]
        cmd_std_out = "" if not cmd_res[1] else cmd_res[1]
        cmd_std_err = "" if not cmd_res[2] else cmd_res[2]

        return cmd_ec, cmd_std_out, cmd_std_err

    def create_fut_set_env(self) -> str:
        """
        Create file containing shell environment variables.

        Name of the file is hardcoded to 'fut_set_env.sh'.

        Returns:
            (str): Path to shell environment variable file.
        """
        client_config = {
            "FUT_TOPDIR": "/tmp/fut-base",
            "SHELL": "/bin/bash",
        }

        shell_fut_env_path = f"{self.FUT_BASE_DIR}/fut_set_env.sh"
        shell_fut_env_file = open(shell_fut_env_path, "w")

        for key, value in client_config.items():
            ini_line = f'{key}="{value}"\n'
            shell_fut_env_file.write(ini_line)

        shell_fut_env_file.write('echo "${FUT_TOPDIR}/fut_set_env.sh sourced"\n')
        shell_fut_env_file.close()

        return shell_fut_env_path

    @allure_script_execution_post_processing
    def execute(self, path: str, args: str = "", as_sudo: bool = False, **kwargs) -> tuple[int, str, str]:
        """
        Execute the specified script with optional arguments.

        Args:
            path (str): Path to script.
            args (str): Optional script arguments. Defaults to empty
                string.
            as_sudo (bool): Execute script with superuser privileges.
        Keyword Args:
            suffix (str): Suffix of the script
            folder (str): Name of the folder where the script is located
        Returns:
            (list): List comprising the exit code, standard output and standard error
        """
        cmd_ec, cmd_std_out, cmd_std_err = self._run_raw(path, args, as_sudo, **kwargs)
        return cmd_ec, cmd_std_out, cmd_std_err

    def create_and_transfer_fut_env_file(self):
        env_file = self.create_fut_set_env()
        self.put_file(file_name=env_file, location=self.FUT_DIR)
