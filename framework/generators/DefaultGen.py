import importlib.util
import sys
from itertools import product
from pathlib import Path

from config.defaults import all_pytest_flags, channel_keywords, radio_band_keywords, radio_band_list
from framework.lib.fut_lib import load_reg_rule, validate_channel_ht_mode_band
from lib_testbed.generic.pod.generic.pod_api import PodApi
from lib_testbed.generic.util.logger import log

fut_base_dir = Path(__file__).absolute().parents[2].as_posix()
sys.path.append(fut_base_dir)

generator_modules = []
generator_dir = "framework/generators"
generator_mod = generator_dir.replace("/", ".")
generator_names = [
    filename.stem
    for filename in Path(__file__).parent.absolute().iterdir()
    if "Gen.py" in filename.name and "Template" not in filename.name and "DefaultGen" not in filename.name
]
for generator_name in generator_names:
    spec = importlib.util.find_spec(f"{generator_mod}.{generator_name}")
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Shallow-merge new module over existing dictionary
        generator_modules.append(module.__getattribute__(generator_name)())


class DefaultGenClass:
    def __init__(self, gw: "PodApi", leaf: "PodApi"):
        self.gw = gw
        self.leaf = leaf
        self.regulatory_domain = self.gw.capabilities.get_regulatory_domain()
        self.regulatory_rule = load_reg_rule()
        attributes_to_add = []
        for gen_key in dir(self):
            if not gen_key.startswith("__") and not gen_key.endswith("__"):
                attributes_to_add.append(gen_key)

        for generator_module in generator_modules:
            for gen_key in dir(generator_module):
                if not gen_key.startswith("__") and not gen_key.endswith("__"):
                    self.__setattr__(gen_key, getattr(generator_module, gen_key))
            for add_attr in attributes_to_add:
                setattr(generator_module.__class__, add_attr, self.__getattribute__(add_attr))

    def _check_unii_4_capable(self) -> bool:
        """Check if the gw device capabilities file supports the 5g or 5gu channels needed for UNII-4 support."""
        # try to get self.unii_4_capable if exists, else continue with the function
        if hasattr(self, "unii_4_capable"):
            return self.unii_4_capable
        for radio_band in ["5g", "5gu"]:
            if self._check_band_compatible(radio_band, "gw"):
                break
        else:
            raise RuntimeError("No 5g radio band supported!")
        unii_4_channels = self.regulatory_rule["UNII_4"]["HT20"]
        supported_channels = self.gw.capabilities.get_supported_radio_channels(freq_band=radio_band)
        self.unii_4_capable = set(unii_4_channels).issubset(supported_channels)
        return self.unii_4_capable

    def _check_band_compatible(self, band: str, device: str) -> bool:
        """Check if the device capabilities contain a radio interface name for the selected band."""
        try:
            res = self.__getattribute__(device).capabilities.get_phy_radio_ifname(freq_band=band) is not None
        except AttributeError:
            res = False
        if not res:
            log.debug(f"Radio band {band} is not compatible with device")
        return res

    def _check_band_channel_compatible(self, band: str, channel: int, device: str, ht_mode: str = "HT20") -> bool:
        """Check if the device supports the requested channel and if the channel, ht_mode and band are regulatory compliant."""
        try:
            channels = self.__getattribute__(device).capabilities.get_supported_radio_channels(freq_band=band)
        except AttributeError:
            return False
        if not channels:
            return False
        channel_supported = channel in channels
        if not channel_supported:
            log.debug(f"Radio band {band} is not compatible with device")
        channel_ht_mode_band_regulatory_compliant = validate_channel_ht_mode_band(
            channel,
            radio_band=band,
            ht_mode=ht_mode,
            reg_domain=self.regulatory_domain,
            regulatory_rule=self.regulatory_rule,
        )
        return channel_supported and channel_ht_mode_band_regulatory_compliant

    def get_if_name_type_from_if_role(self, if_role: str, radio_band: str | None = None) -> list[tuple[str]]:
        """
        Return the interface type and name from the interface role and optionally the radio band for VIFs.

        Args:
            if_role (str): Interface role. Options are keys from Interfaces list in model_properties file.
            radio_band (str): Optional: The radio band for VIF type interfaces.

        Raises:
            KeyError: If an unsupported interface role is provided.
            RuntimeError: If the radio band could not be determined.

        Returns:
            (list): List of tuples
                if_name (str): Interface name
                if_type (str): Interface type: vif, gre, eth, bridge
        """
        match if_role:
            case (
                "aux_1_ap"
                | "aux_2_ap"
                | "cportal_ap"
                | "fhaul_ap"
                | "haahs_ap"
                | "home_ap"
                | "backhaul_ap"
                | "onboard_ap"
                | "backhaul_sta"
            ):
                if_type = "vif"
                interfaces = self.gw.capabilities.get_ifnames(iftype=if_role)
            case "uplink_gre":
                if_type = "gre"
                interfaces = self.gw.capabilities.get_ifnames(iftype=if_role)
            case "lan_bridge" | "wan_bridge":
                if_type = "bridge"
                interfaces = self.gw.capabilities.get_bridge_ifname(bridge_type=if_role)
            case "lan_interfaces":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_lan_ifaces()
            case "wan_interfaces":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_wan_ifaces()
            case "management_interface":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_management_iface()
            case "ppp_wan_interface":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_ppp_wan_interface()
            case "primary_lan_interface":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_primary_lan_iface()
            case "primary_wan_interface":
                if_type = "eth"
                interfaces = self.gw.capabilities.get_primary_wan_iface()
            case _:
                raise KeyError(f"Invalid interface role: {if_role}")
        if isinstance(interfaces, dict) and if_type == "vif":
            if radio_band in radio_band_list:
                if_names = interfaces.get(radio_band, None)
            elif radio_band is None:
                if_names = list(filter(None, list(interfaces.values())))
            else:
                raise RuntimeError(f"Unsupported radio_band: {radio_band}")
        else:
            if_names = interfaces
        if if_names is None:
            return
        if isinstance(if_names, str):
            if_names = [if_names]
        interface_list = [(if_name, if_type) for if_name in if_names]
        return interface_list

    def _check_ht_mode_band_support(self, radio_band: str, ht_mode: str, device: str = "gw") -> bool:
        try:
            band_max_width = self.__getattribute__(device).capabilities.get_max_channel_width(freq_band=radio_band)
            if not band_max_width:
                return False
            ht_mode_num = int(ht_mode.split("HT")[1])
            if ht_mode_num > band_max_width:
                log.debug(
                    f"HT mode {ht_mode} for radio band {radio_band} is larger than max supported width for band of HT{band_max_width}",
                )
                return False
        except AttributeError:
            return False
        return True

    def _replace_if_role_with_if_name_type(self, inputs: dict) -> dict:
        """Replace the if_role argument and values with if_name and if_type from the device capabilities."""
        tmp_inputs = []
        if "if_role" not in inputs.get("args_mapping", []):
            return inputs
        else:
            if_role_idx = inputs["args_mapping"].index("if_role")
        for single_input in inputs["inputs"].copy():
            try:
                radio_band_idx = inputs["args_mapping"].index("radio_band")
                radio_band = single_input[radio_band_idx]
            except ValueError:
                radio_band = None
            if_role = single_input[if_role_idx]
            interfaces = self.get_if_name_type_from_if_role(if_role, radio_band)
            if interfaces is not None:
                tmp_inputs.extend([single_input + list(interface) for interface in interfaces])
                if not any(["if_name" in inputs["args_mapping"], "if_type" in inputs["args_mapping"]]):
                    inputs["args_mapping"].extend(["if_name", "if_type"])
        inputs["inputs"] = tmp_inputs
        return inputs

    @staticmethod
    def _inputs_int_or_str_to_list(inputs: dict) -> dict:
        """Wrap int or str type test case inputs into a list."""
        for idx, single_input in enumerate(inputs.get("inputs", [])):
            if isinstance(single_input, str) or isinstance(single_input, int):
                inputs["inputs"][idx] = [single_input]
        return inputs

    @staticmethod
    def _generate_permutations(single_input: list) -> list:
        """
        Generate permutations.

        Attempts to generate permutations by finding list or set type elements in the single_input list and replacing
        these elements with values contained within.

        Example:
            input:
               [[6, "HT40", "24g", [36, 123]],
                [6, "HT40", "6g", {1, 2, 3}]]
            output:
               [[6, "HT40", "24g", 36],
                [6, "HT40", "24g", 123],
                [6, "HT40", "6g", 1],
                [6, "HT40", "6g", 2],
                [6, "HT40", "6g", 3]]

        Args:
            single_input (list): Input list.
        """
        list_items = [item for item in single_input if isinstance(item, list | set)]
        for p in product(*list_items):
            iterator = iter(p)
            yield [output if not isinstance(output, list) else next(iterator) for output in single_input]

    def _expand_permutations(self, inputs: dict) -> dict:
        """
        Generate several test case inputs if the test case inputs contains expand_permutations=True.

        Expand any list or set in a single input into several inputs containing items of that list item.
        Expand any tuple in a single input into several inputs containing items in (end-inclusive) range of that tuple.
        """
        if not inputs.get("expand_permutations", False):
            return inputs
        tmp_inputs = []
        for single_input in inputs["inputs"]:
            # Expand tuples into lists ov values within the end-inclusive range of the tuple
            tmp_input = [
                item if not isinstance(item, tuple) else list(range(item[0], item[1] + 1)) for item in single_input
            ]
            for permutation in self._generate_permutations(tmp_input):
                tmp_inputs.append(permutation)
        inputs["inputs"] = tmp_inputs
        return inputs

    @staticmethod
    def _implicit_insert_encryption(inputs: dict) -> dict:
        """Implicitly insert missing encryption parameter into test case inputs where radio_band is present."""
        if (
            "args_mapping" not in inputs
            or "radio_band" not in inputs["args_mapping"]
            or "encryption" in inputs["args_mapping"]
        ):
            return inputs
        radio_band_index = inputs["args_mapping"].index("radio_band")
        inputs["args_mapping"] = inputs["args_mapping"] + ["encryption"]
        encryption_index = inputs["args_mapping"].index("encryption")
        for idx, single_input in enumerate(inputs["inputs"]):
            if len(single_input) == len(inputs["args_mapping"]):
                continue
            encryption = "WPA3" if str(single_input[radio_band_index]).lower() == "6g" else "WPA2"
            inputs["inputs"][idx].insert(encryption_index, encryption)
        return inputs

    def _filter_device_incompatible_bands(self, inputs: dict) -> dict:
        """Filter out inputs where radio_band is set and not supported by the device."""
        if "args_mapping" not in inputs:
            return inputs
        if set(radio_band_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        tmp_inputs = []
        radio_band_keys = set(radio_band_keywords).intersection(inputs["args_mapping"])
        for single_input in inputs["inputs"]:
            compatibility_condition = True
            for radio_band_key in radio_band_keys:
                radio_band_index = inputs["args_mapping"].index(radio_band_key)
                radio_band = single_input[radio_band_index]
                device = "leaf" if radio_band_key.removesuffix("_radio_band") in ["leaf", "l1", "l2"] else "gw"
                band_compatible = self._check_band_compatible(radio_band, device)
                if radio_band is not None and not band_compatible:
                    compatibility_condition = False
                    continue
            if compatibility_condition:
                tmp_inputs.append(single_input)
        inputs["inputs"] = tmp_inputs
        return inputs

    def _filter_device_incompatible_bandwidths(self, inputs: dict) -> dict:
        """Filter out inputs where ht_mode is not supported by the device."""
        if "args_mapping" not in inputs:
            return inputs
        if set(radio_band_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        tmp_inputs = []
        radio_band_keys = set(radio_band_keywords).intersection(inputs["args_mapping"])
        for single_input in inputs["inputs"]:
            compatibility_condition = True
            for radio_band_key in radio_band_keys:
                radio_band_index = inputs["args_mapping"].index(radio_band_key)
                radio_band = single_input[radio_band_index]
                ht_mode = "HT20"
                if "ht_mode" in inputs["args_mapping"]:
                    ht_mode_index = inputs["args_mapping"].index("ht_mode")
                    ht_mode = single_input[ht_mode_index]
                ht_mode_supported = self._check_ht_mode_band_support(radio_band=radio_band, ht_mode=ht_mode)
                if None in [radio_band, ht_mode]:
                    """if any of the provided parameters is None, skip this check"""
                    pass
                elif not ht_mode_supported:
                    compatibility_condition = False
                    continue
            if compatibility_condition:
                tmp_inputs.append(single_input)
        inputs["inputs"] = tmp_inputs
        return inputs

    def _filter_regulatory_incompatible_wifi_params(self, inputs: dict) -> dict:
        """Filter out inputs where ht_mode is not supported by the device."""
        if "args_mapping" not in inputs:
            return inputs
        if set(radio_band_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        if set(channel_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        tmp_inputs = []
        radio_band_keys = set(radio_band_keywords).intersection(inputs["args_mapping"])
        for single_input in inputs["inputs"]:
            compatibility_condition = True
            for radio_band_key in radio_band_keys:
                radio_band_index = inputs["args_mapping"].index(radio_band_key)
                radio_band = single_input[radio_band_index]
                channel_prefix = radio_band_key.removesuffix("radio_band")
                channel_key = f"{channel_prefix}channel"
                channel_index = inputs["args_mapping"].index(channel_key)
                channel = single_input[channel_index]
                device = "leaf" if radio_band_key.removesuffix("_radio_band") in ["leaf", "l1", "l2"] else "gw"
                ht_mode = "HT20"
                if "ht_mode" in inputs["args_mapping"]:
                    ht_mode_index = inputs["args_mapping"].index("ht_mode")
                    ht_mode = single_input[ht_mode_index]
                channel_ht_mode_band_regulatory_compliant = self._check_band_channel_compatible(
                    radio_band,
                    channel,
                    device,
                    ht_mode=ht_mode,
                )
                if None in [radio_band, channel, ht_mode]:
                    """if any of the provided parameters is None, skip this check"""
                    pass
                elif not channel_ht_mode_band_regulatory_compliant:
                    compatibility_condition = False
                    continue
            if compatibility_condition:
                tmp_inputs.append(single_input)
        inputs["inputs"] = tmp_inputs
        return inputs

    def _remove_unii_4(self, inputs: dict) -> dict:
        """Remove combinations for UNII-4 channels for devices that do not support them."""
        if self._check_unii_4_capable():
            return inputs
        if "args_mapping" not in inputs:
            return inputs
        if set(radio_band_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        if set(channel_keywords).isdisjoint(inputs["args_mapping"]):
            return inputs
        tmp_inputs = []
        radio_band_keys = set(radio_band_keywords).intersection(inputs["args_mapping"])
        for single_input in inputs["inputs"]:
            compatibility_condition = True
            for radio_band_key in radio_band_keys:
                radio_band_index = inputs["args_mapping"].index(radio_band_key)
                radio_band = single_input[radio_band_index]
                channel_prefix = radio_band_key.removesuffix("radio_band")
                channel_key = f"{channel_prefix}channel"
                channel_index = inputs["args_mapping"].index(channel_key)
                channel = single_input[channel_index]
                ht_mode = "HT20"
                if "ht_mode" in inputs["args_mapping"]:
                    ht_mode_index = inputs["args_mapping"].index("ht_mode")
                    ht_mode = single_input[ht_mode_index]
                if None in [radio_band, channel, ht_mode]:
                    """if any of the provided parameters is None, skip this check"""
                    pass
                elif radio_band in ["5g", "5gu"] and (
                    channel in [169, 173, 177, 181]
                    or (channel == 165 and ht_mode != "HT20")
                    or (channel in [149, 153, 157, 161] and ht_mode == "HT160")
                ):
                    compatibility_condition = False
                    continue
            if compatibility_condition:
                tmp_inputs.append(single_input)
        inputs["inputs"] = tmp_inputs
        return inputs

    def _ignore_test_cases(self, inputs: dict) -> dict:
        """Ignore test cases when the inputs contain the 'ignore' key."""
        flag = "ignore"
        if flag not in inputs:
            return inputs

        if not isinstance(inputs[flag], dict):
            raise TypeError(f"type(inputs['{flag}']) is {type(inputs[flag])}, should only be dict.")

        flag_conf = inputs[flag]
        tmp_inputs = []
        if "inputs" in flag_conf and "inputs" in inputs:
            # Ignore only speficied inputs, instead of the entire test case
            flag_conf = self._inputs_int_or_str_to_list(flag_conf)
            flag_inputs = flag_conf["inputs"]
            if not isinstance(inputs["inputs"], list):
                raise TypeError(f"type(inputs['inputs']) is {type(inputs['inputs'])}, should only be list.")
            if not isinstance(flag_inputs, list):
                raise TypeError(f"type(inputs['{flag}']['inputs']) is {type({flag_inputs})}, should only be list.")
            for single_input in inputs["inputs"]:
                remove = any(single_input == flag_input for flag_input in flag_inputs)
                if not remove:
                    tmp_inputs.append(single_input)

        if "msg" in flag_conf:
            log.debug(f"Ignoring configuration: {flag_conf['msg']}. Old: {inputs['inputs']}. New {tmp_inputs}.")

        inputs["inputs"] = tmp_inputs
        return inputs

    def _do_args_mapping(self, inputs: dict) -> dict:
        """Map inputs to args, extract flags and provide configs."""
        if "inputs" not in inputs:
            raise KeyError(f'Key "inputs" not present in argument: {inputs}')

        configs = []

        flags = [flag for flag in all_pytest_flags if flag in inputs]

        for single_input in inputs["inputs"]:
            config = {}
            config = single_input if "args_mapping" not in inputs else dict(zip(inputs["args_mapping"], single_input))
            if config is None:
                continue

            for flag in flags:
                flag_conf = inputs[flag]
                flag_conf = self._inputs_int_or_str_to_list(flag_conf)
                flag_msg = flag_conf.get("msg", f"{flag.upper()}: Uncommented {flag.upper()}")
                # Do not unpack the flag if there are speficied inputs and none match the current config
                if "inputs" in flag_conf and not any(single_input == flag_input for flag_input in flag_conf["inputs"]):
                    continue
                config[flag] = True
                config[f"{flag}_msg"] = flag_msg

            configs.append(config)
        inputs["configs"] = configs
        return inputs

    def _unpack_default_values(self, inputs: dict) -> list[dict]:
        """
        Unpack default values from test case configs into each individual test case configuration.

        When using dictionary unpacking with the ** operator to merge dictionaries, the order of merging matters.
        The latter dictionary in the sequence take precedence over the former one. Therefore, the dictionary
        containing default test case values ('default') should always come second, so that it is not overwritten by
        the dictionary containing generated values ('single_config').
        """
        default_configs = inputs.get("default", {})
        configs = inputs["configs"]
        unpacked_configs = [{**single_config, **default_configs} for single_config in configs]
        return unpacked_configs

    def default_gen(self, inputs: dict) -> list[dict]:
        if not isinstance(inputs, dict):
            raise TypeError(f"type(inputs):{type(inputs)}, should only be dict.")
        if "inputs" not in inputs:
            inputs["inputs"] = [{}]

        import traceback

        try:
            inputs = self._replace_if_role_with_if_name_type(inputs)
            inputs = self._inputs_int_or_str_to_list(inputs)
            inputs = self._expand_permutations(inputs)
            inputs = self._implicit_insert_encryption(inputs)
            inputs = self._filter_device_incompatible_bands(inputs)
            inputs = self._filter_device_incompatible_bandwidths(inputs)
            inputs = self._filter_regulatory_incompatible_wifi_params(inputs)
            inputs = self._remove_unii_4(inputs)
            inputs = self._ignore_test_cases(inputs)
            inputs = self._do_args_mapping(inputs)
            configs = self._unpack_default_values(inputs)
        except Exception as exception:
            raise exception(traceback.format_exc())
        return configs
