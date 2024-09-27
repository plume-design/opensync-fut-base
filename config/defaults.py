opensync_service_name = ["cm", "fcm", "fsm", "nm", "om", "owm", "pm", "qm", "sm", "um", "wano", "wm"]
opensync_service_kconfig = [f"CONFIG_MANAGER_{name.upper()}" for name in opensync_service_name]

all_encryption_types = ["open", "WPA2", "WPA3", "WPA3-transition"]

radio_band_list = ["24g", "5g", "5gl", "5gu", "6g"]
all_bandwidth_list = ["HT20", "HT40", "HT80", "HT160", "HT320"]
all_channels = {
    "24g": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "5g": [36, 40, 44, 48, 52, 56, 60, 64]
    + [100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]
    + [169, 173, 177, 181],
    "5gl": [36, 40, 44, 48, 52, 56, 60, 64],
    "5gu": [100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165],
    "6g": [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93]
    + [97, 101, 105, 109, 113]
    + [117, 121, 125, 129, 133, 137, 141, 145, 149, 153, 157, 161, 165, 169, 173, 177, 181, 185]
    + [189, 193, 197, 201, 205, 209, 213, 217, 221, 225, 229, 233],
}

def_tx_power_range = (1, 24)
def_tx_power_set = set(range(def_tx_power_range[0], def_tx_power_range[1] + 1))

def_bandwidth_list = ["HT40", "HT40", "HT40", "HT40", "HT40"]
def_channel_list = [6, 44, 44, 157, 5]
def_radio_type = ["2.4G", "5G", "5GL", "5GU", "6G"]
sm_radio_types = dict(zip(radio_band_list, def_radio_type))

def_wifi_args = ["channel", "ht_mode", "radio_band"]
def_wifi_inputs = [[ch, bw, rb] for ch, bw, rb in zip(def_channel_list, def_bandwidth_list, radio_band_list)]

all_pytest_flags = ["skip", "xfail"]

modifiers = ["gw", "leaf", "l1", "l2", "alt", "custom", "A", "B"]
radio_band_keywords = {f"{mod}_radio_band" for mod in modifiers} | {"radio_band"}
channel_keywords = {f"{mod}_channel" for mod in modifiers} | {"channel"}

# Unit test specific variables
unit_test_exec_name = "unit"
unit_test_resource_dir = "resource/ut"
unit_test_subdir = "utest"
