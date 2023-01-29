class SmGen:
    def _parse_sm_inputs(self, inputs):
        if 'args_mapping' in inputs:
            tmp_inputs = []
            for i in inputs['inputs']:
                tmp_inputs.append(i)
            inputs['inputs'] = tmp_inputs
        return inputs

    def gen_sm_leaf_report(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_sm_neighbor_report(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)
