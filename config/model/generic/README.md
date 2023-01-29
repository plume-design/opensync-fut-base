# Generic FUT test configuration generator

## Overview

FUT is automatically generating test configurations based on model's
capabilities file. The generator is aware of the DUT and REF device
capabilities and based on their capabilities, it generates appropriate FUT
testcase configuration for given devices.

## Requirements

Since FUT generator is dependent on model capabilities files, it is required
for the model capabilities file being present in appropriate path for both DUT
and REF OSRT devices.

Configuration should be stored in:

```shell
./fut-base/config/model_properties/reference/MODEL-NAME.yaml
```

For models added by vendor, **internal** instead of **reference** directory
could be used, e.g.:

```shell
./fut-base/config/model_properties/internal/MODEL-NAME.yaml
```

## Optional requirements

Some devices could require some **additional test inputs** being present or
some of pre-generated test configurations to be **skipped**, **ignored** or
marked as **xfail**. In order to achieve this, FUT model configuration should
be added into FUT model configuration path

```shell
./fut-base/config/model/MODEL-NAME/inputs/
```

Note that **MODEL-NAME** should match the **MODEL-NAME** for device
capabilities `.yaml` file. For `PP203X` device the model capabilities file is
named `pp203x.yaml`.

## Workflow for generating the testcase configuration files

Generic test generator uses custom templating structure for definition of the
test inputs.

Generation of generic test inputs happens in

```shell
./fut-base/config/model/generic/generators/
```

where we define **DefaultGen** class for default generation and additional
**ModuleGen** files where we define generation of the testcases which require
additional logic not supported by default generation.

Main test inputs are defined in

```shell
./fut-base/config/model/generic/inputs/
```

in **MODULE_inputs.py** files.

### Defining test inputs using default generation

We will use **TEST-NAME** for example test name.

#### Single test inputs

Input definition:

```python
test_inputs = {
    'TEST-NAME': {},
}
```

Result:

```python
{
    'TEST-NAME': [
        {},
    ]
}
```

#### Using args_mapping

**args_mapping** option is used to define mapping of each input element entry
defined in
**inputs** to which key

Input definition:

```python
test_inputs = {
    'TEST-NAME': {
        'args_mapping': [
            'first_key_name', 'second_key_name'
        ],
        'inputs': [
            ['first_value_1', 'second_value_1'],
            ['first_value_2', 'second_value_2'],
            ['first_value_2', 10],
        ],
    },
}
```

Result:

```python
{
    "TEST-NAME": [
        {
            "first_key_name": "first_value_1",
            "second_key_name": "second_value_1"
        },
        {
            "first_key_name": "first_value_2",
            "second_key_name": "second_value_2"
        },
        {
            "first_key_name": "first_value_2",
            "second_key_name": 10
        }
    ]
}
```

### Using fixed dictionaries

Input definition:

```python
test_inputs = {
    'TEST-NAME': {
        'inputs': [
            {
                'key_name_1': 'key_value_1',
                'key_name_2': 'key_value_2',
            },
            {
                'key_name_1': 'key_value_1',
                'key_name_3': 'key_value_3',
            }
        ],
    },
}
```

Result:

```python
{
    "TEST-NAME": [
        {
            "key_name_1": "key_value_1",
            "key_name_2": "key_value_2"
        },
        {
            "key_name_1": "key_value_1",
            "key_name_3": "key_value_3"
        }
    ]
}
```

### Using custom generator

Some testcases can require test input generation using only device capabilities
file resulting in empty test inputs definition but with appropriate generator
override in

```shell
./fut-base/config/model/generic/generators/
```

To define custom generator for **TEST-NAME**, we first need to define and load
**NewGen**. To do so, we copy

```shell
./fut-base/config/model/generic/generators/TemplateGen.py
```

to

```shell
./fut-base/config/model/generic/generators/NewGen.py
```

and change the 'Template' and 'template' words inside **NewGen.py** to match
the test module name 'New' and 'new'.

`TemplateGen.py`

```python
class TemplateGen:
    @staticmethod
    def gen_template_test_inputs(inputs):
        return inputs
```

`NewGen.py`

```python
class NewGen:
    @staticmethod
    def gen_*

    # TEST - NAME > (inputs):

return inputs
```

Now, generation for test **TEST-NAME** will not use default generator rather the
generation we will define.

For example, if we need to take value from device capabilities file and create
configuration based on it, we can do that in following way:

```python
def gen_<


TEST - NAME > (self, inputs):
configs = []
for mtu_type, mtu_value in self.dut_gw_capabilities.get('mtu').items():
    configs.append({
        'mtu_type': mtu_type,
        'mtu_value': mtu_value,
    })

return configs
```

Result:

```python
{
    "TEST-NAME": [
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

#### Special FutGen flags

In some generations of test inputs, we require certain model capabilities
values, such as interface names. To access them, we use **FutGen** flags which
implementation is defined in **_parse_module_inputs()** methods which are
present in **ModuleGen** classes.

For example, in the cases where we need to access VIF home-ap interface name
based on radio_band relation, we use **FutGen|vif-home-ap-by-band-and-type**.

Given flag, looking at its implementation inside **NmGen** **_parse_nm_inputs**
we see that it returns VIF name for home_ap from device capabilities file for
given radio_band.

```python
# Definition in NmGen.py since it contains _parse_nm_inputs
# To use _parse_nm_inputs() method in other *Gen.py
# One should define _parse_nm_inputs as:
#
# from .NmGen import NmGen
# class NewGen:
#     def _parse_nm_inputs(self, inputs):
#         return NmGen._parse_nm_inputs(self, inputs)

def gen_<


TEST - NAME > (self, inputs):
inputs = self._parse_nm_inputs(inputs)
return self.default_gen(inputs)
```

Inputs:

```python
test_inputs = {
    'TEST-NAME': {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "if_name", "if_type",
        ],
        'inputs': [
            [6, "HT20", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
            [6, "HT20", "24g", 'FutGen|vif-bhaul-sta-by-band-and-type'],
        ]
    },
}
```

Result:

```python
{
    "TEST-NAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "if_name": "home-ap-24",
            "if_type": "vif"
        },
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "if_name": "bhaul-sta-24",
            "if_type": "vif"
        }
    ]
}
```

#### Special NM parsing

FutGen|eth-interfaces:

- Return **interfaces.lan_interfaces**

```python
# Input
{
    "TEST-NAME": {
        'inputs': [
            'FutGen|eth-interfaces',
        ]
    }
}
# Result
{
    "TEST-NAME": [
        {
            "if_name": "eth1",
            "if_type": "eth"
        },
        {
            "if_name": "eth0",
            "if_type": "eth"
        }
    ]
}
```

FutGen|eth-vif-interfaces:

- Return **interfaces.lan_interfaces**, **interfaces.phy_radio_name** and
  **interfaces.backhaul_sta**

```python
# Input
{
    "TEST-NAME": {
        'inputs': [
            'FutGen|eth-vif-interfaces',
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "if_name": "bhaul-sta-u50",
            "if_type": "vif"
        },
        {
            "if_name": "bhaul-sta-l50",
            "if_type": "vif"
        },
        {
            "if_name": "bhaul-sta-24",
            "if_type": "vif"
        },
        {
            "if_name": "wifi2",
            "if_type": "vif"
        },
        {
            "if_name": "wifi1",
            "if_type": "vif"
        },
        {
            "if_name": "wifi0",
            "if_type": "vif"
        },
        {
            "if_name": "eth1",
            "if_type": "eth"
        },
        {
            "if_name": "eth0",
            "if_type": "eth"
        }
    ]
}
```

FutGen|vif-phy-interfaces - Returns **interfaces.phy_radio_name**

```python
# Input
{
    "TEST-NAME": {
        'inputs': [
            'FutGen|vif-phy-interfaces',
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "if_name": "wifi2",
            "if_type": "vif"
        },
        {
            "if_name": "wifi1",
            "if_type": "vif"
        },
        {
            "if_name": "wifi0",
            "if_type": "vif"
        }
    ]
}
```

Following flags return VIF interface names from device capabilities file as
stated:

- FutGen|vif-home-ap-interfaces
- FutGen|vif-bhaul-sta-interfaces
- FutGen|vif-bhaul-ap-interfaces
- FutGen|vif-onboard-ap-interfaces

```python
# Input
{
    "TEST-NAME": {
        'inputs': [
            'FutGen|vif-home-ap-interfaces',
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "if_name": "home-ap-u50",
            "if_type": "vif"
        },
    ]
}
# Input
{
    "TEST-NAME": {
        'inputs': [
            'FutGen|vif-bhaul-sta-interfaces',
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "if_name": "bhaul-sta-u50",
            "if_type": "vif"
        },
    ]
}
# Same for bhaul-ap and onboard-ap
```

#### Special NM list inputs

Note:

- `args_mapping` entry is mandatory

FutGen|phy-if-by-band-and-type - Return **interfaces.phy_radio_name** for
specific radio_band

```python
# Input
{
    'args_mapping': [
        "radio_band", "if_name", "if_type",
    ],
    'inputs': [
        ["24g", 'FutGen|phy-if-by-band-and-type'],
        ["5gl", 'FutGen|phy-if-by-band-and-type'],
    ]
}
# Result
{
    "TEST-NAME": [
        {
            "radio_band": "24g",
            "if_name": "wifi0",
            "if_type": "vif"
        },
        {
            "radio_band": "5gl",
            "if_name": "wifi1",
            "if_type": "vif"
        }
    ]
}
```

FutGen|vif-home-ap-by-band-and-type - Return **interfaces.home_ap** for
specific radio_band.

```python
# Input
{
    'args_mapping': [
        "radio_band", "if_name", "if_type",
    ],
    'inputs': [
        ["24g", 'FutGen|vif-home-ap-by-band-and-type'],
        ["5gl", 'FutGen|vif-home-ap-by-band-and-type'],
    ]
}
# Result
{
    "TEST-NAME": [
        {
            "radio_band": "24g",
            "if_name": "home-ap-24",
            "if_type": "vif"
        },
        {
            "radio_band": "5gl",
            "if_name": "home-ap-l50",
            "if_type": "vif"
        }
    ]
}
```

## Additional features

While using **args_mapping** method, there are some additional checks which
occur depending on device capabilities. Channel compatibility check is also
done against device regulatory_domain from capabilities file.

- If **radio_band** in args_mapping, generator checks if given radio band is
  supported.

```python
# Device supports only 24g, 5gl and 5gu radio_band-s
# Input
{
    "TEST-NAME": {
        'args_mapping': [
            "radio_band",
        ],
        'inputs': [
            ["24g"],
            ["5gl"],
            ["5gu"],
            ["6g"],
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "radio_band": "24g"
        },
        {
            "radio_band": "5gl"
        },
        {
            "radio_band": "5gu"
        }
    ]
}
```

- If **radio_band** and **channel** in args_mapping, generator checks the
  radio_band - channel compatibility.

```python
# Input
{
    "TEST-NAME": {
        'args_mapping': [
            "radio_band", "channel"
        ],
        'inputs': [
            ["24g", 5],
            ["5gl", 44],
            ["5gu", 10],
            ["6g", 1],
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "radio_band": "24g",
            "channel": 5
        },
        {
            "radio_band": "5gl",
            "channel": 44
        }
    ]
}
# WARN [FRM] Incorrect combination of parameters: channel:10, ht_mode:HT20, band:5gu, regulatory domain: US
```

- If **radio_band** and **channels** in args_mapping, generator checks the
  radio_band - channel compatibility.

```python
# Input
{
    "TEST-NAME": {
        'args_mapping': [
            "radio_band", "channels"
        ],
        'inputs': [
            ["24g", [5, 6, 13]],
            ["5gl", [44, 39]],
            ["5gu", [1, 10, 157]],
            ["6g", [1]],
        ]
    },
}
# Result
{
    "TEST-NAME": [
        {
            "radio_band": "24g",
            "channels": [
                5,
                6
            ]
        },
        {
            "radio_band": "5gl",
            "channels": [
                44
            ]
        },
        {
            "radio_band": "5gu",
            "channels": [
                157
            ]
        }
    ]
}
# WARN [FRM] Incorrect combination of parameters: channel:13, ht_mode:HT20, band:24g, regulatory domain: US
# WARN [FRM] Channel 13 is not valid for 24g for set regulatory domain of US
# WARN [FRM] Incorrect combination of parameters: channel:39, ht_mode:HT20, band:5gl, regulatory domain: US
# WARN [FRM] Channel 39 is not valid for 5gl for set regulatory domain of US
# WARN [FRM] Incorrect combination of parameters: channel:1, ht_mode:HT20, band:5gu, regulatory domain: US
# WARN [FRM] Channel 1 is not valid for 5gu for set regulatory domain of US
# WARN [FRM] Incorrect combination of parameters: channel:10, ht_mode:HT20, band:5gu, regulatory domain: US
# WARN [FRM] Channel 10 is not valid for 5gu for set regulatory domain of US
```

## Ignoring, skipping and marking tests with xfail

Generator supports marking tests per FUT device configuration with **ignore**,
**skip** or **xfail**. To mark test with one of the flags, entry in FUT device
configuration should be the following:

Using TEST-DEVICE as device name. Using TEST-NAME as testcase name.

```python
# fut-base/config/model/generic/inputs/TEST_inputs.py
test_inputs = {
    "TEST-NAME": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            [6, "HT20", "24g"],
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5g"],
            [157, "HT40", "5gu"],
            [5, "HT20", "6g"],
            [157, "HT20", "6g"],
        ],
    },
}
# Result
{
    "TEST-NAME": [
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
# fut-base/config/model/TEST-DEVICE/inputs/TEST_inputs.py
test_inputs = {
    "TEST-NAME": {
        'ignore': {
            'msg': 'Testcase failing'
        }
    },
}
# Result
{
    "TEST-NAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "ignore_collect": True,
            "ignore_collect_msg": "Testcase failing"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "ignore_collect": True,
            "ignore_collect_msg": "Testcase failing"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu",
            "ignore_collect": True,
            "ignore_collect_msg": "Testcase failing"
        }
    ]
}
# fut-base/config/model/TEST-DEVICE/inputs/TEST_inputs.py
test_inputs = {
    "TEST-NAME": {
        'skip': {
            'msg': 'Testcase not required'
        }
    },
}
# Result
{
    "TEST-NAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g",
            "skip": True,
            "skip_msg": "Testcase not required"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "skip": True,
            "skip_msg": "Testcase not required"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu",
            "skip": True,
            "skip_msg": "Testcase not required"
        }
    ]
}
```

One can ignore, skip or xfail single input as well.

```python
# fut-base/config/model/TEST-DEVICE/inputs/TEST_inputs.py
test_inputs = {
    "TEST-NAME": {
        'skip': {
            'input': [44, "HT40", "5gl"],
            'msg': 'Testcase not required'
        },
    },
}
# Result
{
    "TEST-NAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "skip": True,
            "skip_msg": "Testcase not required"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu"
        }
    ]
}
```

Or skip multiple entries with the same message.

```python
# fut-base/config/model/TEST-DEVICE/inputs/TEST_inputs.py
test_inputs = {
    "TEST-NAME": {
        'skip': {
            'inputs': [
                [44, "HT40", "5gl"],
                [157, "HT40", "5gu"],
            ],
            'msg': 'Testcase not required'
        },
    },
}
# Result
{
    "TEST-NAME": [
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5gl",
            "skip": True,
            "skip_msg": "Testcase not required"
        },
        {
            "channel": 157,
            "ht_mode": "HT40",
            "radio_band": "5gu",
            "skip": True,
            "skip_msg": "Testcase not required"
        }
    ]
}
```
