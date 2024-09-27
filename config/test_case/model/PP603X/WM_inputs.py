from config.defaults import def_tx_power_set

# Note that def_tx_power_set is (1, 24)
tx_power_range_24g = (1, 20)
tx_power_range_5g = (1, 27)
tx_power_range_6g = (1, 23)
tx_power_set_24g = set(range(tx_power_range_24g[0], tx_power_range_24g[1] + 1))
tx_power_set_5g = set(range(tx_power_range_5g[0], tx_power_range_5g[1] + 1))
tx_power_set_6g = set(range(tx_power_range_6g[0], tx_power_range_6g[1] + 1))

test_inputs = {
    "wm2_set_radio_tx_power": {
        # To achive a smaller range than defaults, ignore additional ones. Anticipate adding encryption.
        "ignore": {
            "inputs": [[6, "HT40", "24g", tx_power, "WPA2"] for tx_power in def_tx_power_set - tx_power_set_24g]
            + [[5, "HT40", "6g", tx_power, "WPA3"] for tx_power in def_tx_power_set - tx_power_set_6g],
        },
        "inputs": [
            # To achive an extended range in addition to defaults, add more inputs here
            [44, "HT40", "5g", list(tx_power_set_5g - def_tx_power_set)],
        ],
    },
}
