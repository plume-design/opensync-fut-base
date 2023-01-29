"""Module containing FUT cloud class and methods."""

from pathlib import Path

import framework.tools.logger

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

CLOUD_LISTENER_LOG_FILE = "/tmp/cloud_listener.log"


class FutCloud:
    """FutCloud class used to simulate the actual cloud.

    FUT cloud simulation is needed to keep the FUT independent of the actual
    cloud and still be able to test certain things.
    Apart from the connection (running locally), no real services are simulated.
    """

    def __init__(
            self,
            server_handler=None,
    ):
        self.server_handler = server_handler
        # Initialize path to haproxy configuration file
        self.hap_path = f'{self.server_handler.fut_base_dir}/shell/tools/server/files/haproxy.cfg'
        # Initialize the path to cloud simulation script
        self.cloud_script = 'start_cloud_simulation.sh'
        self.cloud_script_path = f'{self.server_handler.fut_base_dir}/shell/tools/server/{self.cloud_script}'
        if not Path(self.hap_path).is_file():
            log.exception(f'Missing file {self.hap_path}')
        if not Path(self.cloud_script_path).is_file():
            log.exception(f'Missing file {self.cloud_script_path}')

    def change_tls_ver(self, tls_ver):
        """Change the FUT cloud TLS version.

        Version can be changed to one of:
        [10, 11, 12, '1.0', '1.1', '1.2'].

        Args:
            tls_ver (str): TLS version

        Returns:
            (bool): True if TLS version was changed, False otherwise.
        """
        log.info(f'Changing FUT Cloud TLS version to {tls_ver}')
        tls_ver = str(tls_ver).replace('.', '')
        tls_ver_exp = '.'.join(tls_ver)
        r_1 = 'ssl-default-bind-options force-tlsv.* ssl-max-ver TLSv.* ssl-min-ver TLSv.*'
        r_2 = 'ssl-default-server-options force-tlsv.* ssl-max-ver TLSv.* ssl-min-ver TLSv.*'

        s_0 = f'force-tlsv{tls_ver} ssl-max-ver TLSv{tls_ver_exp} ssl-min-ver TLSv{tls_ver_exp}'
        s_1 = f'ssl-default-bind-options {s_0}'
        s_2 = f'ssl-default-server-options {s_0}'

        r_1 = self.server_handler.execute(f"sed -i 's/{r_1}/{s_1}/g' {self.hap_path} && grep -q '{s_1}' {self.hap_path}", shell=True, print_out=True)
        r_2 = self.server_handler.execute(f"sed -i 's/{r_2}/{s_2}/g' {self.hap_path} && grep -q '{s_2}' {self.hap_path}", shell=True, print_out=True)

        if r_1 != 0 or r_2 != 0:
            log.warning('Failed to change FUT Cloud TLS version')
            return False
        log.info('FUT Cloud TLS version changed')
        return True

    @staticmethod
    def clear_log():
        """Clear the FUT cloud log file."""
        log.info(f'Clearing {CLOUD_LISTENER_LOG_FILE} file')
        if Path(CLOUD_LISTENER_LOG_FILE).is_file():
            open(CLOUD_LISTENER_LOG_FILE, 'w').close()
        return True

    def dump_log(self):
        """Dump contents of the FUT cloud log file.

        Returns log lines and clears the file if the file exists, returns
        information string otherwise.

        Returns:
            (str): Log
        """
        if Path(CLOUD_LISTENER_LOG_FILE).is_file():
            with open(CLOUD_LISTENER_LOG_FILE) as file:
                log_lines = file.readlines()
            self.clear_log()
            return ''.join(log_lines)
        else:
            return f'No {CLOUD_LISTENER_LOG_FILE} log file found!'

    def restart_cloud(self):
        """Restart FUT cloud simulation.

        Cloud simulation is restarted by executing the cloud script.
        Script is selected at instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is restarted, False otherwise.
        """
        log.info('Restarting FUT Cloud simulation')
        if self.server_handler.execute(f'{self.cloud_script_path} -r', print_out=True) != 0:
            log.warning('Could not restart FUT cloud simulation')
            return False
        log.info('FUT Cloud simulation restarted')
        return True

    def start_cloud(self):
        """Start FUT cloud simulation.

        Simulation is started by executing the cloud script.
        Script is selected at instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is started, False otherwise.
        """
        log.info('Starting FUT Cloud simulation')
        if self.server_handler.execute(self.cloud_script_path, print_out=True) != 0:
            log.warning('Couldn\'t start FUT cloud simulation')
            return False
        log.info('FUT Cloud simulation started')
        return True

    def stop_cloud(self):
        """Stop FUT cloud simulation.

        Cloud simulation is stopped by stopping the cloud script.
        Script is selected at instantiation of the class.

        Returns:
            (bool): True if FUT cloud simulation is stopped, False otherwise.
        """
        log.info('Stopping FUT Cloud simulation')
        if self.server_handler.execute(f'{self.cloud_script_path} -s', print_out=True) != 0:
            log.warning('Could not stop FUT cloud simulation')
            return False
        log.info('FUT Cloud simulation stopped')
        return True
