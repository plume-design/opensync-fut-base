# FUT - Functional Unit Testing

[FUT](https://opensync.atlassian.net/wiki/spaces/OCC/pages/39920206446/Functional+Unit+Testing+FUT) is a cloudless,
white box integration testing framework for verifying the [OpenSync](https://opensync.atlassian.net/wiki/spaces/OCC)
stack integration on your device.

## Requirements

FUT has several key requirements for proper operation:

- **Testbed:** FUT requires a standardized testbed environment.[CRATOS (Comprehensive Reference Apparatus for Testing OpenSync)](https://opensync.atlassian.net/wiki/spaces/OCC/pages/39920140747/Comprehensive+Reference+Apparatus+for+Testing+OpenSync+CRATOS)
  is the specified testbed for this purpose.
- **Device Access:** Full management SSH access to the device is necessary, including `root` privileges and `scp`
  capabilities for script transfer.
- **Environment:** The FUT framework runs within a **Docker** container and uses **Pytest** for test automation and
  **Allure** for reporting.
- **Directory Structure:** A [specific directory and repository structure](./doc/repository_structure.md) must be
  maintained for FUT to function correctly.

## Features

- **Cloudless:** your OpenSync device does not need a connection to any cloud services. Testing is self-contained and
  can be executed during integration of the OpenSync stack into the device firmware.
- **White box:** access to the OpenSync device allows FUT to verify the internal structures and implementation, as well
  as the device functionality.
- **Portable:** using containerization, the framework execution environment does not require special setup by the user.
  By implementing test cases in shell, and the framework in python, testing is possible on most Linux-based devices.
- **Configurable:** the scope of testing (the test plan) can easily be configured by the user. The device model present
  in the test environment is configurable as well.
- **Extendable:** Adding test scripts or adding different input parameters to the test run is possible. Most OpenSync
  devices are able to run FUT, even those not supported out-of-the-box. Adding support is easy for the user.
- **Informative:** extensive logging and reporting capabilities provide detailed insight into the steps of each test and
  ease debugging effort.

## Documentation

It is recommended to read the documentation and review release notes of the latest version before executing test cases.

- [User manual](./doc/user_manual.md): Overall information about FUT is available in this document.
- [Repository and Directory Structure](./doc/repository_structure.md): Requirements for other repositories in the
  directory structure in order to use FUT.
- [Release notes](./doc/release_notes.md): Information about FUT features for the current and past releases.
- [Test case definitions](./doc/definitions/): These files are the source of truth and a high-level text definition of
  test cases on which implementation details are based.
- [Test case configuration generators and inputs](./doc/test_case_configuration_generators_and_inputs.md): documentation
  containing an explanation and practical examples of everything related to test case configuration.
