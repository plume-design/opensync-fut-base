from config.defaults import (
    def_wifi_args,
    def_wifi_inputs,
)

tx_power_range_24g = (1, 24)
tx_power_range_5g = (1, 23)
tx_power_range_6g = (1, 20)
tx_power_list_24g = list(range(tx_power_range_24g[0], tx_power_range_24g[1] + 1))
tx_power_list_5g = list(range(tx_power_range_5g[0], tx_power_range_5g[1] + 1))
tx_power_list_6g = list(range(tx_power_range_6g[0], tx_power_range_6g[1] + 1))

test_inputs = {
    "wm2_set_radio_tx_power_pp603x": {
        "default": {"test_script_timeout": 20},
        "args_mapping": def_wifi_args[:] + ("tx_power",),
        "inputs": [
            item + [val]
            for item, val in zip(
                def_wifi_inputs[:],
                [tx_power_list_24g] + [tx_power_list_5g] * (len(def_wifi_inputs) - 2) + [tx_power_list_6g],
            )
        ],
        "expand_permutations": True,
        "override": "wm2_set_radio_tx_power",
    },
    "wm2_set_radio_thermal_tx_chainmask_pp603x": {
        "args_mapping": def_wifi_args[:] + ("tx_chainmask",),
        "inputs": [item + [val] for item, val in zip(def_wifi_inputs[:], [3, 240, 0, 0, 15])],
        "override": "wm2_set_radio_thermal_tx_chainmask",
    },
    "wm2_set_radio_tx_chainmask_pp603x": {
        "args_mapping": def_wifi_args[:] + ("tx_chainmask",),
        "inputs": [item + [val] for item, val in zip(def_wifi_inputs[:], [3, 240, 0, 0, 15])],
        "override": "wm2_set_radio_tx_chainmask",
    },
}
