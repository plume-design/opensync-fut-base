class SmGen:
    def _parse_sm_inputs(self, inputs):
        if "args_mapping" in inputs:
            get_sm_radio_band = (
                True
                if "channel" in inputs["args_mapping"] and "FutGen|sm_radio_type" in inputs["args_mapping"]
                else False
            )
            sm_radio_band, sm_radio_band_index = None, None
            if get_sm_radio_band:
                sm_radio_band_index = inputs["args_mapping"].index("FutGen|sm_radio_type")
                inputs["args_mapping"][sm_radio_band_index] = "sm_radio_type"

            radio_band_index = inputs["args_mapping"].index("radio_band")

            tmp_inputs = []
            for i in inputs["inputs"]:
                radio_band = i[radio_band_index]
                if get_sm_radio_band:
                    if radio_band == "24g":
                        sm_radio_band = "2.4G"
                    else:
                        sm_radio_band = radio_band.upper()
                    i = list(i)
                    i.insert(sm_radio_band_index, sm_radio_band)
                tmp_inputs.append(i)
            inputs["inputs"] = tmp_inputs
        return inputs

    def gen_sm_dynamic_noise_floor(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_sm_leaf_report(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_sm_neighbor_report(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)

    def gen_sm_survey_report(self, inputs):
        inputs = self._parse_sm_inputs(inputs)
        return self.default_gen(inputs)
