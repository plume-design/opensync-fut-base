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
**DefaultGen** class is used by default for all test case parameter generation.

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

To add the same arguments to all the test case inputs, use the `default` option. This is a dict of key value pairs, that
is directly appended to the generated configuration parameters at the very end of the process.

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
`inputs` key without using the `args_mapping` key. This is sometimes used for more fine-grained control over individual
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
            ["5g"],
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
            ["5g", 40],
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

In the above example, bands `5g` and `6g` are unsupported by `mymodel`, `channel 13` is invalid in the `US regulatory
domain` and `channel 10` is invalid for the `5gu` band.

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

## Custom configuration keys

The generators also support special keys that govern how the test case inputs are treated and used to create the test
case configurations.

### Sorting

The `do_not_sort = True` key prevents sorting of the generated test case configurations. This is used when you wish to
explicitly determine the order of test case execution, due to advantageous test precedence. For example changing
channels and bandwidths between tests may be advantageous compared to changing bands for the same channel and bandwidth.

The configuration **inputs** may look like this:

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

The generated **configuration parameters** for a tri-band device will be sorted by the values in order. This means that
the `6g` config will be sorted first as its `channel` value is `5`, before the `24g` config with the `channel` value of
`6`:

```python
{
    "TESTNAME": [
        {
            "channel": 5,
            "ht_mode": "HT40",
            "radio_band": "6g"
        },
        {
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5g"
        }
    ]
}
```

However if the configuration **inputs** include `do_not_sort = True`:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "channel", "ht_mode", "radio_band",
        ],
        "do_not_sort": True,
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

The generated **configuration parameters** for a tri-band device will not be sorted by values and the `6g` config will
be configured last, as it appeared in the **inputs**:

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
            "radio_band": "5g"
        },
        {
            "channel": 5,
            "ht_mode": "HT40",
            "radio_band": "6g"
        }
    ]
}
```

### Expanding permutations

The `expand_permutations` key instructs the generators to create several test case **configurations** where individual
test case **inputs** contain a `list` or `set` of values, or a `tuple` that indicates a `range` of values.

**Note** that `tuples` should contain two elements for the start and end of the range, and both intervals are included
in the range, also the end interval.

The configuration **inputs** may look like this:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "channel", "ht_mode", "radio_band", "bcn_int",
        ],
        "expand_permutations": True,
        "inputs": [
            [6, "HT20", "24g", [100, 200, 400]],
            [44, "HT40", "5g", [100, 200, 400]],
            [44, "HT40", "5gl", [100, 200, 400]],
            [157, "HT40", "5gu", [100, 200, 400]],
            [5, "HT20", "6g", [100, 200, 400]],
        ],
    },
}
```

The generated **configuration parameters** for a tri-band device will contain an entry for each item in the list of
individual test inputs:

```python
{
    "TESTNAME": [
        {
            "bcn_int": 100,
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "bcn_int": 200,
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "bcn_int": 400,
            "channel": 6,
            "ht_mode": "HT20",
            "radio_band": "24g"
        },
        {
            "bcn_int": 100,
            "channel": 44,
            "ht_mode": "HT40",
            "radio_band": "5g"
        }
        ...
    ]
}
```

The configuration **inputs** can contain `tuples` indicating ranges of values, and can have several expandable values
for each test case input:

```python
test_inputs = {
    "TESTNAME": {
        "args_mapping": [
            "channel", "ht_mode", "radio_band", "number_of_clients", "encryption",
        ],
        "expand_permutations": True,
        "inputs": [
            [44, "HT40", "5g", (1, 3), {"WPA2", "WPA3"}],
        ],
    },
}
```

The generated **configuration parameters** for a tri-band device will contain combinations of entries for each item in
the list of individual test inputs and for each item in the range provided by the tuple:

```python
{
    "TESTNAME": [
        {
            "channel": 44,
            "encryption": "WPA2",
            "ht_mode": "HT40",
            "number_of_clients": 1,
            "radio_band": "5g"
        },
        {
            "channel": 44,
            "encryption": "WPA2",
            "ht_mode": "HT40",
            "number_of_clients": 2
            "radio_band": "5g"
        },
        {
            "channel": 44,
            "encryption": "WPA2",
            "ht_mode": "HT40",
            "number_of_clients": 3,
            "radio_band": "5g"
        },
        {
            "channel": 44,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "number_of_clients": 1,
            "radio_band": "5g"
        },
        {
            "channel": 44,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "number_of_clients": 2,
            "radio_band": "5g"
        },
        {
            "channel": 44,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "number_of_clients": 3,
            "radio_band": "5g"
        },
    ]
}
```
