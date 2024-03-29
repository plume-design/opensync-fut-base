# FUT - Functional Unit Testing

[FUT](https://opensync.atlassian.net/wiki/spaces/OCC/pages/39920206446/Functional+Unit+Testing+FUT) is a cloudless,
white box integration testing framework for verifying the [OpenSync](https://opensync.atlassian.net/wiki/spaces/OCC)
stack integration on your device.

## [Requirements](./doc/user_manual.md#Requirements)

FUT code and configuration consists of several git repositories, see the user manual chapter [Directory and repository
structure](./doc/user_manual.md#Directory-and-repository-structure).

## Features

* **Cloudless:** your OpenSync device does not need a connection to any cloud services. Testing is self-contained and
  can be executed during integration of the OpenSync stack into the device firmware.
* **White box:** access to the OpenSync device allows FUT to verify the internal structures and implementation, as well
  as the device functionality.
* **Portable:** using containerization, the framework execution environment does not require special setup by the user.
  By implementing test cases in shell, and the framework in python, testing is possible on most Linux-based devices.
* **Configurable:** the scope of testing (the test plan) can easily be configured by the user. The device model present
  in the test environment is configurable as well.
* **Extendable:** Adding test scripts or adding different input parameters to the test run is possible. Most OpenSync
  devices are able to run FUT, even those not supported out-of-the-box. Adding support is easy for the user.
* **Informative:** extensive logging and reporting capabilities provide detailed insight into the steps of each test and
  ease debugging effort.

## Documentation

It is recommended to read the documentation and review release notes of the latest version before executing test cases.

* [User manual](./doc/user_manual.md): Overall information about FUT is available in this document.
* [Repository and directory structure](./doc/repository_structure.md): Requirements for other repositories in the
  directory structure in order to use FUT.
* [Release notes](./doc/release_notes.md): Information about FUT features for the current and past releases.
* [Test case definitions](./doc/definitions/): These files are the source of truth and a high-level text definition of
  test cases on which implementation details are based.
* [Test case configuration generators and inputs](./doc/test_case_configuration_generators_and_inputs.md): documentation
  containing an explanation and practical examples of everything related to test case configuration.
