import framework.tools.logger
from framework.tools.functions import validate_channel_ht_mode_band


global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


class WmGen:
    def __init__(self):
        self.limited_channels_map = {
            '24g': [1, 6, 11],
            '5g': [36, 44, 56, 64, 100, 108, 149, 157],
            '5gl': [36, 44, 56, 64],
            '5gu': [100, 108, 149, 157],
            '6g': [5, 21, 37, 53, 69, 85, 101, 117, 133, 149, 165, 181, 197, 213, 229],
        }
        self.optimized_channels_map = {
            '24g': [6],
            '5g': [36, 157],
            '5gl': [36],
            '5gu': [157],
            '6g': [5, 149],
        }
        self.wpa3_not_supported_config = {
            'ignore': {
                'msg': 'NO-SUPPORT: Device does not support WPA3',
            },
        }

    def _check_wpa3_compatible(self):
        supported_hw_modes = self.dut_gw_capabilities.get('interfaces.radio_hw_mode')
        for hw_mode in supported_hw_modes.values():
            if hw_mode == '11ax':
                return True
        return False

    def _filter_supported_channels(self, channels, radio_band, ht_mode='HT20'):
        tmp_channels = []
        supported_channels = self.dut_gw_capabilities.get(f'interfaces.radio_channels.{radio_band}')
        for ch in channels:
            if ch in supported_channels and validate_channel_ht_mode_band(ch, radio_band=radio_band, ht_mode=ht_mode,
                                                                          reg_domain=self.regulatory_domain,
                                                                          regulatory_rule=self.regulatory_rule):
                tmp_channels.append(ch)
        return tmp_channels

    @staticmethod
    def _get_ht_modes(max_ht_mode):
        modes = []
        for i in [20, 40, 80, 160]:
            if i <= max_ht_mode:
                modes.append(f'HT{i}')
        return modes

    def gen_wm2_set_channel(self, inputs):
        tmp_inputs = []

        radio_channels_band = self.dut_gw_capabilities.get('interfaces.radio_channels')
        for radio_band, channels in radio_channels_band.items():
            if channels == '' or not channels:
                continue
            tmp_cfg = {}
            tmp_cfg['radio_band'] = radio_band
            if radio_band == '6g':
                channels = self.limited_channels_map['6g']
            if self.gen_type == 'optimized':
                channels = self.optimized_channels_map[radio_band]
            tmp_cfg['channels'] = self._filter_supported_channels(channels, radio_band)
            tmp_cfg['ht_mode'] = 'HT40'
            if tmp_cfg['channels']:
                tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def gen_wm2_set_ht_mode(self, inputs):
        tmp_inputs = []
        radio_channels_band = self.dut_gw_capabilities.get('interfaces.radio_channels')
        for radio_band, channels in radio_channels_band.items():
            if channels == '' or not channels:
                continue
            max_ht_mode = int(self.dut_gw_capabilities.get(f'interfaces.max_channel_width.{radio_band}'))
            channel_list = self.limited_channels_map[radio_band]
            if self.gen_type == 'optimized':
                channel_list = self.optimized_channels_map[radio_band]
            for ht_mode in self._get_ht_modes(max_ht_mode):
                tmp_cfg = {}
                tmp_cfg['radio_band'] = radio_band
                tmp_cfg['channels'] = self._filter_supported_channels(channel_list, radio_band, ht_mode=ht_mode)
                tmp_cfg['ht_modes'] = [ht_mode]
                if tmp_cfg['channels']:
                    tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def gen_wm2_ht_mode_and_channel_iteration(self, inputs):
        tmp_inputs = []
        radio_channels_band = self.dut_gw_capabilities.get('interfaces.radio_channels')
        for radio_band, channels in radio_channels_band.items():
            if channels == '' or not channels:
                continue
            max_ht_mode = int(self.dut_gw_capabilities.get(f'interfaces.max_channel_width.{radio_band}'))
            tmp_cfg = {}
            tmp_cfg['radio_band'] = radio_band
            if radio_band == '6g':
                channels = self.limited_channels_map['6g']
            if self.gen_type == 'optimized':
                channels = self.optimized_channels_map[radio_band]
            for ht_mode in self._get_ht_modes(max_ht_mode):
                tmp_cfg = {}
                tmp_cfg['radio_band'] = radio_band
                tmp_cfg['channels'] = self._filter_supported_channels(channels, radio_band, ht_mode=ht_mode)
                tmp_cfg['ht_modes'] = [ht_mode]
                if tmp_cfg['channels']:
                    tmp_inputs.append(tmp_cfg)
        return self.default_gen(tmp_inputs)

    def _parse_wm_inputs(self, inputs):
        tmp_inputs = []
        if 'args_mapping' in inputs:
            tmp_inputs = []
            for i in inputs['inputs']:
                if 'gw_radio_band' in inputs['args_mapping']:
                    gw_radio_band_index = inputs['args_mapping'].index('gw_radio_band')
                    if not self._check_band_compatible(i[gw_radio_band_index], 'dut_gw'):
                        continue
                if 'leaf_radio_band' in inputs['args_mapping']:
                    leaf_radio_band_index = inputs['args_mapping'].index('leaf_radio_band')
                    if not self._check_band_compatible(i[leaf_radio_band_index], 'ref_leaf'):
                        continue
                if 'gw_channel' in inputs['args_mapping'] and (
                        'gw_radio_band' in inputs['args_mapping'] or 'radio_band' in inputs['args_mapping']
                ):
                    if 'gw_radio_band' in inputs['args_mapping']:
                        radio_band_index = inputs['args_mapping'].index('gw_radio_band')
                    else:
                        radio_band_index = inputs['args_mapping'].index('radio_band')
                    gw_channel_index = inputs['args_mapping'].index('gw_channel')
                    if not self._check_band_channel_compatible(i[radio_band_index], i[gw_channel_index], 'dut_gw'):
                        continue

                if 'leaf_channel' in inputs['args_mapping'] and (
                        'leaf_radio_band' in inputs['args_mapping'] or 'radio_band' in inputs['args_mapping']
                ):
                    if 'leaf_radio_band' in inputs['args_mapping']:
                        radio_band_index = inputs['args_mapping'].index('leaf_radio_band')
                    else:
                        radio_band_index = inputs['args_mapping'].index('radio_band')
                    leaf_channel_index = inputs['args_mapping'].index('leaf_channel')
                    if not self._check_band_channel_compatible(i[radio_band_index], i[leaf_channel_index], 'ref_leaf'):
                        continue
                tmp_inputs.append(i)
        inputs['inputs'] = tmp_inputs
        return inputs

    def gen_wm2_topology_change_change_parent_change_band_change_channel(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_topology_change_change_parent_same_band_change_channel(self, inputs):
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_connect_wpa3_client(self, inputs):
        if not self._check_wpa3_compatible():
            log.warning('WPA3 is not supported on this device')
            return self.default_gen(self.wpa3_not_supported_config)
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_connect_wpa3_leaf(self, inputs):
        if not self._check_wpa3_compatible():
            log.warning('WPA3 is not supported on this device')
            return self.default_gen(self.wpa3_not_supported_config)
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_set_ht_mode_neg(self, inputs):
        tmp_inputs = []
        for i in inputs['inputs']:
            radio_band_index = inputs['args_mapping'].index('radio_band')
            radio_band = i[radio_band_index]
            band = self.dut_gw_capabilities.get(f'interfaces.max_channel_width.{radio_band}')
            if not band:
                continue
            max_ht_mode = int(band)
            if max_ht_mode < 160:
                tmp_inputs.append(i)
        inputs['inputs'] = tmp_inputs
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_wm2_create_wpa3_ap(self, inputs):
        if not self._check_wpa3_compatible():
            log.warning('WPA3 is not supported on this device')
            return self.default_gen(self.wpa3_not_supported_config)
        inputs = self._parse_wm_inputs(inputs)
        return self.default_gen(inputs)
