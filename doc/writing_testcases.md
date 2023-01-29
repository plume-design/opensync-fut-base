# Writing FUT testcases: User guide

## Introduction

Deciding to write your own FUT tests promotes you from being a test executor to
a test contributor. Assuming you can run the FUT testcases, you already
have some knowledge about how the FUT and OSRT work, you should be able to
follow the presented guide.

In this document we will follow the "5-step process" from the Appendix A of this
document with as little deviation as possible. Some steps can be partially
omitted, since in this document we want to give a general feel about how to
write the testcases.

Writing new FUT testcases falls into two main categories:

- Adding a new testcase to the already existing test suite
- Adding a new, non-existing test suite

This guide covers both of these categories, starting with adding a new testcase
to the existing test suite.

In the first part of this guide you will add a new simple testcase to the
existing suite. The testcase will just verify the number of parameters fed into
the testcase script. Since we will not add a new suite, the existing DM
(_Diagnostic Manager_) suite will be used.

In the second part, the guide provides instructions on how to add a new test
suite.

## Prerequisites

Besides the access FUT-related sources, you need:

### Hardware

OSRT is required for the testcase execution. Details on how to set up your
testbed and testing environment are available in **EIN-020-022-501 OSRT Setup
Guide**.

### Experience

- Shell scripting
- Python
- Linux command line

### Useful resources

Before using the FUT testing environment, it is recommended to read the
**user_manual.md**.

Also recommended is to study the source files and available scripts. Before
writing your own testcases, read about the shell script styling, so your scripts
are in line with the rest. After all, the scripts will certainly be read and
used by other developers and integrators, etc. It is important that the scripts
are easy to understand and maintain. A shell script style guide is available
**shell_style_guide.md**.

## Step 1: Create a testcase definition

The first thing to do is to define the testcase meaning - what do you want to
test. A tester should create a testcase definition, preferably in markdown
language.

At this point, we will provide the simplest possible testcase definition,
which is just to verify if the parameters fed into the testcase script are
correctly fed, and that there is a correct number of parameters.

As a part of the design step, you should also determine what are the
requirements regarding the states of the OSRT devices, which of the managers is
under test, which manager will provide the right environment, etc.

Tick this checkbox:

- [] Prepare the testcase definition.

## Step 2 - Manual process

Manual process is required for real-life testcases. In this case you should try
to test the device manually by manually executing the commands on the device,
trying out stuff, checking if the device is in the correct state, etc.

Since we will not create a real life case, we can skip this step. We actually
need a script to be able to try out the process and to manually execute it.
Continue with the next step at this point.

Tick this checkbox:

- [] Complete the manual process.

## Step 3 - Create shell scripts

### Getting the testcase scripts

To help you execute the testcase manually, there are existing testcase scripts
available which can serve as examples. The scripts are all well-equipped with
help and usage notes.

The scripts are available as a part of the OpenSync `core` repository on
the GitHub. More precisely, the scripts can be found in the
`core/src/<manager_name>/fut/` directory.

The `<manager_name>` placeholder is typically the acronym with two or more
letters, such as `brv`, `cm2`, `dm`, `nm2`, etc.

**Note:**\
Read more about the OpenSync managers in the **EUB-020-013-001 OpenSync
Overview**.

To get the FUT testcase scripts, clone the OpenSync `core` git repository.

**Important:**\
Inside each of the test suite directories, there is also a `unit.mk` file. This
file is important for including the scripts when creating a tar file needed
for the actual testcase execution.

We explain the execution in a separate document. Remember that when adding
testcases, also add a line with a new test script to the `unit.mk` file. So,
when creating the FUT shell tar file using the `make` build system, all files
are included in the created tar file.

### Getting the libraries and tools

To write the testcases, you will also need libraries and tools that are found in
the `core/src/fut/` directory and its subdirectories. Libraries and tools
contain general and reusable functions that do not belong to any individual test
scripts. You obtained libraries and tools when cloning the `core` repository.

Similar to testcase scripts, all library functions are equipped with
descriptions, input parameters and comments on how to use the scripts correctly.

The location of the libraries is `core/src/fut/shell/lib/`.

Libraries are always named using this format: `<manager_acronym>_lib.sh`\
The `<manager_acronym>` placeholder is used to recognize which library belongs
to a particular manager, although a single script can source more than one
library.

Examples of library files are: `brv_lib.sh`, `cm2_lib.sh`, `dm_lib.sh`,
`nm2_lib.sh`, `onbrd_lib.sh`, etc.

There are also a few more libraries used by more than a single suite, one of
them being `unit_lib.sh`.

**Important:**\
Before writing your own functions, stop and take a look if a function that you
need is already written by someone else. If not, write your own function,
adequately document the function, and add the function to the appropriate
library.

If you want to enhance or change an existing library function, you are welcome
to do so, just keep in mind what kind of an effect this might have on the
existing testcases. The more basic the function, the stronger downstream effect
the function might have.

The tools are separate scripts which prepare the OSRT devices for testcase
execution. These are located in `core/src/fut/shell/tools/` and subdirectories.

## Overrides

Overrides is a special group of shell scripts. The purpose of these scripts is
to handle the platform or device specifics. Some DUTs require special
procedures to achieve certain actions. The reason for such adaptations might be
that these devices do not have all the system tools installed, or that the
tools work differently compared to other devices. For that reason, functions
need to be modified or written differently.\
In such cases, write the dedicated functions and save these functions into one
of the two files:

- `<platform_name>_lib_override.sh` for functions and procedures that are not
  common for all models, but are the same for a platform, e.g., `qca` or `bcm`
- `<model_name>_lib_override.sh` for functions that are specific only for a
  single model

**Note:**\
The platform- or model-specific file, as the name implies, overrides the
library when the two contain a function with the same name.

Platform overrides are located in:\
`platform/<platform_name>/src/fut/shell/lib/override/`.\
Each supported platform has its own file.

Model overrides are located in:\
`platform/<platform_name>/src/fut/shell/lib/override/`.\
Each supported model has its own file.

### Writing the first testcase script

After getting familiar with the available resources, you can start writing your
first testcase script.

At this point, the task is to write and to be able to manually execute a simple
testcase script with the provided parameters.

The steps in the testcase are:

1. Check if the number of parameters is as expected.
2. Log the parameters.
3. Pass the tests if the number of parameters is as expected. If not, display
   an error message informing the number of parameters is incorrect.

The first thing is to write a test script and to name the script appropriately.

The correct name of the example testcase script would be:\
`dm_verify_number_of_params.sh`

The testcase script `dm_verify_number_of_params.sh` should be fed by 3 input
parameters. If filled with more or less than 3, the script is supposed to
display usage notes. If fed with exactly 3, the script would log these input
parameters and pass.

Create the file in the directory:\
`core/src/dm/fut/`

Copy the below contents to the `dm_verify_number_of_params.sh`:

```bash
#!/bin/sh

# FUT environment loading
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/dm_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_number_of_params.sh [-h] arguments
Description:
    - Verify if number of provided parameters is correct.
Arguments:
    -h  show this help message
    \$1 (name)    : Description    : (string)(required)
    \$2 (surname) : Description    : (string)(required)
    \$2 (surname) : Description    : (int)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_number_of_params.sh <name> <surname> <year>
Script usage example:
    ./dm/dm_verify_number_of_params.sh John Doe 2022

usage_string
}
if [ -n "${1}" ]; then
    case "${1}" in
        help | \
        --help | \
        -h)
            usage && exit 1
            ;;
        *)
            ;;
    esac
fi

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly '${NARGS}' input arguments" -l "dm/dm_verify_awlan_node_params.sh" -arg
name=${1}
surname=${2}
year=${1}

log_title "dm/dm_verify_number_of_params.sh: DM test - Verify number of parameters"

log "dm/dm_verify_number_of_params.sh: name parameter is $name - Success"
log "dm/dm_verify_number_of_params.sh: surname parameter is $surname - Success"
log "dm/dm_verify_number_of_params.sh: year parameter is $year - Success"

pass
```

Modify the `unit.mk` file, so the file will be built into the tar file.

Save both files.

### Execute the testcase script on the device

Now, you should be ready to manually execute your first testcase.

The idea is to transfer the testcase script to the tested device, and execute
the script on the device. However, this topic is not covered here. To read about
how to prepare everything to actually execute the testcase, refer to the
document **executing_testcases.md**.

Search for the instructions on:

- How to prepare the testcase tar file
- How to transfer the testcase script to the OSRT RPI server
- How to transfer the testcase scripts to the device itself, using the
  `init.sh` script with `-tr` option provided.

After reading through **executing_testcases.md**, return
to this point and execute the example testcase script using the commands below
and compare the actual results with the ones at the bottom.

Connect to your RPI server, navigate to your `fut-base` directory, connect to
the DUT and run these two commands:

```bash
/tmp/fut-base/shell/tests/dm/dm_setup.sh wifi0 wifi1 wifi2
/tmp/fut-base/shell/tests/dm/dm_verify_number_of_params.sh John Doe 2022
```

The first command prepares the device (example wireless radio interfaces -
replace with correct interface names if necessary). The second command is the
actual testcase script.

The testcase should execute and log various messages to the terminal. At
the end, the script should print something like:

```bash
dm/dm_verify_number_of_params.sh: name parameter is John - Success
dm/dm_verify_number_of_params.sh: surname parameter is Doe - Success
dm/dm_verify_number_of_params.sh: year parameter is 2022 - Success
```

The testcase passes.

Tick these checkboxes at this point:

- [x] Obtain shell sources from the `core` repo
- [x] Create testcase shell script

Tick this checkbox:

- [x] Manually execute the testcase script

And since you will not need any new library functions, ignore these checkboxes:

- [ ] Create shell library functions
- [ ] Create shell library override functions for the platform
- [ ] Create shell library override functions for the model

## Step 4 - Integrate into the FUT framework

In this step we will integrate the new testcase into the FUT framework.

### Getting the FUT framework files

The `fut-base` repository contains framework files, including configuration
files, required for executing the testcases. To start working on the new
testcase, clone the `fut-base` repository to a directory on your local machine.

Certain other git repositories are also required to provide the device
configuration files and common framework tools and libraries. These repositories
are linked to by symbolic links in the `fut-base` repository and need to be
checked out in the correct directory structure separately.
The required directory structure, with respect to the other OpenSync
repositories:

```bash
OPENSYNC_ROOT
├── core
├── platform/...
├── vendor/...
└── qa
    ├── fut-base
    │   ├── config/model_properties -> ../../config/model_properties
    │   └── lib_testbed -> ../lib_testbed
    ├── config/model_properties
    │       └── reference
    └── lib_testbed
        └── generic
```

### Preparing a testcase configuration file

Most of the test scripts require some sort of input parameters which are
defined in test configuration files. Configuration files are part of the FUT
framework.

The location of testcase configurations is:\
`fut-base/config/<my_model>/testcase/`

All input parameters are compiled per test suite and from files which use this
exact naming format: `<TEST_SUITE>_config.py`, where `TEST_SUITE` stands for
test suite acronym. This time, capital letters are used. For every testcase,
there must be an entry in the configuration file even if the testcase script
uses zero parameters. In such case, an empty configuration must still be
provided.

Examples of configuration files are:\
`BRV_config.py`, `CM_config.py`, `DM_config.py`, `NM_config.py`, etc.

These configuration files are Python dictionaries, or "dictionary of
dictionaries", so some knowledge of Python is required to add the testcase
configurations. Looking at the contents of these files, the testcases are easily
identified. The actual testcase names are keys of the key-value pairs in the
dictionary.

To explain the procedure on how to prepare a configuration file, we are using
the DM test suite.

The location of our example configuration file is:\
`fut-base/config/<my_model>/testcase/DM_config.py`

To prepare the testcase configuration file for your model:

1. Navigate to the `my_model` directory that you are developing the testcase
   for. `my_model` can be some existing device name, or can be a new model if
   your goal is to support a currently non-supported model.
2. Open the corresponding test suite configuration file. In our case, the file
   is `DM_config.py`.
3. Add the testcase configuration dictionary as shown in the example below.
   Follow the already established alphabetical order and insert your test
   configuration at the appropriate place.

Configuration example with 3 parameters (2 strings and 1 numeric parameter):

```python
"dm_verify_number_of_params": [
    {
        "name": "John",
        "surname": "Doe",
        "year": 2022,
    },
],
```

Because the configuration file is a dictionary, the testcase name is a key
`dm_verify_number_of_params`. The value is actually a list of dictionaries.
Each element of the list is another dictionary of key-value pairs that
represent the testcase input parameters and their values.

The list of dictionaries enables repeated execution of testcases with changing
input parameters. This is called parametrization of each testcase. As already
mentioned, if the testcase has no input parameters, the testcase configuration
must still exist, but is an empty dictionary like in the example below:

```python
"test_without_params": [
    {},
],
```

Save the updated configuration file.

### Matching the test configuration with pytest file and script

After you have prepared the testcase configuration file, match the testcase
configuration name with the `pytest` function name (prepend with `test_`) and
testcase script file name.

The roles of `pytest` functions are to:

- Prepare the OSRT devices for the testcase which can include executing multiple
  setup and configuration scripts, depending on the testcase complexity.
- Load the testcase configuration.
- Feed the testcase configuration parameters into the testcase script.
- Execute the testcase script.

For more complex testcases, prior to executing the actual test script, the
`pytest` function also prepares the OSRT devices.\
For our simple testcase example, we make no modifications on any of the OSRT
devices.

Before executing your testcase, you need to write the `pytest` function. If you
are expanding the suite of already existing `pytest` functions, most of the
work is already done.

The available `pytest` functions already allow you to:

- Prepare the DUT, which is done by the function at the top of the file in a
  function named `test_dm_fut_setup_dut`.
- Load the test suite configuration into the configuration dictionary.

Open the `pytest` file `DM_test.py` where you will add the function that
serializes the configuration parameters and executes the testcase script.

Your new testcase configuration will be loaded together with the other already
made configurations, but the testcase takes only the related test parameters
from the dictionary.

For now, we simplify writing of the `pytest` function by adding the code below
at the bottom of the `DM_test.py` file:

```python
test_dm_verify_number_of_params_inputs = dm_config.get('dm_verify_number_of_params', [])

@allure.severity(allure.severity_level.TRIVIAL)
@pytest.mark.dut_only()
@pytest.mark.os_integration_m1()
@pytest.mark.gateway_compatible()
@pytest.mark.extender_compatible()
@pytest.mark.parametrize('test_config', test_dm_verify_number_of_params_inputs)
@pytest.mark.dependency(depends=["dm_fut_setup"], scope='session')
def test_dm_verify_number_of_params(test_config):
    dut_handler = pytest.dut_handler
    test_args = get_command_arguments(
        test_config['name'],
        test_config['surname']
        test_config['year']
    )
assert dut_handler.run('tests/dm/dm_verify_number_of_params', test_args) == ExpectedShellResult
```

When done, save the updated `pytest` file.

This is a good point to tick the checkboxes of what is already achieved:

- [x] Obtain framework sources from the `fut-base` repo
- [x] Obtain common tools and libraries from the `lib-testbed` repo
- [x] Obtain device capability files from the `config/model_properties` repo
- [x] Prepare configuration for the testcase
- [x] Prepare pytest function in `*_test.py` (`DM_test.py`)

### Executing the first testcase script

As already mentioned, the topic on how to execute the testcase is covered in
the document **executing_testcases.md**.

Search for the instructions on:

- How to list the available testcases
- How to execute a single testcase using the `-r` option

The `-l` switch lists all the testcases available from within the pytest file
(`DM_test.py` in this case). Among the available testcases, you should be able
to find your testcase:

```bash
Available test cases:
    ...
    dm_verify_number_of_params
    ...
collected 1000 items
Pytest collection finished 1000 items
```

If the testcase is listed, execute the testcase using:

```bash
./init.sh -r dm_verify_number_of_params -o
```

If all went well and if the testcase passed, tick the last checkbox for Step 4:

- [ ] Execute testcase script using the framework

## Step 5 - Support all models and verify with Jenkins

Finally the new testcase should be added to all of the relevant devices. To add
the testcase to the execution on the particular device, add the configuration
to the directories that exist for each of the supported models. For example
`fut-base/config/<model_name>/testcase/` and test for each model.

Tick this checkbox at this point:

- [ ]  Support testcase for all relevant models

## Adding a new test suite

Adding the new test suite requires completing most of the steps from the
previous section, but to add a new test suite, you must also create a few new
files.

### New suite FUT framework modifications

Adding a new suite to the FUT framework requires completing the following
actions:

- Create a new configuration file to store the testcase configurations for the
  new suite.

Name the file `<NEW_SUITE>_config.py` and save the file to
`fut-base/config/<model_name>/testcase`. Do this for each model that you plan
to support.

- Create a new `pytest` file to store the `pytest` functions.

Name the file `<NEW_SUITE>_test.py` and save the file to `fut-base/test/`.

- Update the `conftest.py` file to support the new suite.

Go to `fut-base/test`, edit `conftest.py`, and add lines to `setup_test_dict`
to support the new test suite. Use the existing dictionary key-value pairs as a
reference.

### New suite core repository modifications

When adding a new test suite, some additions to the `core` repository are
also expected. New suite testcase scripts would normally be located in a new
directory:\
`core/src/<new_suite>/fut/`

Testcase scripts would be named according to the rule:\
`<new_suite>_<descriptive_test_name>.sh`\

Also, a `unit.mk` file in the same directory as the scripts is needed.

It is also recommended to make a library file for the newly created test suite.
This applies if the new suite will use functions that will not be used by any
other suite:

1. Name the library `<new_suite>_lib.sh`
2. Save the library to: `core/src/fut/shell/lib/`
3. Add `<new_suite>_setup_test_environment` function to the library file.\
Refer to the already available libs and search for the function that prepares
the device for testing. You can quickly identify the function by looking at the
comments. The best way is to use `dm_lib.sh` as an example since the `dm` tests
do not require any special action e.g., neither stopping of managers, nor
starting only the specific ones. The `dm` testcases leave the devices running
as they would in normal operation.

4. Create the `<new_suite>_setup.sh` file and save the file to:
   `core/src/<new_suite>/fut/`

This shell script is called only when preparing the device for the test. The
shell itself is used at the top of the `<NEW_SUITE>_test.py` file. Again, refer
to already made `*_setup.sh` script.

## Making scripts verbose

Besides using the library functions, equip your scripts with functions taken
from the `base_lib.sh`. These functions are used to log the test progress as
well as to indicate where the test might fail. Refer to the comments of
functions to get more info on how to use them and do use logs in the same manner
as in the already available testcase scripts. Note that this file is already
sourced by `unit_lib.sh` and using or modifying this file should warrant a
careful consideration.

The `base_lib.sh` script is located in:\
`core/src/fut/shell/lib/`

## Appendix A: 5-step process

Use the steps to monitor how you are making progress with the new test scripts.
Finally, the purpose of the steps is to check if the mandatory phases are
complete, and to help you confirm that your work is done.

### Step 1 - Create a testcase definition

These are just words, no code. You need to define the environment needed, what
are the things you are testing, what you need to do during the test, and what
is the expected result. Think of everything needed, and also what is not needed
to test one thing specifically.

### Step 2 - Manual process

Try it out by hand first: if you start to automate and run into issues, it is
hard to fix the issues since there is no reference to how this is supposed to
look when it actually works! Do it by hand and create a set of functions that
you can copy-paste step-by-step and achieve the same goal.

### Step 3 - Create shell scripts

Create a test script or several test scripts. This is the point at which you
refine the manual steps, the commands, remove redundant steps, make the test
script repeatable, consider timing issues, consider if the test is stateful or
stateless, reuse existing code (library functions), make the code portable by
preparing the way for possible per-model overload functions, and make the
script generally pretty, compact and fast.

### Step 4 - Integrate into FUT framework

Combine shell with Python. Integrate the test scripts with the framework and
configuration. Consider possible parametrization for the testcase, and which
parameters used are device specific and which are testcase specific.

### Step 5 - Support all models and verify with Jenkins

When the testcase works for one model, the testcase should be verified for all
models. If all guidelines were followed, there should be little work at this
stage, and modifications can easily fit into any component, since the testcase
was made configurable enough.

## Appendix B: "5-step process" checkboxes

**Step 1:**

- [] Prepare the testcase definition

**Step 2:**

- [] Complete the manual process

**Step 3:**

- [ ] Obtain shell sources from the `core` repo
- [ ] Obtain shell overrides from the `platform/*` repo (optional, recommended)
- [ ] Obtain shell overrides from the `vendor/*` repo (optional, recommended)
- [ ] Create testcase shell script
- [ ] Create shell library functions
- [ ] Create shell library override functions for the platform
- [ ] Create shell library override functions for the model

**Step 4:**

- [ ] Obtain framework sources from the `fut-base` repo
- [ ] Obtain common tools and libraries from the `lib-testbed` repo
- [ ] Obtain device capability files from the `config/model_properties` repo
- [ ] Prepare configuration for the testcase
- [ ] Prepare pytest function in `*_test.py` (`DM_test.py`)
- [ ] Execute testcase script using the framework

**Step 5:**

- [ ]  Support testcase for all relevant models

## Appendix C: Important directories and their contents

Testcase shell scripts, setup and cleanup files are located in the directory:\
`core/src/<manager_name>/fut/`

Shell library files are located in:\
`core/src/fut/shell/lib/`

Library override files for supported platforms and models are located in:\
`platform/<platform_name>/src/fut/shell/lib/override/`

The `pytest` files are located in:\
`fut-base/test/`

Framework testcase configuration files are located in:\
`fut-base/config/model/<my_model>/testcase/`

Model properties and capabilities files are located in:\
`fut-base/config/model_properties/reference/<my_model>.yaml`

## Appendix D: Sourcing the sources

When sourcing the shell scripts, follow the "no horizontal sourcing" rule. This
means that when one library file requires the other, use indirect sourcing
through the lib_sources.sh file, which will actually check the exported guard
variables and source all the other required libraries.
