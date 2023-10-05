class NmGen:
    def _get_if_names_if_type_combinations(self, gen_key, if_type=None, if_role=None):
        only_names = False

        if gen_key.endswith("-if-name"):
            only_names = True
            gen_key = gen_key.removesuffix("-if-name")

        if gen_key.endswith("-if-name-type"):
            gen_key = gen_key.removesuffix("-if-name-type")

        match gen_key:
            case "FutGen|eth-interfaces":
                if_type = "eth"
                if_role = f"{if_role}_interfaces" if if_role else "lan_interfaces"
            case "FutGen|vif-phy-interfaces":
                if_role = "phy_radio_name"
                if_type = "vif"  # Should not be used?
            case "FutGen|vif-interfaces":
                if_role = "backhaul_sta"
                if_type = "vif"
            case "FutGen|vif-home-ap-interfaces":
                if_role = "home_ap"
                if_type = "vif"
            case "FutGen|vif-bhaul-sta-interfaces":
                if_role = "backhaul_sta"
                if_type = "vif"
            case "FutGen|vif-bhaul-ap-interfaces":
                if_role = "backhaul_ap"
                if_type = "vif"
            case "FutGen|vif-onboard-ap-interfaces":
                if_role = "onboard_ap"
                if_type = "vif"
            case "FutGen|bridge-interface":
                if_type = "bridge"
                if_role = f"{if_role}_bridge" if if_role else "lan_bridge"
            case "FutGen|primary-interface":
                if_type = "eth"
                if_role = f"primary_{if_role}_interface" if if_role else "primary_lan_interface"
            case _:
                RuntimeError(f"Unsupported configuration key: '{gen_key}'.")

        interfaces = self.gw_capabilities.get(f"interfaces.{if_role}")
        if isinstance(interfaces, dict):
            interfaces = list(filter(None, list(interfaces.values())))
        elif isinstance(interfaces, str):
            interfaces = [interfaces]
        try:
            interface_list = [interface if only_names else (interface, if_type) for interface in interfaces]
        except TypeError:
            interface_list = None
        return interface_list

    def _get_if_name_by_band_and_type(self, band, if_type):
        return self.gw_capabilities.get(f"interfaces.{if_type}.{band}")

    def _modify_input_item_str(self, inputs, single_input: str):
        """Process the single test case input string based on auxilliary configuration in inputs.

        Args:
            inputs (dict): Test case inputs for one test case
            single_input (str): Single input for one test case, on which to execute processing

        Returns:
            None: if test case input is ignored
            dict: modified single test case input
        """
        interface_inputs = self._get_if_names_if_type_combinations(gen_key=single_input)
        tmp_cfgs = self._parse_fut_opts(inputs, single_input=[single_input], cfg=interface_inputs)
        if tmp_cfgs:
            tmp_cfgs = [dict(zip(["if_name", "if_type"], tmp_cfg)) for tmp_cfg in tmp_cfgs]
        return tmp_cfgs

    def _modify_input_item_list(self, inputs, single_input: list):
        """Modify one item in the single test case input list based on auxilliary configuration in inputs.

        Args:
            inputs (dict): Test case inputs for one test case
            single_input (list): Single input for one test case, on which to execute processing

        Returns:
            None: if test case input is ignored or items in list mismatch the device capabilities
            dict: modified single test case input
        """
        if "FutGen|vif-home-ap-by-band-and-type" in single_input:
            token = "FutGen|vif-home-ap-by-band-and-type"
            if_role = "home_ap"
        elif "FutGen|bhaul-sta-by-band-and-type" in single_input:
            token = "FutGen|bhaul-sta-by-band-and-type"
            if_role = "backhaul_sta"
        else:
            RuntimeError(f"Unsupported FutGen token in input '{single_input}'.")
        token_index = single_input.index(token)
        band_index = inputs["args_mapping"].index("radio_band")
        if_name = self._get_if_name_by_band_and_type(single_input[band_index], if_role)
        if not if_name:
            return None
        # Replace token with interface name and insert interface type
        single_input[token_index] = if_name
        single_input.insert(token_index + 1, "vif")
        return single_input

    def _modify_input_item_dict(self, inputs, single_input: dict):
        """Modify one item in the single test case input list based on auxilliary configuration in inputs.

        Args:
            inputs (dict): Test case inputs for one test case
            single_input (dict): Single input for one test case, on which to execute processing

        Returns:
            None: if test case input is ignored or items in list mismatch the device capabilities
            dict: modified single test case input
        """
        tmp_cfgs = []
        if "FutGen|eth-interfaces-if-name" in single_input:
            token = "FutGen|eth-interfaces-if-name"
        elif "FutGen|bridge-interface-if-name" in single_input:
            token = "FutGen|bridge-interface-if-name"
        elif "FutGen|bridge-interface-if-name-type" in single_input:
            token = "FutGen|bridge-interface-if-name-type"
        elif "FutGen|vif-interfaces-if-name" in single_input:
            token = "FutGen|vif-interfaces-if-name"
        elif "FutGen|primary-interface-if-name" in single_input:
            token = "FutGen|primary-interface-if-name"
        elif "FutGen|primary-interface-if-name-type" in single_input:
            token = "FutGen|primary-interface-if-name-type"
        if_role = single_input[token]
        del single_input[token]
        interface_inputs = self._get_if_names_if_type_combinations(gen_key=token, if_role=if_role)
        if "-if-name-type" in token:
            interface_inputs = [dict(zip(["if_name", "if_type"], iface), **single_input) for iface in interface_inputs]
        if interface_inputs:
            tmp_cfgs.extend(interface_inputs)
        return tmp_cfgs

    def _parse_nm_inputs(self, inputs):
        tmp_inputs = []
        # To avoid loop corruption, the iterator is uses a list comprehension, as the inputs are manipulated in the loop
        # for input_item in [item for item in inputs["inputs"]]:
        for input_item in inputs["inputs"].copy():
            if "FutGen|" in input_item:
                # input_item is type str
                tmp_cfgs = self._modify_input_item_str(inputs=inputs, single_input=input_item)
                if tmp_cfgs:
                    tmp_inputs.extend(tmp_cfgs)
                continue
            elif isinstance(input_item, list):
                # input_item is type list
                tmp_cfgs = self._modify_input_item_list(inputs=inputs, single_input=input_item)
                if tmp_cfgs:
                    tmp_inputs.append(tmp_cfgs)
                continue
            elif isinstance(input_item, dict):
                # input_item is type dict
                tmp_cfgs = self._modify_input_item_dict(inputs=inputs, single_input=input_item)
                if tmp_cfgs:
                    tmp_inputs.extend(tmp_cfgs)
                continue
            if input_item:
                tmp_inputs.append(input_item)
        inputs["inputs"] = tmp_inputs
        return inputs

    def gen_nm2_enable_disable_iface_network(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_ovsdb_configure_interface_dhcpd(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_ovsdb_ip_port_forward(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_ovsdb_remove_reinsert_iface(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_broadcast(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_dns(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_gateway(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_inet_addr(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_mtu(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_nat(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_netmask(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_vlan_interface(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs

    def gen_nm2_set_ip_assign_scheme(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        inputs = self.default_gen(inputs)
        return inputs
