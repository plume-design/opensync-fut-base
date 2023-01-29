"""Module provides class and its methods to handle the testcase configuration."""

import framework.tools.logger
from framework.tools.functions import FailedException

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


class Config:
    """Config class."""

    def __init__(self, config):
        self.cfg = config

    def _get_recursive(self, value_path_split, cfg_dict, raise_exc=False):
        """Get value of the configuration key.

        Uses recursion.

        Args:
            value_path_split (str): Path to the configuration value
            cfg_dict (dict): Configuration dictionary
            raise_exc (bool, optional): Raise exception if value key is not found. Defaults to False.

        Raises:
            FailedException: Value key is not found.

        Returns:
            (str): Value of the configuration key if found, None otherwise.
        """
        key = value_path_split[0]

        if key not in cfg_dict:
            if raise_exc is True:
                raise FailedException('Key "{key}" not found in the configuration dictionary')
            else:
                log.debug(f'Key: {key} not found in the configuration file')
                return None
        elif cfg_dict[key] and isinstance(cfg_dict[key], type({})) and cfg_dict:
            value_path_split.pop(0)
            if value_path_split:
                return self._get_recursive(value_path_split, cfg_dict[key])
            else:
                return cfg_dict[key]
        else:
            return cfg_dict[key]

    def get(self, cfg_value_path, fallback=''):
        """Get value from configuration dictionary.

        If no value found, return fallback.

        Args:
            cfg_value_path (str): Path to the configuration value
            fallback (str, optional): Fallback of the requested value. Defaults to ''.

        Returns:
            (str): Configuration value if found, else fallback value.
        """
        value_path_split = cfg_value_path.split('.')
        if len(value_path_split) == 1 and value_path_split[0] in self.cfg:
            value = self.cfg[value_path_split[0]]
        else:
            value = self._get_recursive(value_path_split, self.cfg)

        if value is None:
            log.debug('Value not found in the configuration file, returning fallback value')
            return fallback
        else:
            return value

    def get_or_raise(self, cfg_value_path):
        """Get value from configuration dictionary with raise.

        If value key is not present, exception is raised in the called method.

        Args:
            cfg_value_path (str): Path to the configuration value

        Returns:
            (str): Configuration value.
        """
        value_path_split = cfg_value_path.split('.')
        return self._get_recursive(value_path_split, self.cfg, raise_exc=True)

    def set(self, key, value):
        """Set value for key to the configuration.

        Method works on one level of dictionary.

        Args:
            key (str): Configuration key
            value (str): Configuration value

        Returns:
            (bool): True, always.
        """
        self.cfg[key] = value
        return True
