test_cfg = {
    "um_config": {
        "fw_name": "openwrt-os-PIRANHA2_QSDK53-ap-fit-3.2.2-55-g069aae5-dev-debug.img",
    },
    "um_corrupt_image": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_corrupt_md5_sum": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_download_image_while_downloading": [
        {
            "fw_dl_timer": 30,
            "test_script_timeout": 120,
        },
    ],
    "um_missing_md5_sum": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_set_firmware_url": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_set_invalid_firmware_pass": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_set_invalid_firmware_url": [
        {
            "test_script_timeout": 120,
        },
    ],
    "um_set_upgrade_dl_timer_abort": [
        {
            "fw_dl_timer": 5,
            "test_script_timeout": 20,
        },
    ],
    "um_set_upgrade_dl_timer_end": [
        {
            "fw_dl_timer": 100,
            "test_script_timeout": 120,
        },
    ],
    "um_set_upgrade_timer": [
        {
            "fw_up_timer": 10,
            "test_script_timeout": 120,
        },
    ],
    "um_verify_firmware_url_length": [
        {
            "url_max_length": 256,
        },
    ],
}
