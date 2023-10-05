from .NmGen import NmGen


class OnbrdGen:
    def _get_if_names_if_type_combinations(self, gen_key, if_type=None, if_role=None):
        return NmGen._get_if_names_if_type_combinations(self, gen_key, if_type=None, if_role=None)

    def _modify_input_item_dict(self, inputs, single_input: dict):
        return NmGen._modify_input_item_dict(self, inputs, single_input)

    def _parse_nm_inputs(self, inputs):
        return NmGen._parse_nm_inputs(self, inputs)

    def gen_onbrd_verify_dhcp_dry_run_success(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)
