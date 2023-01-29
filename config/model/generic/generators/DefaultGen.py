import importlib.util
import sys
from pathlib import Path

import framework.tools.logger
from framework.tools.functions import (load_reg_rule,
                                       validate_channel_ht_mode_band)

sys.path.append('../../../')

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()

generator_modules = []
generator_dir = 'config/model/generic/generators'
generator_mod = generator_dir.replace('/', '.')
generator_names = [f.stem for f in Path(__file__).parent.absolute().iterdir() if
                   'Gen.py' in f.name and 'Template' not in f.name and 'DefaultGen' not in f.name]
for generator_name in generator_names:
    spec = importlib.util.find_spec(f'{generator_mod}.{generator_name}')
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Shallow-merge new module over existing dictionary
        generator_modules.append(module.__getattribute__(generator_name)())


class DefaultGenClass:
    def __init__(
            self,
            dut_gw_capabilities,
            ref_leaf_capabilities,
            gen_type='optimized',
    ):
        self.dut_gw_capabilities = dut_gw_capabilities
        self.ref_leaf_capabilities = ref_leaf_capabilities
        self.regulatory_domain = self.dut_gw_capabilities.get('regulatory_domain')
        self.gen_type = gen_type
        self.regulatory_rule = load_reg_rule()
        attributes_to_add = []
        for gen_key in dir(self):
            if not gen_key.startswith('__') and not gen_key.endswith('__'):
                attributes_to_add.append(gen_key)

        for generator_module in generator_modules:
            for gen_key in dir(generator_module):
                if not gen_key.startswith('__') and not gen_key.endswith('__'):
                    self.__setattr__(gen_key, getattr(generator_module, gen_key))
            for add_attr in attributes_to_add:
                setattr(generator_module.__class__, add_attr, self.__getattribute__(add_attr))

    def _get_default_options(self, inputs):
        default = {}
        if 'default' in inputs:
            default = inputs['default']
        return default

    def _check_band_compatible(self, band, device):
        res = self.__getattribute__(f'{device}_capabilities').get(f'interfaces.phy_radio_name.{band}') != ""
        if not res:
            log.warning(f'Radio band {band} is not compatible with device')
        return res

    def _check_band_channel_compatible(self, band, channel, device, ht_mode='HT20'):
        channels = self.__getattribute__(f'{device}_capabilities').get(f'interfaces.radio_channels.{band}')
        if not channels or channels == '':
            return False
        device_check = channel in self.__getattribute__(f'{device}_capabilities').get(
            f'interfaces.radio_channels.{band}')
        if not device_check:
            log.warning(f'Radio band {band} is not compatible with device')
        reg_check = validate_channel_ht_mode_band(channel, radio_band=band, ht_mode=ht_mode,
                                                  reg_domain=self.regulatory_domain,
                                                  regulatory_rule=self.regulatory_rule)
        return device_check and reg_check

    def _check_ht_mode_band_support(self, radio_band, ht_mode, device='dut_gw'):
        try:
            band_max_width = self.__getattribute__(f'{device}_capabilities').get(
                f'interfaces.max_channel_width.{radio_band}')
            if not band_max_width:
                return False
            ht_mode_num = int(ht_mode.split('HT')[1])
            if ht_mode_num > band_max_width:
                log.warning(
                    f'HT mode {ht_mode} for radio band {radio_band} is larger than max supported width for band of HT{band_max_width}')
                return False
        except Exception:
            return False
        return True

    def _check_encryption_compatible(self, encryption):
        if encryption == 'WPA2':
            return True
        elif encryption == 'WPA3':
            supported_hw_modes = self.dut_gw_capabilities.get('interfaces.radio_hw_mode')
            for hw_mode in supported_hw_modes.values():
                if hw_mode == '11ax':
                    return True
            log.warning('Encryption WPA3 not supported on device.')
        return False

    def _parse_fut_opts(self, inputs, i=None, cfg=None):
        if any([res in inputs for res in ['skip', 'ignore', 'xfail']]):
            for fut_opt in ['skip', 'ignore', 'xfail']:
                if fut_opt in inputs:
                    if isinstance(inputs[fut_opt], dict):
                        inputs[fut_opt] = [inputs[fut_opt]]
                    for fut_opt_conf in inputs[fut_opt]:
                        do_opt = False
                        if 'inputs' in fut_opt_conf and i:
                            for f in fut_opt_conf['inputs']:
                                if not isinstance(f, list):
                                    f = [f]
                                if i == f:
                                    do_opt = True
                                    break
                        elif 'input' in fut_opt_conf and i:
                            if not isinstance(fut_opt_conf['input'], list):
                                fut_opt_conf['input'] = [fut_opt_conf['input']]
                            if i == fut_opt_conf['input']:
                                do_opt = True
                            else:
                                continue
                        elif inputs['inputs'] == [{}]:
                            do_opt = True
                        elif 'msg' in fut_opt_conf:
                            do_opt = True
                        if do_opt:
                            if fut_opt == 'ignore':
                                fut_opt = 'ignore_collect'
                            cfg[fut_opt] = True
                            if 'msg' in fut_opt_conf:
                                cfg[f'{fut_opt}_msg'] = fut_opt_conf['msg']
                            else:
                                cfg[f'{fut_opt}_msg'] = f'{fut_opt.upper()}: Uncommented {fut_opt.upper()}'
        return cfg

    def _do_args_mapping(self, inputs):
        tmp_inputs = []
        if 'inputs' in inputs:
            for i in inputs['inputs']:
                tmp_cfg = {}
                if isinstance(i, str) or isinstance(i, int):
                    i = [i]
                elif isinstance(i, dict):
                    i = self._parse_fut_opts(inputs, cfg=i)
                    tmp_inputs.append(i)
                    continue
                if 'args_mapping' in inputs:
                    if 'encryption' in inputs['args_mapping']:
                        encryption_index = inputs['args_mapping'].index('encryption')
                        check_encryption = self._check_encryption_compatible(i[encryption_index])
                        if not check_encryption:
                            continue
                    if 'radio_band' in inputs['args_mapping']:
                        radio_band_index = inputs['args_mapping'].index('radio_band')
                        check_band = self._check_band_compatible(i[radio_band_index], 'dut_gw')
                        if not check_band:
                            continue
                    if 'radio_band' in inputs['args_mapping'] and 'channel' in inputs['args_mapping']:
                        radio_band_index = inputs['args_mapping'].index('radio_band')
                        channel_index = inputs['args_mapping'].index('channel')
                        ht_mode = 'HT20'
                        if 'ht_mode' in inputs['args_mapping']:
                            ht_mode_index = inputs['args_mapping'].index('ht_mode')
                            ht_mode = i[ht_mode_index]
                        check_channel_band = self._check_band_channel_compatible(i[radio_band_index], i[channel_index],
                                                                                 'dut_gw', ht_mode=ht_mode)
                        check_band_ht_mode = self._check_ht_mode_band_support(radio_band=i[radio_band_index],
                                                                              ht_mode=ht_mode)
                        if not check_channel_band or not check_band_ht_mode:
                            continue
                    if 'radio_band' in inputs['args_mapping'] and 'channels' in inputs['args_mapping']:
                        radio_band_index = inputs['args_mapping'].index('radio_band')
                        channels_index = inputs['args_mapping'].index('channels')
                        ht_mode = 'HT20'
                        if 'ht_mode' in inputs['args_mapping']:
                            ht_mode_index = inputs['args_mapping'].index('ht_mode')
                            ht_mode = i[ht_mode_index]
                        new_channels = []
                        for ch in i[channels_index]:
                            check_channel_band = self._check_band_channel_compatible(i[radio_band_index], ch, 'dut_gw',
                                                                                     ht_mode=ht_mode)
                            check_band_ht_mode = self._check_ht_mode_band_support(radio_band=i[radio_band_index],
                                                                                  ht_mode=ht_mode)
                            if check_channel_band and check_band_ht_mode:
                                new_channels.append(ch)
                            else:
                                log.warning(
                                    f'Channel {ch} is not valid for {i[radio_band_index]} for set regulatory domain of {self.regulatory_domain}')
                        i[channels_index] = new_channels
                    for il in range(len(i)):
                        tmp_cfg[inputs['args_mapping'][il]] = i[il]
                    tmp_cfg = self._parse_fut_opts(inputs, i=i, cfg=tmp_cfg)
                tmp_inputs.append(tmp_cfg)
        else:
            tmp_inputs.append(inputs)
        inputs['inputs'] = tmp_inputs
        return inputs

    def default_gen(self, inputs):
        if isinstance(inputs, list):
            return inputs
        default = self._get_default_options(inputs)
        if 'inputs' not in inputs:
            inputs['inputs'] = [{}]
        inputs = self._do_args_mapping(inputs)
        return [{**default, **i} for i in inputs['inputs']]
