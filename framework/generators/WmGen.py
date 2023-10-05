from itertools import product

from framework.lib.fut_lib import validate_channel_ht_mode_band


class WmGen:
    def __init__(self):
        self.suggested_channels_map = {
            "24g": [1, 6, 11],
            "5g": [44, 157],
            "5gl": [44, 60],
            "5gu": [108, 124, 140, 157],
            "6g": [5, 21, 37, 53, 69, 85, 101, 117, 133, 149, 165, 181, 197, 213],
        }
        self.minimal_channels_map = {
            "24g": [6],
            "5g": [44, 157],
            "5gl": [44],
            "5gu": [157],
            "6g": [5, 149],
        }

    def _filter_supported_channels(self, channels, radio_band, ht_mode="HT20"):
        tmp_channels = []
        supported_channels = self.gw_capabilities.get(f"interfaces.radio_channels.{radio_band}")
        if not isinstance(channels, list):
            channels = [channels]
        for ch in channels:
            if ch in supported_channels and validate_channel_ht_mode_band(
                ch,
                radio_band=radio_band,
                ht_mode=ht_mode,
                reg_domain=self.regulatory_domain,
                regulatory_rule=self.regulatory_rule,
            ):
                tmp_channels.append(ch)
        return tmp_channels

    @staticmethod
    def _get_ht_modes(max_ht_mode):
        modes = []
        for i in [20, 40, 80, 160]:
            if i <= max_ht_mode:
                modes.append(f"HT{i}")
        return modes

    @staticmethod
    def _generate_permutations(input_list):
        """
        Generate permutations.

        Attempts to generate permutations by replacing elements in the
        input list, that contains a nested list, with values from that
        nested list.

        Example:
            input:
                [6, "HT40", "24g", [36, 123]]
            output:
                [6, "HT40", "24g", 36]
                [6, "HT40", "24g", 123]

        Args:
            input_list (list): Input list.
        """
        list_position = [item for item in input_list if isinstance(item, list)]
        for p in product(*list_position):
            iterator = iter(p)
            yield [output if not isinstance(output, list) else next(iterator) for output in input_list]

    def gen_wm2_set_bcn_int(self, inputs):
        tmp_inputs = []
        radio_channels_band = self.gw_capabilities.get("interfaces.radio_channels")
        bcn_interval_list = [100, 200, 400]
        ht_mode = "HT40"
        for radio_band, channels in radio_channels_band.items():
            if not isinstance(channels, list):
                continue
            channels = self.minimal_channels_map[radio_band]
            channels = self._filter_supported_channels(channels, radio_band, ht_mode)
            if not channels:
                continue
            for channel in channels:
                for bcn_interval in bcn_interval_list:
                    tmp_cfg = {
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "radio_band": radio_band,
                        "bcn_int": bcn_interval,
                    }
                    tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def gen_wm2_set_channel(self, inputs):
        tmp_inputs = []
        radio_channels_band = self.gw_capabilities.get("interfaces.radio_channels")
        ht_mode = "HT40"
        for radio_band, channels in radio_channels_band.items():
            if not isinstance(channels, list):
                continue
            channels = self.minimal_channels_map[radio_band]
            channels = self._filter_supported_channels(channels, radio_band, ht_mode)
            if not channels:
                continue
            encryption = "WPA2" if radio_band != "6g" else "WPA3"
            for channel in channels:
                tmp_cfg = {
                    "channel": channel,
                    "ht_mode": ht_mode,
                    "radio_band": radio_band,
                    "encryption": encryption,
                }
                tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def gen_wm2_set_ht_mode(self, inputs):
        tmp_inputs = []
        radio_channels_band = self.gw_capabilities.get("interfaces.radio_channels")
        for radio_band, channels in radio_channels_band.items():
            if not isinstance(channels, list):
                continue
            max_ht_mode = int(self.gw_capabilities.get(f"interfaces.max_channel_width.{radio_band}"))
            for ht_mode in self._get_ht_modes(max_ht_mode):
                channels = self.minimal_channels_map[radio_band]
                channels = self._filter_supported_channels(channels, radio_band, ht_mode=ht_mode)
                if not channels:
                    continue
                encryption = "WPA2" if radio_band != "6g" else "WPA3"
                for channel in channels:
                    tmp_cfg = {
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "radio_band": radio_band,
                        "encryption": encryption,
                    }
                    tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def gen_wm2_ht_mode_and_channel_iteration(self, inputs):
        # Configuration is automatically generated based on device capabilities
        # For each supported radio_band and each ht_mode (until defined max_channel_width) for ALL supported channels
        tmp_inputs = []
        radio_channels_band = self.gw_capabilities.get("interfaces.radio_channels")
        for radio_band, channels in radio_channels_band.items():
            if not isinstance(channels, list):
                continue
            if radio_band == "6g":
                channels = self.suggested_channels_map["6g"]
            for channel in channels:
                max_ht_mode = int(self.gw_capabilities.get(f"interfaces.max_channel_width.{radio_band}"))
                for ht_mode in self._get_ht_modes(max_ht_mode):
                    if not validate_channel_ht_mode_band(
                        channel=channel,
                        ht_mode=ht_mode,
                        radio_band=radio_band,
                        reg_domain=self.regulatory_domain,
                        regulatory_rule=self.regulatory_rule,
                    ):
                        continue
                    encryption = "WPA2" if radio_band != "6g" else "WPA3"
                    tmp_cfg = {
                        "channel": channel,
                        "ht_mode": ht_mode,
                        "radio_band": radio_band,
                        "encryption": encryption,
                    }
                    tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def _parse_wm_inputs(self, inputs):
        tmp_inputs = []
        if "args_mapping" in inputs:
            tmp_inputs = []
            for i in inputs["inputs"]:
                if "gw_radio_band" in inputs["args_mapping"]:
                    gw_radio_band_index = inputs["args_mapping"].index("gw_radio_band")
                    if not self._check_band_compatible(i[gw_radio_band_index], "gw"):
                        continue
                if "leaf_radio_band" in inputs["args_mapping"]:
                    leaf_radio_band_index = inputs["args_mapping"].index("leaf_radio_band")
                    if not self._check_band_compatible(i[leaf_radio_band_index], "leaf"):
                        continue
                if "gw_channel" in inputs["args_mapping"] and (
                    "gw_radio_band" in inputs["args_mapping"] or "radio_band" in inputs["args_mapping"]
                ):
                    if "gw_radio_band" in inputs["args_mapping"]:
                        radio_band_index = inputs["args_mapping"].index("gw_radio_band")
                    else:
                        radio_band_index = inputs["args_mapping"].index("radio_band")
                    gw_channel_index = inputs["args_mapping"].index("gw_channel")
                    if not self._check_band_channel_compatible(i[radio_band_index], i[gw_channel_index], "gw"):
                        continue

                if "leaf_channel" in inputs["args_mapping"] and (
                    "leaf_radio_band" in inputs["args_mapping"] or "radio_band" in inputs["args_mapping"]
                ):
                    if "leaf_radio_band" in inputs["args_mapping"]:
                        radio_band_index = inputs["args_mapping"].index("leaf_radio_band")
                    else:
                        radio_band_index = inputs["args_mapping"].index("radio_band")
                    leaf_channel_index = inputs["args_mapping"].index("leaf_channel")
                    if not self._check_band_channel_compatible(i[radio_band_index], i[leaf_channel_index], "leaf"):
                        continue
                tmp_inputs.append(i)
        inputs["inputs"] = tmp_inputs
        return inputs

    def gen_wm2_topology_change_change_parent_change_band_change_channel(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_topology_change_change_parent_same_band_change_channel(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_connect_wpa3_client(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_connect_wpa3_leaf(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_set_ht_mode_neg(self, inputs):
        tmp_inputs = []
        for i in inputs["inputs"]:
            radio_band_index = inputs["args_mapping"].index("radio_band")
            radio_band = i[radio_band_index]
            band = self.gw_capabilities.get(f"interfaces.max_channel_width.{radio_band}")
            if not band:
                continue
            max_ht_mode = int(band)
            if max_ht_mode < 160:
                tmp_inputs.append(i)
        inputs["inputs"] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_create_wpa3_ap(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_set_channel_neg(self, inputs):
        tmp_inputs = []
        for i in inputs["inputs"]:
            for permutation in self._generate_permutations(i):
                tmp_inputs.append(permutation)
        inputs["inputs"] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_set_radio_tx_power(self, inputs):
        tmp_inputs = []
        for i in inputs["inputs"]:
            tx_power_index = inputs["args_mapping"].index("tx_power")
            i[tx_power_index] = list(range(i[tx_power_index][0], i[tx_power_index][1] + 1))
            for permutation in self._generate_permutations(i):
                tmp_inputs.append(permutation)
        inputs["inputs"] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_set_ssid(self, inputs):
        tmp_inputs = []
        for i in inputs["inputs"]:
            for permutation in self._generate_permutations(i):
                tmp_inputs.append(permutation)
        inputs["inputs"] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_verify_wifi_security_modes(self, inputs):
        tmp_inputs = []
        for i in inputs["inputs"]:
            for permutation in self._generate_permutations(i):
                tmp_inputs.append(permutation)
        inputs["inputs"] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)
