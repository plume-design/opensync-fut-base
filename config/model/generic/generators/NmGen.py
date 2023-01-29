import framework.tools.logger

global log
if 'log' not in globals():
    log = framework.tools.logger.get_logger()


class NmGen:
    def _get_if_names_if_type_combinations(self, eth_only=False, vif_only=False, vif_type='backhaul_sta',
                                           vif_phy_only=False, only_names=False):
        eth_interface_combinations = []
        vif_phy_interface_combinations = []
        vif_interface_combinations = []
        lan_eth_interfaces = self.dut_gw_capabilities.get('interfaces.lan_interfaces')
        vif_phy_radio_names = self.dut_gw_capabilities.get('interfaces.phy_radio_name')
        vif_phy_radio_names = list(filter(None, list(vif_phy_radio_names.values())))
        vif_radio_names = self.dut_gw_capabilities.get(f'interfaces.{vif_type}')
        vif_radio_names = list(filter(None, list(vif_radio_names.values())))
        for i in lan_eth_interfaces:
            if only_names:
                eth_interface_combinations.append(i)
            else:
                eth_interface_combinations.append((i, 'eth'))
        if eth_only:
            return eth_interface_combinations

        for i in vif_phy_radio_names:
            if only_names:
                vif_phy_interface_combinations.append(i)
            else:
                vif_phy_interface_combinations.append((i, 'vif'))
        if vif_phy_only:
            return vif_phy_interface_combinations
        for i in vif_radio_names:
            if only_names:
                vif_interface_combinations.append(i)
            else:
                vif_interface_combinations.append((i, 'vif'))
        if vif_only:
            return vif_interface_combinations
        return eth_interface_combinations + vif_phy_interface_combinations + vif_interface_combinations

    def _get_if_name_by_band_and_type(self, band, if_type):
        return self.dut_gw_capabilities.get(f'interfaces.{if_type}.{band}')

    def _parse_nm_inputs(self, inputs):
        tmp_inputs = []
        if 'FutGen|eth-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|eth-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(eth_only=True)
            if not self._parse_fut_opts(inputs, i=['FutGen|eth-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|eth-vif-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|eth-vif-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(eth_only=False)
            if not self._parse_fut_opts(inputs, i=['FutGen|eth-vif-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|vif-phy-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|vif-phy-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(vif_phy_only=True)
            if not self._parse_fut_opts(inputs, i=['FutGen|vif-phy-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|vif-home-ap-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|vif-home-ap-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(vif_only=True, vif_type='home_ap')
            if not self._parse_fut_opts(inputs, i=['FutGen|vif-home-ap-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|vif-bhaul-sta-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|vif-bhaul-sta-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(vif_only=True, vif_type='backhaul_sta')
            if not self._parse_fut_opts(inputs, i=['FutGen|vif-bhaul-sta-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|vif-bhaul-ap-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|vif-bhaul-ap-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(vif_only=True, vif_type='backhaul_ap')
            if not self._parse_fut_opts(inputs, i=['FutGen|vif-bhaul-ap-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        if 'FutGen|vif-onboard-ap-interfaces' in inputs['inputs']:
            inputs['inputs'].remove('FutGen|vif-onboard-ap-interfaces')
            eth_inputs = self._get_if_names_if_type_combinations(vif_only=True, vif_type='onboard_ap')
            if not self._parse_fut_opts(inputs, i=['FutGen|vif-onboard-ap-interfaces'], cfg={}):
                for eth_input in eth_inputs:
                    inputs['inputs'].insert(0, {
                        'if_name': eth_input[0],
                        'if_type': eth_input[1],
                    })
        for i in inputs['inputs']:
            if 'FutGen|phy-if-by-band-and-type' in i:
                index = i.index('FutGen|phy-if-by-band-and-type')
                band_index = inputs['args_mapping'].index('radio_band')
                if_name = self._get_if_name_by_band_and_type(i[band_index], 'phy_radio_name')
                if not if_name:
                    continue
                i[index] = if_name
                i.insert(index + 1, 'vif')
            if 'FutGen|vif-home-ap-by-band-and-type' in i:
                index = i.index('FutGen|vif-home-ap-by-band-and-type')
                band_index = inputs['args_mapping'].index('radio_band')
                if_name = self._get_if_name_by_band_and_type(i[band_index], 'home_ap')
                if not if_name:
                    continue
                i[index] = if_name
                i.insert(index + 1, 'vif')
            if 'FutGen|bhaul-sta-by-band-and-type' in i:
                index = i.index('FutGen|bhaul-sta-by-band-and-type')
                band_index = inputs['args_mapping'].index('radio_band')
                if_name = self._get_if_name_by_band_and_type(i[band_index], 'backhaul_sta')
                if not if_name:
                    continue
                i[index] = if_name
                i.insert(index + 1, 'vif')
            if 'FutGen|eth-interfaces-if-name' in i:
                del (i['FutGen|eth-interfaces-if-name'])
                i = self._get_if_names_if_type_combinations(eth_only=True, only_names=True)
                for ic in i:
                    if ic:
                        tmp_inputs.append(ic)
                continue
            if 'FutGen|bridge-interface-if-name' in i:
                type = i['FutGen|bridge-interface-if-name']
                del (i['FutGen|bridge-interface-if-name'])
                if_name = self.dut_gw_capabilities.get(f'interfaces.{type}_bridge')
                if not if_name:
                    continue
                i = if_name
            if 'FutGen|bridge-interface-if-name-type' in i:
                type = i['FutGen|bridge-interface-if-name-type']
                del (i['FutGen|bridge-interface-if-name-type'])
                if_name = self.dut_gw_capabilities.get(f'interfaces.{type}_bridge')
                if not if_name:
                    continue
                i = {
                    'if_name': if_name,
                    'if_type': 'bridge',
                    **i,
                }
            if 'FutGen|vif-interfaces-if-name' in i:
                type = i['FutGen|vif-interfaces-if-name']
                del (i['FutGen|vif-interfaces-if-name'])
                i = self.dut_gw_capabilities.get(f'interfaces.{type}')
                for if_name in i.values():
                    if if_name:
                        tmp_inputs.append(if_name)
                continue
            if 'FutGen|primary-interface-if-name' in i:
                type = i['FutGen|primary-interface-if-name']
                del (i['FutGen|primary-interface-if-name'])
                if_name = self.dut_gw_capabilities.get(f'interfaces.primary_{type}_interface')
                if not if_name:
                    continue
                i = if_name
            if 'FutGen|primary-interface-if-name-type' in i:
                type = i['FutGen|primary-interface-if-name-type']
                del (i['FutGen|primary-interface-if-name-type'])
                if_name = self.dut_gw_capabilities.get(f'interfaces.primary_{type}_interface')
                if not if_name:
                    continue
                i = {
                    'if_name': if_name,
                    'if_type': 'eth',
                    **i,
                }
            if i:
                tmp_inputs.append(i)
        inputs['inputs'] = tmp_inputs
        return inputs

    def gen_nm2_enable_disable_iface_network(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_ovsdb_configure_interface_dhcpd(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_ovsdb_ip_port_forward(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_ovsdb_remove_reinsert_iface(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_broadcast(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_dns(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_gateway(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_inet_addr(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_mtu(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_nat(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_netmask(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_vlan_interface(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_nm2_set_ip_assign_scheme(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)
