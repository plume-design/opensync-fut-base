# How to execute FUT testcases using the init.sh script

## Introduction

This document provides instructions on how to execute the FUT testcases using
the `init.sh` script. This document also provides instructions on how to
prepare the environment to actually be able to execute the testcases. The
latter info partly overlaps with the information that is also available in the
**user_manual.md**, but is also available here to make this document
independent.

## Background

After the testcase development, which includes writing the scripts and `pytest`
functions, all FUT testcase scripts are executed on OSRT devices. Which devices
take part in the testcase execution depends on the testcase itself.

To make execution of the test scripts possible, all required scripts (`.sh`
files) must be transferred to the OSRT devices.

`pytest` scripts that are used to execute the actual test scripts must be
present on the OSRT RPI server. In contrast to the testcase scripts, which are
implemented in `shell`, `pytest` scripts are implemented in Python.

Testcase scripts and library files are part of the OpenSync `core` repository.
`pytest` scripts are in the `fut-base` directory.

To execute the tests, make all sources available at the OSRT RPI
server, where the shell scripts are initially stored in form of a tar file.

`pytest` scripts are checked out from the `fut-base` repository. Certain
other git repositories are also required to provide the device configuration
files and common framework tools and libraries. These repositories are linked to
by symbolic links in the `fut-base` repository and need to be checked out in the
correct directory structure separately. The required directory structure, with
respect to the other OpenSync repositories:

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

Complete these four steps to execute the testcases:

1. Create the tar file containing the shell scripts.
2. Prepare the FUT framework on the OSRT RPI server.
3. Transfer the tar file prepared in the first step to the OSRT RPI server.
4. Use the `./init.sh` script to execute the testcases.

**Note:**\
Instructions on how to setup the OSRT is out of scope of this document. For
instructions on how to setup OSRT refer to the **EIN-020-022-501 OSRT Setup
Guide**.

## Executing the testcases

There is more than one way to execute the testcases. This document provides
instructions on how to use the `init.sh` script.

### Step 1: Create a tar file containing FUT shell files

The goal of this step is to create a tar file which contains shell scripts,
library files, and other files that are necessary to execute the testcases.

Assuming that you came to this point after writing your own testcase, or you
simply want to execute an existing testcase, you should have the `core` OpenSync
git repository checked out on your local PC. If not, first clone the `core`
repository.

To create a FUT shell tar file, navigate to the `core` directory and
execute the below command:

```bash
make fut TARGET=alltargets
```

After printouts informing that the tar file was created, check if the
`core/images` directory contains the tar file. Navigate to the `images`
directory and list files.

There should be a newly created file, named similar to (*example tar file*):\
`fut-alltargets-2.2.2.0-0-g8f04cc-mods-development.tar.bz2`

Later in step 3, transfer this tar file to the FUT OSRT RPI server.

### Step 2: Prepare the framework files

The goal of this step is to make the FUT framework files available.

Establish an SSH connection to the OSRT RPI server and navigate into the
`/home/plume/` directory.

Clone the FUT framework git repository. The FUT framework files are now
available inside the `fut-base` directory.

While on the OSRT RPI server, navigate to `fut-base/resource` and create the
`shell` directory:\
`mkdir shell`

`shell` directory is needed in step 3, where we transfer the tar file to
the OSRT RPI server.

### Step 3: Transferring the tar file

The goal of this step is to transfer the tar file to the FUT OSRT RPI server.

From the local PC, copy the FUT shell tar file to the `fut-base/resource/shell`
directory on the OSRT RPI server.

The `fut-base/resource/shell` is where the framework expects and looks for the
tar file containing the testcase scripts. At this point, the testcase scripts
are not yet on the DUT and other OSRT devices. The extraction of the tar file
and transfer of the scripts to OSRT devices is done after the testcase
execution command is entered. We will return to this later.

Use the below command to copy the tar file to the OSRT RPI server (*example tar
file, example IP address*):

```bash
scp fut-alltargets-2.2.2.0-0-g8f04cc-mods-development.tar.bz2  plume@10.1.1.99:/home/plume/fut-base/resource/shell/
```

After copying the tar file to the OSRT RPI server, make sure there is exactly
one tar file located in the `fut-base/resource/shell` directory. If there are
two or more, the `init.sh` script cannot determine which tar file to unpack and
fails. Delete any pre-existing tar files.

After this step you can to execute the testcases.

### Step 4: Execute the testcases

On the OSRT RPI server, navigate to the `fut-base` directory. To execute the
tests, use the `init.sh` script with or without the optional flags. Flags are
described in the script’s help:

```bash
./init.sh -h
```

Executing the `init.sh` script without any additional options unpacks the shell
files from the FUT shell tar file and transfers the required files to the DUT,
REFs, and client devices.\
After the transfer is completed, the `init.sh` script issues commands to
execute the required scripts to setup the OSRT devices, and executes all
testcases.

**Note:**\
When running the `init.sh` script for the first time, the script builds a
Docker environment. This procedure may take a long time, even more than 2 h, so
be patient. The testcases will execute after the Docker container is ready. For
all subsequent executions, the Docker environment will be reused, resulting in
a much shorter preparation time before the actual testcase execution.

### init.sh usage examples

To learn how to use the `init.sh` script and how to use the script to execute
testcases use the built-in help. To list help use the below command:

```bash
./init.sh -l
```
