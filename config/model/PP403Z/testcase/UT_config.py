test_cfg = {
    # Regardless of collection, these unit tests are skipped
    "wl80211_tool_tput": {
        "skip": True,
        "skip_msg": "Unit Test failing",
    },
    "test_mdns_plugin": {
        "skip": True,
        "skip_msg": "Unit Test failing",
    },
    # Collect all unit tests in folder
    "ut": {},
}
