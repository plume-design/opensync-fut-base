# Functional Unit Testing

## Overview

Functional Unit Testing (FUT) verifies individual OpenSync manager
functionalities. FUT tests individual functional units on devices, without
the need for cloud management and full-scale end-to-end testing.

FUT operates at a higher level than pure unit testing of C source code, which
tests function calls and APIs of managers, tools, and libraries.

On the other hand, FUT operates at a lower level than end-to-end system testing,
which depends not only on OpenSync core code and device integration, but also
on cloud implementation, making it harder to pinpoint the source of the problem
when a test fails.

## Further reading

This readme provides basic information about the FUT environment. For a more
detailed explanation, refer to:

- **FUT Quick Start Guide**, available at [./doc/quick_start_guide.md](./doc/quick_start_guide.md)
- **FUT User Manual**, available at [./doc/fut_user_manual.md](./doc/fut_user_manual.md)

## Environment setup

FUT test scripts are implemented as individual shell scripts. They are intended
for execution on the Device Under Test (DUT). These scripts are executable
manually, and with minimal dependencies, like setup scripts and common
libraries. These scripts are all part of the code. You can execute the scripts
manually, providing only input parameters.

If you wish to execute the tests with the provided **FUT Python framework**,
run the tests from the RPI server device within the OSRT. By executing the
tests on an official OSRT, the execution environment is predefined and tested.
The framework is based on the python3 test library `pytest`, with an
additionally extended implementation.

## Quick start

The reference models for testing and verification of FUT scripts are provided
with the code. See the configurations in `config` directory. We use the `PP203X`
as an example. This model is also known as _Plume SuperPod_. This model will
be used here for demonstration purposes, along with the configuration files and
shell library overrides.

If you wish to adapt any reference configuration for another device model, and
the corresponding configuration files are not yet created:

1. Duplicate and rename the configuration directory of the reference model,
   or another suitable model.
2. Modify the content of configuration files to match the targeted device.

Go to section "Configuration files" for more details.

For easier use of FUT framework, the script `init.sh` wraps the pytest library
invocation, and provides the common FUT run commands. The script includes an
extensive help that details its use:

```bash
./init.sh -h
```

### Environment preparation

The shell test scripts and other scripts needed for FUT execution are provided
in separate git repos from the framework. This modular design helps both users
and developers perform their tasks more independently. The runner script can be
instructed to skip the unpacking of the shell tarball if the user has already
done so before, and if all the shell files are already in their final directory
`fut-base/shell`. To perform a full test run without attempting to unpack the
shell tarball from `resource/shell/*.tar.bz2`, execute:

```bash
./init.sh -noshunpack
```

Without this flag, the framework will attempt to unpack the shell tarball
`resource/shell/*.tar.bz2` into the directory `fut-base/shell` before the test
execution.

The default execution environment for FUT is controlled by a docker container.
Building the docker image for the first time can take a long time, possibly
exceeding one hour. Once built, the image and container are reused, thus
executing FUT more quickly.

There is an option to execute FUT natively on the system, without a docker
container. It is advised to only run FUT this way for debugging purposes,
not for actual testing.

```bash
./init.sh -nodocker
```

### Test execution

Use the runner script without input parameters to perform test execution of
all available and configured testcases. The tests are selected and configured
based on the DUT configuration directory setting. This is how you tell the
framework which per-device configuration files to read.

```bash
./init.sh
```

Use the runner script to only transfer the files to the devices in the OSRT,
without executing the tests. This feature is particularly useful if one wants
to manually run scripts on the device (e.g., when debugging).

```bash
./init.sh -tr
```

Use the runner script to expose the pytest markers facility. If used without
parameters, all available markers are listed - default and custom ones. If used
with input parameters, the markers provided are used for test execution and
filtering.

```bash
# List available markers
./init.sh -m
# Use a single marker or a boolean expression of several markers (use quotes)
./init.sh -m "require_dut"
./init.sh -m "require_dut and not dfs or require_rc"
```

### Collection and execution filtering

Use the runner script to specify the path to the pytest testcase definition
file(s), defaulting to `test/`. This way you can manipulate the collection of
test cases by providing only a select suite of testcases, determined by the
provided file(s). If several files are listed, use comma separated notation.

```bash
./init.sh -path test/NM_test.py
./init.sh -path test/UT_test.py,test/CM_test.py
```

Use the runner script to list all collected testcases for the selected
configuration with the `-l` flag. This is useful in combination with the `-r`
flag for specifying the list of testcases to execute, instead of all available
testcases (by default).

```bash
./init.sh -l
```

Use the runner script to list all available configurations for the selected
model. This is similar to the `-l` option, but prints each parametrized
testcase separately, instead of only once. For example, one testcase can be
executed several times with different input parameters. All options are listed
here.

```bash
./init.sh -c
```

Use the runner script with `-r` flag to define a subset of the default set of
testcases. Specify the testcase selection by names, or by names and input
parameter configuration. If specifying several testcases, use comma separated
notation (without spaces in between).

```bash
./init.sh -r test_foo
./init.sh -r test_bar[config_0]
./init.sh -r test_foo,test_bar,test_baz[config_0],test_baz[config_4]
```

### Debugging

When executing other processes (e.g., scripts), pytest normally captures
everything going to stdout and stderr for report generation and customizable
logging, therefore none of that is outputted to the terminal.

Use the runner script with the `-p` option to enable 'live logging' -- in this
mode all log messages as well as stdout/stderr of executed scripts are also
sent simultaneously to the terminal.

```bash
./init.sh -p
```

Use the runner script with the `-d` flag to enable the debug mode: increase
pytest logging verbosity level to debug and change the logging format to
provide more information. You can combine this flag with the `-p` flag to
enable both features simultaneously.

```bash
./init.sh -d
```

Use the runner script option `-o` to disable pytest capture of stdout and
stderr, and let the output go directly to the terminal. This can be helpful
when developing or troubleshooting a testcase.
Note however that since the output is not captured, it will be missing from the
results (and from the report, if one is generated).

```bash
./init.sh -o
```

This option can also be combined with the `-d` flag for additional verbosity.

### Reporting

Use the runner script to collect and execute all available tests configured for
the selected model, and also generate pytest results in the `allure` package
friendly format. The results are stored in the specified directory.

```bash
./init.sh -allure allure-results
```

The `allure` package visualizes the FUT test execution results. Generating and
viewing the report (not to be confused with the results) is out of scope for
this document. See [**FUT User Manual**](./doc/fut_user_manual.md) for
instructions.

## Configuration files

The FUT framework allows you to configure testcase execution without the need
to change any test shell scripts. There are several editable configuration
files that serve as inputs for both - FUT framework and shell test scripts.
Configure these files as needed.

The configuration files are grouped into three types:

- **testbed:** general settings applicable to the specific testbed instance,
  for example: username and password, management IP, configuration directory
  name
- **device:** per-model, device-specific information, for example: regulatory
  domain information, radio interface names and bands, model string
- **testcase:** a set of per-model files, each containing input parameters
  for a suite of shell test scripts

Configuration files are `yaml` files, loaded by the FUT framework.

This is the directory structure:

```plaintext
fut-base/config/
├── model
│   └── PP203X
│       └── testcase
│           └── <suite_name>_config.py
├── model_properties
│   └── reference
│       └── pp203x.yaml
├── rules
│   ├── fut_version_map.yaml
│   └── regulatory.yaml
└── testbed
    └── config.yaml
```

### Testbed configuration

FUT framework can not be generalized in advance to work with the cases, in
which the device models and configurations vary widely. Providing information
about the testbed setup is essential. The testbed configuration file location
is `config/testbed/config.yaml`.

The parameters in the testbed configuration file are applicable to the devices
present in the testbed. They define how to configure and access the testbed
devices.

### Device configuration

The device configuration files contain device-specific (per-model) information,
required for successful test parametrization. The configuration is located in
the following file: `config/model_properties/reference/<my_model>.yaml`. This
file includes information about radio interface names and bands, regulatory
domain information, model string, etc.

If some configuration entries are not applicable for your particular device
model, the value should be set to `null`.

### Testcase configuration

Directory `config/model/<my_model>/testcase/` contains configuration files
with the filename format `<suite_name>_config.py`. Each of the configuration
files contains settings specific for one suite of tests, defined in the
corresponding pytest script `test/<suite_name>_test.py`. For example, here are
the configuration and pytest test collection scripts, both corresponding to
`NM` (_Network Manager_):

```bash
./config/model/<my_model>/testcase/NM_config.yaml
./test/NM_test.py
```

See below a demonstrative example of the content for one of the testcase
suites. Names and values are symbolic.

```python
test_cfg = {
    "simple_testcase_without_config": [
        {},
    ],
    "echo_input_parameter_to_stdout": {
        "input_parameter": "Hello world!",
        "test_script_timeout": 42  # Timeout after 42 seconds
    },
    "test_in_development": {
        "value" : 42,
        "skip": True,
        "skip_msg": "Test implementation pending"
    },
    ...
}
```

## Developer notes

FUT test scripts, framework and configuration files are designed to allow the
users of FUT tests to validate their contributions to OpenSync. The existing
testcases need to be executable without modification. This means that the
**user of FUT tests** is the one who provides the input parameters and runs the
existing tests, while it is not necessary to develop new scripts or change the
source code.

**Developers of FUT test cases** and **writers of FUT shell scripts** on the
other hand are those who create the testcase definitions, and design and
implement the test script. It is ideal for the developers of new OpenSync
features to be the ones who also provide the definitions of test cases, and
design and implement the shell script due to their knowledge of the feature.

### Basic FUT postulates

1. **Shell scripts are atomic.** The user must be able to manually execute the
   test shell scripts, and execute or source setup scripts and shared
   libraries, provided that input parameters are known. This both separates the
   testcase implementation in shell from the FUT framework assistive
   facilities, as well as lower the barrier for entry to developers of new test
   scripts.
2. **Code is modular.** Use of shared shell libraries and common functions is
   encouraged. This makes testcases more flexible if some functions in the test
   script must be overloaded due to the unique per-model properties.
3. **Code is portable.** Test scripts, common libraries, and shell functions
   must be implemented in such a way, that correct code execution is possible
   on several device models, despite the differences in execution environments.
   This can be achieved by making test procedures modular and functions
   overloadable. This creates the opportunity to specialize certain function
   calls in the `lib/override` directory.
4. **Framework should only assist the user.** There must be no testcase
   implementation in Python, only shell is allowed. The test shell scripts
   should be executable and fully functional without the FUT framework.
   The framework should only make it easier to execute the tests en-masse,
   by handling the management ssh, copying files, collecting results, and
   generating the reports.

### Development process

To reduce the entry barrier for developers who wish to contribute the testcases
and implement the shell scripts, **developers must provide:**

1. _Definition of the testcase:_ listed dependencies and environment specifics,
   inputs and expected outputs and behavior.
2. _Test shell script_, including code comments, input parameter explanation.
3. _Example of use_, like invocation with example input parameters.

Once the test script is developed and is executable on the device, the FUT
framework can be extended with new features if needed, and adapted to execute
the new testcase. The testcase configuration entries are created, and test
execution with the framework is verified.

The following sections detail the individual stages of the development process.

#### Testcase definition

The testcase definition is the first step of developing a new FUT testcase,
because it is the _"source of truth"_ throughout the entire development
process. In all future conflicts, for example discovered bugs in the test
script implementation, the testcase definition is the reference, and others
have to change or adapt.

This makes the testcase definition of paramount importance from the start, and
must be executed flawlessly. Any change in the definition must result in a
restart of the entire process.

The testcase definition is done in writing, either in bullet points or
descriptively. The definition should contain, depending on actual testcase:

- Description of the environment, necessary for testing
- Description of the subject of testing: _what is being tested_
- All the setup steps or prerequisites needed _before_ the test is executed
- The actual test steps (one or more)
- Definition of expected results after each step
- Any teardown steps needed _after_ the test (e.g., for cleanup)

To make the contributions as simple as possible, test definitions are available
as `Markdown` files in the [./doc/definitions/](./doc/definitions/) directory,
where one can find multiple directories, which group testcase definitions by the
OpenSync manager that is tested, or by some other distinct criteria.

Here is an example. The testcase name is **entity_tool_present_on_device**. The
definition for such a testcase might look like this:

```md
# Testcase entity_tool_present_on_device

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that the selected tool required for
executing the FUT testcases is present on the device and discoverable on the
PATH.

## Expected outcome and pass criteria

The tool checked is present on the device and is discoverable on the PATH.
```

#### Shell script design and implementation

Before starting to write code, a _test script design_ should be created. In
this step, the developer takes the testcase definition and adds implementation
details that will result in the final implemented test script.

During implementation, the test shell scripts must be completed with code
comments, input parameter explanations, and examples of use like invocation
with example input parameters. Optionally, setup and teardown step requirements
are listed.

Logging helps to record what occurred during the execution of a shell script:

1. Testcase files use only "log" function for all logging. This will be
   manipulated by the framework and added into reports.
2. Shell library files use "log" function only for "function title messages",
   that announce the usage and purpose of the function at the beginning of the
   function.
3. Shell library files use "log -deb" function for all logging other than
   function title messages. This will be shown in the test reports if the debug
   level logging was configured at the start of test execution.

Let us continue with the example from the previous chapter. The test script
design is noted in the team collaboration software tools. Here, we skip to the
script implementation.

For future testcase grouping, let us also define the suite of tests, named
_Entity_ tests. Therefore we prepend our filenames accordingly, and place them
inside the `shell/tests/entity` directory.

There are two steps: the **setup** and the **test** step. The setup script
`shell/tests/entity/entity_setup.sh` ensures that the _prerequisites_ from
the testcase definition are met. The script might look like this:

```bash
#!/bin/sh

# FUT environment loading
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/entity_lib.sh"
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "" -olfm

entity_setup_env &&
    log "entity/entity_setup.sh: entity_setup_env - Success " ||
    raise "entity_setup_env - Failed" -l "entity/entity_setup.sh" -ds

exit 0
```

You may have noticed that there is a call to source the `lib/entity_lib.sh`
script. This common script should contain all the functions that several test
scripts might want to share and reuse. You may have also noticed that the only
function call is to `entity_setup_env`, which coincidentally is implemented
inside the `lib/entity_lib.sh` script. Here is how this script might look like:

```bash
#!/bin/sh

# FUT environment loading
export FUT_ENTITY_LIB_SRC=true
[ "${FUT_BASE_LIB_SRC}" != true ] && source "${FUT_TOPDIR}/shell/lib/base_lib.sh"
echo "${FUT_TOPDIR}/shell/lib/entity_lib.sh sourced"

check_isnot_sudo()
{
    sudo -l -U $USER | egrep -q 'not allowed to run sudo'
    rv=$?
    return $rv
}

entity_setup_env()
{
    log "entity_lib:entity_setup_env - Running ENTITY setup"

    # Ensure administrative or sudo privilege on device
    check_isnot_sudo &&
        raise "$USER lacks sudo privilege" -l "entity_lib:entity_setup_env" -ds

    return 0
}

is_tool_on_system()
{
    command -v $1
    return $?
}
```

The code above is a good example of library functions that can be overridden.
The function `entity_setup_env` is called by the setup script, and inside it
there is a call to another function `check_isnot_sudo`, which may be implemented
differently on another model or platform. In that case, the user can override
any default function in a file `lib/override/<my_device>_lib_override.sh`.

The test script contains the actual test steps, outlined in the testcase
definition. The filename is for example
`shell/tests/entity/entity_tool_present_on_device.sh` and the script might
look like this:

```bash
#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/entity_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
entity/entity_tool_present_on_device.sh [-h] tool_name
Options:
    -h  show this help message
Arguments:
    \$1  (tool_name)      : tool name to be checked - (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./entity/entity_setup.sh
                 Run: ./entity/entity_tool_present_on_device.sh <tool-name>
Script usage example:
    ./entity/entity_tool_present_on_device.sh "ls"
    ./entity/entity_tool_present_on_device.sh "bc"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "entity/entity_tool_present_on_device.sh" -arg
tool_name=${1}

log_title "entity/entity_tool_present_on_device.sh: Verify tool ${tool_name} is present on device"

is_tool_on_system ${tool_name} &&
    log "entity/entity_tool_present_on_device.sh: tool ${tool_name} present on device - Success" ||
    raise "FAIL: tool ${tool_name} not present on device" -l "entity/entity_tool_present_on_device.sh" -tc

pass
```

After all the shell scripts are created, they should be manually executable and
should `pass`. The job of the developer may end here, and the FUT maintainers
may take over the steps that follow, or the developer may choose to continue by
themselves.

#### Framework integration and configuration creation

The framework is based around the testing library for python3 `pytest`.
Therefore, you must create a _"test suite"_ file. This file uses pytest
fixtures to define the testcases, and exposes them to the user.

To create a new suite of tests named `ENTITY`, create `ENTITY_test.py` inside
the directory `test/`. This file is a pytest wrapper that maps shell
scripts to pytest _testcases_. The pytest file should have the following
content:

```python
import framework.tools.logger
from framework.tools.functions import get_command_arguments
from framework.tools.functions import step
from .globals import ExpectedShellResult
from .globals import SERVER_HANDLER_GLOBAL
import pytest
import allure

# Read entire testcase configuration
entity_config = SERVER_HANDLER_GLOBAL.get_test_config(cfg_file_prefix='ENTITY')

@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.dut_setup()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.dependency(name="entity_fut_setup_dut", depends=["compat_dut_ready"], scope='session')
def test_entity_fut_setup_dut():
    server_handler, dut_handler = pytest.server_handler, pytest.dut_handler
    with step('Transfer'):
        assert dut_handler.clear_tests_folder()
        assert dut_handler.transfer(manager='entity')
    server_handler.recipe.clear_full()
    with step('ENTITY setup'):
        assert dut_handler.run('tests/entity/entity_setup', dut_handler.get_if_names(True)) == ExpectedShellResult
    server_handler.recipe.mark_setup()


########################################################################################################################
test_entity_tool_present_on_device_inputs = entity_config.get('entity_tool_present_on_device', [])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.require_dut()
@pytest.mark.os_integration_m2()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_entity_tool_present_on_device_inputs)
@pytest.mark.dependency(depends=["wm2_fut_setup_dut"], scope='session')
def test_entity_tool_present_on_device(test_config):
    dut_handler = pytest.dut_handler
    tool_name = test_config.get('tool_name')
    test_args = get_command_arguments(tool_name)
    with step('Testcase'):
        assert dut_handler.run('entity/entity_tool_present_on_device', test_args) == ExpectedShellResult
```

There is a lot going on in the example above. The first important aspect is the
so called "module fixture" `entity_initial_setup`. This is the way in which the
FUT framework replaces manually transferring all files to device(s), and
running the setup script as initialization. The setup script is only run once
if the user wishes to run several testcases sequentially, thus saving the
overhead time.

The second important part is the testcase function definition
`test_entity_tool_present_on_device`. If the function name starts with `test_`,
pytest automatically collects it as an available testcase. Within the function,
there is the input argument collection, and then the remote execution of test
shell script on the device, where the correct result is asserted.

The third important part is configuration collection and test function
parametrization. The variable `entity_config` contains all the input parameters
for all test functions, including our example
`test_entity_tool_present_on_device`. These input arguments are collected from
the _testcase configuration file_, as explained in the previous section.

All other pytest or Allure decorators are also required. See other code
examples to determine which markers are needed for a newly added test function.

Here is how you add a testcase configuration file, or a testcase configuration
entry to an existing file. In directory `config/model/<my_model>/testcase/`,
create a file `ENTITY_config.py`. The file content might look like this:

```python
test_cfg = {
    "entity_tool_present_on_device": [
        {
            "tool_name": "ifconfig",
        },
    ],
    ...
}
```

If the testcase definition requires the use of several tools, you can achieve
this without changing any testcase or framework implementation. Pytest
parametrization (`@pytest.mark.parametrize`) enables the user to quickly add
configurations to the testcase config file:

```python
test_cfg = {
    "entity_tool_present_on_device": [
        {
            "tool_name": "ifconfig",
        },
        {
            "tool_name": "echo",
        },
        {
            "tool_name": "ls",
        },
    ],
    ...
}
```

### Testing your work

This completes the entire integration process from start to finish. The user
can now verify the developed testcase as part of the entire test run,
individually, or as specified by the test configuration:

```bash
./init.sh  -r entity_tool_present_on_device
./init.sh  -r entity_tool_present_on_device[config_0],entity_tool_present_on_device[config_2]
```

## OpenSync resources

For further information please visit: <https://www.opensync.io/>
