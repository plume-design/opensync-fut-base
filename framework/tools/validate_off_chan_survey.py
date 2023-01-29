"""Module to determine if off-channel survey can be performed.

Performing the survey depends on the channel, HT mode and radio band
combination in relation to the device regulatory domain.
"""

from copy import deepcopy

import yaml

import framework.tools.logger

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


def check_channel_is_non_dfs(channel, ht_mode, radio_band, reg_domain):
    """Check if channel is a DFS channel or not.

    Uses regulatory file to determine the DFS channel list.
    Combines standard and weather channels to complete the list and searches
    for channel in the argument in the created list.

    Args:
        channel (int): Channel to be checked
        ht_mode (str): Used HT mode
        radio_band (str): Used radio band
        reg_domain (str): Used regulatory domain

    Returns:
        (bool): True if channel is not a DFS channel, False otherwise.
    """
    with open('config/rules/regulatory.yaml') as regulatory_file:
        loaded_regulatory_file = yaml.safe_load(regulatory_file)
        loaded_regulatory_file_cpy = deepcopy(loaded_regulatory_file)

    # Get the DFS channel list from the regulatory.yaml file
    dfs_standard_chan_list = loaded_regulatory_file_cpy[reg_domain]['dfs']['standard'][radio_band][ht_mode]
    dfs_weather_chan_list = loaded_regulatory_file_cpy[reg_domain]['dfs']['weather'][radio_band][ht_mode]
    # Merge both lists together.
    dfs_chan_list = dfs_standard_chan_list + dfs_weather_chan_list

    if channel in dfs_chan_list:
        log.warning(f'Invalid testcase config for non ETSI reg_domain: {reg_domain}')
        return False
    return True


def check_off_chan_scan_on_non_dfs_channel(channel, ht_mode, radio_band, reg_domain):
    """Determine if off-channel survey can be performed.

    Args:
        channel (int): Channel to be checked
        ht_mode (str): Used HT mode
        radio_band (str): Used radio band
        reg_domain (str): Used regulatory domain

    Returns:
        (bool): True if radio_band is '6g', reg_domain is 'EU' or 'GB', otherwise
                result of 'check_channel_is_non_dfs' function.
    """
    if radio_band == '6g':
        return True
    if reg_domain == 'EU' or reg_domain == 'GB':
        return True

    return check_channel_is_non_dfs(channel, ht_mode, radio_band, reg_domain)
