# Testcase brv_is_bcm_license_on_system_fut

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to check if license is present on the BCM target. If license is present, testcase checks if
it has:

1. `FULL OVS` - support for Open vSwitch HW acceleration.

1. `FULL SERVICE_QUEUE` - support for service queue needed for rate limiting.

## Expected outcome and pass criteria

The testcase passes if license exist on BCM device and has `FULL OVS` and `FULL SERVICE_QUEUE` regex in the license
file.

## Implementation status

Implemented
