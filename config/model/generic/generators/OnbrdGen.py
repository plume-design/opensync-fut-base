from .NmGen import NmGen


class OnbrdGen:
    def _parse_nm_inputs(self, inputs):
        return NmGen._parse_nm_inputs(self, inputs)

    def gen_onbrd_verify_dhcp_dry_run_success(self, inputs):
        inputs = self._parse_nm_inputs(inputs)
        return self.default_gen(inputs)
