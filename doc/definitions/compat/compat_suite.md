# COMPAT testing

## Overview

COMPAT test suite performs compatibility tests and verifies testbed readiness
by performing the following actions:

- Initialization of the ServerHandler class:
    - compat_main_init
- Unblocking of the DUT WAN and management IP addresses:
    - compat_unblock_dut_wan_mng_addresses
- Initialization of DUT, REF, and client devices:
    - compat_dut_init
    - compat_ref_init
    - compat_ref2_init
    - compat_client_init
    - compat_client2_init
- Checking FUT release version:
    - compat_fut_release_version
- Checking server device version:
    - compat_server_device_version
- Checking DUT, REF, and client device versions:
    - compat_dut_device_version
    - compat_ref_device_version
    - compat_ref2_device_version
    - compat_client_device_version
    - compat_client2_device_version
- Checking that tmp directories are mounted as executables:
    - compat_dut_tmp_mount_executable
- Testing if FUT shell scripts are transferred to DUT, REF, and client devices:
    - compat_dut_transfer
    - compat_ref_transfer
    - compat_ref2_transfer
    - compat_client_transfer
    - compat_client2_transfer
- Checking regulatory domain:
    - compat_dut_verify_reg_domain
    - compat_ref_verify_reg_domain
    - compat_ref2_verify_reg_domain
- Preventing REF devices from rebooting:
    - compat_ref_prevent_reboot
    - compat_ref2_prevent_reboot
