from config.defaults import def_tx_power_set, def_wifi_inputs

tx_power_range = (1, 30)
tx_power_set = set(range(tx_power_range[0], tx_power_range[1] + 1))

test_inputs = {
    "wm2_set_radio_tx_power": {
        "inputs": [sublist + [list(tx_power_set - def_tx_power_set)] for sublist in def_wifi_inputs],
    },
}
