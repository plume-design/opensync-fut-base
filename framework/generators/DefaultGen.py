import importlib.util
import sys
from pathlib import Path

from framework.lib.fut_lib import load_reg_rule, validate_channel_ht_mode_band
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
    def __init__(
        self,
        gw_capabilities,
        leaf_capabilities,
    ):
        self.gw_capabilities = gw_capabilities
        self.leaf_capabilities = leaf_capabilities
        self.regulatory_domain = self.gw_capabilities.get("regulatory_domain")
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

    @staticmethod
    def _get_default_options(inputs):
        default = {}
        if "default" in inputs:
            default = inputs["default"]
        return default

    def _check_band_compatible(self, band, device):
        res = self.__getattribute__(f"{device}_capabilities").get(f"interfaces.phy_radio_name.{band}") != ""
        if not res:
            log.debug(f"Radio band {band} is not compatible with device")
        return res

    def _check_band_channel_compatible(self, band, channel, device, ht_mode="HT20"):
        channels = self.__getattribute__(f"{device}_capabilities").get(f"interfaces.radio_channels.{band}")
        if not channels or channels == "":
            return False
        device_check = channel in self.__getattribute__(f"{device}_capabilities").get(
            f"interfaces.radio_channels.{band}",
        )
        if not device_check:
            log.debug(f"Radio band {band} is not compatible with device")
        reg_check = validate_channel_ht_mode_band(
            channel,
            radio_band=band,
            ht_mode=ht_mode,
            reg_domain=self.regulatory_domain,
            regulatory_rule=self.regulatory_rule,
        )
        return device_check and reg_check

    def _check_ht_mode_band_support(self, radio_band, ht_mode, device="gw"):
        try:
            band_max_width = self.__getattribute__(f"{device}_capabilities").get(
                f"interfaces.max_channel_width.{radio_band}",
            )
            if not band_max_width:
                return False
            ht_mode_num = int(ht_mode.split("HT")[1])
            if ht_mode_num > band_max_width:
                log.debug(
                    f"HT mode {ht_mode} for radio band {radio_band} is larger than max supported width for band of HT{band_max_width}",
                )
                return False
        except Exception:
            return False
        return True

    def _parse_fut_opts(self, inputs, single_input=None, cfg=None):
        if not any(res in inputs for res in ["skip", "ignore", "xfail"]):
            return cfg
        for fut_opt in ["skip", "ignore", "xfail"]:
            if fut_opt not in inputs:
                continue
            if "input" in inputs[fut_opt]:
                raise KeyError('Key "input" present in argument, did you mean "inputs"?')
            if isinstance(inputs[fut_opt], dict):
                inputs[fut_opt] = [inputs[fut_opt]]
            for fut_opt_conf in inputs[fut_opt]:
                do_opt = False
                if "inputs" in fut_opt_conf and single_input:
                    for fut_opt_conf_input in fut_opt_conf["inputs"]:
                        if not isinstance(fut_opt_conf_input, list):
                            fut_opt_conf_input = [fut_opt_conf_input]
                        if single_input == fut_opt_conf_input:
                            do_opt = True
                            break
                elif "msg" in fut_opt_conf:
                    do_opt = True
                elif inputs["inputs"] == [{}]:
                    do_opt = True
                if do_opt:
                    if fut_opt == "ignore":
                        if "msg" in fut_opt_conf:
                            log.debug(f"Ignoring test {cfg}: {fut_opt_conf['msg']}")
                        cfg = None
                        continue
                    cfg[fut_opt] = True
                    if "msg" in fut_opt_conf:
                        cfg[f"{fut_opt}_msg"] = fut_opt_conf["msg"]
                    else:
                        cfg[f"{fut_opt}_msg"] = f"{fut_opt.upper()}: Uncommented {fut_opt.upper()}"
        return cfg

    def _do_args_mapping(self, inputs):
        if "inputs" not in inputs:
            raise KeyError(f'Key "inputs" not present in argument: {inputs}')
        tmp_inputs = []
        get_encryption = False
        radio_band_index = -1
        encryption_index = -1
        if (
            "args_mapping" in inputs
            and "radio_band" in inputs["args_mapping"]
            and "encryption" not in inputs["args_mapping"]
        ):
            get_encryption = True
            radio_band_index = inputs["args_mapping"].index("radio_band")
            inputs["args_mapping"].append("encryption")
            encryption_index = inputs["args_mapping"].index("encryption")
        for single_input in inputs["inputs"]:
            tmp_cfg = {}
            if isinstance(single_input, str) or isinstance(single_input, int):
                single_input = [single_input]
            elif isinstance(single_input, dict):
                single_input = self._parse_fut_opts(inputs, cfg=single_input)
                if single_input is not None:
                    tmp_inputs.append(single_input)
                continue
            if "args_mapping" in inputs:
                if get_encryption and len(single_input) != len(inputs["args_mapping"]):
                    if single_input[radio_band_index] and str(single_input[radio_band_index]).lower() == "6g":
                        encryption = "WPA3"
                    else:
                        encryption = "WPA2"
                    single_input.insert(encryption_index, encryption)
                if "radio_band" in inputs["args_mapping"]:
                    radio_band_index = inputs["args_mapping"].index("radio_band")
                    check_band = self._check_band_compatible(single_input[radio_band_index], "gw")
                    if not check_band:
                        continue
                if "radio_band" in inputs["args_mapping"] and "channel" in inputs["args_mapping"]:
                    radio_band_index = inputs["args_mapping"].index("radio_band")
                    channel_index = inputs["args_mapping"].index("channel")
                    ht_mode = "HT20"
                    if "ht_mode" in inputs["args_mapping"]:
                        ht_mode_index = inputs["args_mapping"].index("ht_mode")
                        ht_mode = single_input[ht_mode_index]
                    check_channel_band = self._check_band_channel_compatible(
                        single_input[radio_band_index],
                        single_input[channel_index],
                        "gw",
                        ht_mode=ht_mode,
                    )
                    check_band_ht_mode = self._check_ht_mode_band_support(
                        radio_band=single_input[radio_band_index],
                        ht_mode=ht_mode,
                    )
                    if not check_channel_band or not check_band_ht_mode:
                        continue
                for il in range(len(single_input)):
                    tmp_cfg[inputs["args_mapping"][il]] = single_input[il]
                tmp_cfg = self._parse_fut_opts(inputs, single_input=single_input, cfg=tmp_cfg)
            if tmp_cfg:
                tmp_inputs.append(tmp_cfg)
        inputs["inputs"] = tmp_inputs
        return inputs

    def default_gen(self, inputs):
        if isinstance(inputs, list):
            return inputs
        default = self._get_default_options(inputs)
        if "inputs" not in inputs:
            inputs["inputs"] = [{}]
        inputs = self._do_args_mapping(inputs)
        """
            When using dictionary unpacking with the ** operator to merge dictionaries, the order of merging matters.
            The later dictionary in the sequence take precedence over the earlier one. Therefore, the dictionary
            containing default test input values ('default') should always come second, so that it is not overwritten by
            the dictionary containing generated values ('single_input').
        """
        default_inputs = [{**single_input, **default} for single_input in inputs["inputs"]]
        return default_inputs
