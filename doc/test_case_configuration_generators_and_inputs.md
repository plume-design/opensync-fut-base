# FUT test case configuration generators and inputs

The execution of FUT test cases requires both the **test case scenario** implemented in the `test/*_test.py` files and
input parameters, often referred to as **test case configuration parameters**. The test case configuration parameters
are generated automatically by feeding test case `configuration inputs` in `*_inputs.py` files into test case
`configuration generators` that expand these inputs into test case configuration parameters.

The test case `configuration generators` are located in `framework/generators` and the test case `configuration inputs`
are located in `config/test_case` and its subdirectories.

The generators also load platform and model specific inputs, should they exist, as well as the model properties file to
customize the input parameters for every specific device model.

## Generating the test case configuration parameters from configuration inputs

The generic test case configuration generator uses a template structure to define the test case generator inputs. The
**DefaultGen** class is used by default for all test case parameter generation. Optional **ModuleGen** files are used to
generate test case parameters in cases where additional logic is required and not supported by default generation.

The generic inputs are located in `config/test_case/generic/MODULE_inputs.py` files and are used in all cases, unless
specifics exist in platform specific `config/test_case/platform/MODULE_inputs.py` files or model specific
`config/test_case/model/MODULE_inputs.py` files.

### Single test case inputs

Let us assume the name of the test case of interest is **TESTNAME**.

Test case `configuration inputs` **without arguments** for a **single test case** would look like this:

```python
test_inputs = {
    "TESTNAME": {},
}
```

When the default test case configuration generator uses these inputs, the generated `configuration parameters` are:

```python
{
    "TESTNAME": [
        {},
    ]
}
```

The generated `configuration parameters` are shown in these examples as they are used directly by the `pytest files` for
each individual

### Using the args_mapping key

To add arguments to the test case inputs, use the `args_mapping` option. This is a list of keys to which the values in
the `inputs` are mapped when generating configuration parameters.

Configuration **inputs**:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "animal",
            "favorite_thing",
        ],
        "inputs": [
            ["cat", "sleep"],
            ["dog", "human"],
            ["dog", 10],
        ],
    },
}
```

Generated **configuration parameters**:

```python
{
    "TESTNAME": [
        {
            "animal": "cat",
            "favorite_thing": "sleep",
        },
        {
            "animal": "dog",
            "favorite_thing": "human",
        },
        {
            "animal": "dog",
            "favorite_thing": 10,
        },
    ],
}
```

### Using the default key

To add arguments to the test case inputs, use the `args_mapping` option. This is a list of keys to which the values in
the `inputs` are mapped when generating configuration parameters.

Configuration **inputs**:

```python
test_inputs = {
    "TESTNAME": {
        "default": {
            "pet": True,
        },
        "args_mapping": [
            "animal",
            "favorite_thing",
        ],
        "inputs": [
            ["cat", "sleep"],
            ["dog", "human"],
        ],
    },
}
```

Generated **configuration parameters**:

```python
{
    "TESTNAME": [
        {
            "animal": "cat",
            "favorite_thing": "sleep",
            "pet": True,
        },
        {
            "animal": "dog",
            "favorite_thing": "human",
            "pet": True,
        },
    ],
}
```

### Using fixed dictionaries

To define parameters for each individual test case configuration explicitly, provide a **list of dictionaries** to the
`inputs` key without using the `args_mapping` key. This is sometimes used for more fine grained control over individual
test case configurations, for example when ignoring something for specific platforms or models.

Configuration **inputs**:

```python
test_inputs = {
    "TESTNAME": {
        "inputs": [
            {
                "color": "red",
                "temperature": "hot",
            },
            {
                "color": "blue",
                "temperature": "cold",
            },
        ],
    },
}
```

Generated **configuration parameters**:

```python
{
    "TESTNAME": [
        {
            "color": "red",
            "temperature": "hot",
        },
        {
            "color": "blue",
            "temperature": "cold",
        },
    ]
}
```

### Custom generators

Some test cases may require generation of test case parameters using only model_properties files, with empty test case
configuration inputs. This would normally generate empty configuration parameters unless custom generators are used.

To implement a custom generator for **TESTNAME**, we first need to create a file `framework/generators/MymoduleGen.py`
for the suite of tests called `Mymodule`. A template file is provided, that should be copied and its content modified.

```shell
cp ./fut-base/framework/generators/TemplateGen.py ./fut-base/framework/generators/MymoduleGen.py
```

Change the `Template` and `template` inside **MymoduleGen.py** to match the test suite name `Mymodule` and `mymodule`:

```python
class MymoduleGen:

    def gen_testname(self, inputs):
        return inputs
```

In this example, the test case **testname** will use the custom generator function `gen_testname` to produce the
configuration inputs. The function has no additional logic, but we can imagine a case, where a value is needed from the
model_properties file, and used to produce the configuration inputs:

```python
def gen_testname (self, inputs):
    configs = []
    for mtu_type, mtu_value in self.gw_capabilities.get("mtu").items():
        configs.append({
            "mtu_type": mtu_type,
            "mtu_value": mtu_value,
        })
    return configs
```

Generated **configuration parameters** for the test case **TESTNAME**:

```python
{
    "TESTNAME": [
        {
            "mtu_type": "backhaul",
            "mtu_value": 1600
        },
        {
            "mtu_type": "uplink_gre",
            "mtu_value": 1562
        },
        {
            "mtu_type": "wan",
            "mtu_value": 1500
        }
    ]
}
```

### FutGen flags

In some test cases, input values are needed based on the values from the model_properties file, or simply require
additional parameter generation, that is useful across many test cases and is therefore reusable. For example interface
names depend on the radio band, as well as the interface `role`, like `home_ap`, `onboard_ap` or `fhaul_ap`.

To generate these values, the notation `FutGen|generator_function_name` is used as one of the values in the `inputs`
list. that corresponds to the desired configuration parameter for this test case. The string from this notation is used
to determine which part of the code defined in **\_parse_module_inputs()** method of the **ModuleGen** class is
executed.

Let us look at an example in the `NM` test suite. The `_parse_nm_inputs` method of the `NmGen` class implements several
ways to generate test case inputs, based on the `FutGen` value. One of them is the
`FutGen|primary-interface-if-name-type` which returns the interface name for either the primary `lan` or `wan` ethernet
interface of that device from the model_properties file. This value is used in several test cases in the `NM` suite, but
also elsewhere like the `ONBRD` suite.

The generator function in this case looks very simple, since the implementation is done inside `_parse_nm_inputs`:

```python
def gen_testname (self, inputs):
    inputs = self._parse_nm_inputs(inputs)
    return self.default_gen(inputs)
```

Configuration **inputs**:

```python
test_inputs = {
    "TESTNAME": {
        "default": {
            "broadcast": "10.10.10.255",
        },
        "inputs": [
            {"FutGen|primary-interface-if-name-type": "lan"},
            {"FutGen|primary-interface-if-name-type": "wan"},
        ],
    },
}
```

Generated **configuration parameters** (example interface names):

```python
{
    "TESTNAME": [
        {
            "broadcast": "10.10.10.255",
            "if_name": "eth0",  # primary_lan_interface
            "if_type": "eth",
        },
        {
            "broadcast": "10.10.10.255",
            "if_name": "eth1",  # primary_wan_interface
            "if_type": "eth",
        },
    ],
}
```

Here are configuration **inputs** for another example that uses `args_mapping`:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "channel", "ht_mode", "radio_band", "if_name", "if_type",
        ],
        "inputs": [
            [1, "HT20", "24g", "FutGen|vif-home-ap-by-band-and-type"],
            [1, "HT20", "6g", "FutGen|vif-bhaul-sta-by-band-and-type"],
        ]
    },
}
```

Generated **configuration parameters** (example interface names):

```python
{
    "TESTNAME": [
        {
            "channel": 1,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "if_name": "home-ap-24",
            "if_type": "vif",
        },
        {
            "channel": 1,
            "ht_mode": "HT20",
            "radio_band": "6g",
            "if_name": "bhaul-sta-60",
            "if_type": "vif",
        },
    ],
}
```

### Using the additional_inputs key

It is possible to define the configuration inputs in `platform` and `model` specific files in the same format as the
files in the `generic` directory, and in that case, they are simply overwritten. The most common use case however is to
**add the inputs** for that `platform` and `model` to the existing generic inputs with the `additional_inputs` key.

Default configuration **inputs**:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "breakfast",
        ],
        "inputs": [
            "apple",
            "coffee",
            "muffin",
        ],
    },
}
```

Configuration **inputs** for model `MYMODEL`:

```python
test_inputs = {
    "TESTNAME": {
        "additional_inputs": [
            "eggs",
        ],
    },
}
```

The generated **configuration parameters** for a different model that does not have specific configuration inputs:

```python
{
    "TESTNAME": [
        {
            "breakfast": "apple",
        },
        {
            "breakfast": "coffee",
        },
        {
            "breakfast": "muffin",
        },
    ],
}
```

The generated **configuration parameters** for model `MYMODEL` contains the additional value:

```python
{
    "TESTNAME": [
        {
            "breakfast": "apple",
        },
        {
            "breakfast": "coffee",
        },
        {
            "breakfast": "eggs",
        },
        {
            "breakfast": "muffin",
        },
    ],
}
```

## Features

The generic configuration inputs are sometimes defined for all possible combinations of device capabilities to be as
generic as possible. The main example of this are the **supported radio bands**. Possibilities cover all possible bands
for both dual and tri band devices: `24g`, `5g` or `5gl` and `5gu`, `6g`.

While using the **args_mapping** key for inputs with all possible bands defined, the model_properties file is checked
which bands are actually supported, and the unsupported inputs are not used to generate the configuration parameters. A
channel compatibility check is also performed, using the device regulatory_domain value from the model_properties file
and verifying configuration inputs against the `rules/regulatory.py` file.

If `radio_band` is present in `args_mapping`, the generator checks supported bands.

The relevant section from the model_properties file for model `MYMODEL`:

```yaml
regulatory_domain: US
radio_channels:
  24g: [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ]
  5g: null
  5gl: [ 36, 40, 44, 48, 52, 56, 60, 64 ]
  5gu: [ 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165, 169, 173, 177 ]
  6g: null
```

The configuration **inputs** for model `MYMODEL`:

```python
{
    "TESTNAME": {
        "args_mapping": [
            "radio_band",
        ],
        "inputs": [
            ["24g"],
            ["5gl"],
            ["5gu"],
            ["6g"],
        ],
    },
}
```

The generated **configuration parameters** for model `MYMODEL` contain only the supported bands:

```python
{
    "TESTNAME": [
        {
            "radio_band": "24g",
        },
        {
            "radio_band": "5gl",
        },
        {
            "radio_band": "5gu",
        },
    ],
}
```

If `radio_band`, `channel` and `ht_mode` are present in `args_mapping`, the generator checks compatibility of all three.

The configuration **inputs** for model `MYMODEL`:

```python
{
    "TESTNAME": {
        "args_mapping": [
            "radio_band", "channel"
        ],
        "inputs": [
            ["24g", 13],
            ["5gl", 40],
            ["5gu", 10],
            ["6g", 1],
        ]
    },
}
```

The generated **configuration parameters** for model `MYMODEL` contain only the supported combinations:

```python
{
    "TESTNAME": [
        {
            "radio_band": "5gl",
            "channel": 44,
        },
    ],
}
```

In the above example, band `6g` is unsupported by `mymodel`, `channel 13` is invalid in the `US regulatory domain` and
`channel 10` is invalid for the `5gu` band.

## Ignoring, skipping and marking tests with xfail

The generators support special keys `skip` and `xfail` from the `pytest` framework and a special key `ignore` custom to
the FUT framework. The keys can be applied to an entire test case or individual test case configurations. By using the
`msg` key in the dictionary of any of these three keys, a custom message can be logged or shown in the final report.

The `skip` key causes the test case to be collected by pytest, but execution will be skipped. The report will show the
test case in the `skipped` category.

The `xfail` key causes the test case to be collected and executed normally by pytest, but modifies the reporting of the
test results. If the test case succeeds, the report will show the test case in the `passed` category and pytest will
internally use the `xpass` category. If the test case fails, the report will show the test case in the `skipped`
category and pytest will internally use the `xfail` category. This is useful for flaky tests that should not contribute
to test failures, but should still be executed if they perhaps pass.

The `ignore` key causes the test case to be ignored while pytest is in the collection phase. This is useful for
excluding test cases explicitly for certain models, platforms or under specific conditions while isolating an issue.

Let us observe some examples. The configuration **inputs** in the `generic` folder:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "channel", "ht_mode", "radio_band",
        ],
        "inputs": [
            [6, "HT20", "24g"],
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT20", "6g"],
        ],
    },
}
```

The generated **configuration parameters** for a tri-band device:

```python
{
    "TESTNAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu"
        }
    ]
}
```

If some model creates specific configuration **inputs** with the `ignore` flag, the **configuration parameters** for
that model will not be generated:

```python
test_inputs = {
    "TESTNAME": {
        "ignore": {
            "msg": "Test case failing"
        }
    },
}
```

If the same model creates specific configuration **inputs** with the `skip` flag:

```python
test_inputs = {
    "TESTNAME": {
        "skip": {
            "msg": "Test case not required"
        }
    },
}
```

The generated **configuration parameters** for that model will be collected by pytest but the tests will not run:

```python
{
    "TESTNAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "skip": True,
            "skip_msg": "Test case not required"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "skip": True,
            "skip_msg": "Test case not required"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu",
            "skip": True,
            "skip_msg": "Test case not required"
        }
    ]
}
```

If the same model creates specific configuration **inputs** with the `xfail` flag, but also only targets two entries:

```python
test_inputs = {
    "TESTNAME": {
        "xfail": {
            "inputs": [
                [44, "HT40", "5gl"],
                [157, "HT40", "5gu"],
            ],
            "msg": "Test case may not pass"
        },
    },
}
```

The generated **configuration parameters** for that model will be collected and executed by pytest but the two test
configurations that were marked with `xfail` will be marked as `skipped` if the test result is a `failure` or as
`passed` if the test result is a `pass`:

```python
{
    "TESTNAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "xfail": True,
            "xfail_msg": "Test case may not pass"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu",
            "xfail": True,
            "xfail_msg": "Test case may not pass"
        }
    ]
}
```
