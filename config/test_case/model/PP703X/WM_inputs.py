from config.defaults import (
    def_tx_power_set,
    def_wifi_args,
    def_wifi_inputs,
)

tx_power_list = list(def_tx_power_set)
tx_power_range_6g = (1, 13)
tx_power_list_6g = list(range(tx_power_range_6g[0], tx_power_range_6g[1] + 1))

test_inputs = {
    "wm2_set_radio_tx_power_pp703x": {
        "default": {"test_script_timeout": 20},
        "args_mapping": def_wifi_args[:] + ("tx_power",),
        "inputs": [
            item + [val]
            for item, val in zip(def_wifi_inputs[:], [tx_power_list] * (len(def_wifi_inputs) - 1) + [tx_power_list_6g])
        ],
        "expand_permutations": True,
        "override": "wm2_set_radio_tx_power",
    },
}
