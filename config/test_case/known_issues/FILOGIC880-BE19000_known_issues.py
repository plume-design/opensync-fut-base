# Common variables
dm_verify_remote_triggered_reboot = {"known_issues": {"msg": "Remote triggered reboot did not occur."}}
nm2_set_gateway = {"known_issues": {"msg": "Gateway setting is not removed from Wifi_Inet_State table."}}
sm_neighbor_report = {"known_issues": {"msg": "MQTT messages are missing neighbor reports."}}
um_all_tests = {"known_issues": {"msg": "UM is not supported for this version"}}
wm2_dfs_cac_aborted = {"known_issues": {"msg": "CAC is not aborted when channel is changed during CAC."}}

known_issues = {
    "6.6.0.1": {
        "dm_verify_remote_triggered_reboot": dm_verify_remote_triggered_reboot,
        "nm2_set_gateway": nm2_set_gateway,
        "sm_neighbor_report": sm_neighbor_report,
        "um_corrupt_md5_sum": um_all_tests,
        "um_download_image_while_downloading": um_all_tests,
        "um_missing_md5_sum": um_all_tests,
        "um_set_firmware_url": um_all_tests,
        "um_set_invalid_firmware_pass": um_all_tests,
        "um_set_invalid_firmware_url": um_all_tests,
        "um_set_upgrade_dl_timer_end": um_all_tests,
        "um_set_upgrade_timer": um_all_tests,
        "wm2_dfs_cac_aborted": wm2_dfs_cac_aborted,
    },
}
