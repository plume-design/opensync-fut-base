# Testcase onbrd_verify_id_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to validate `id` field format in the `AWLAN_Node`
table. The testcase verifies the following:

* The node ID must be unique in the world. The node ID is case sensitive.
* The allowed character set is alphanumerical, with the addition of colon and
  underscore. No special characters are allowed.
* The node ID length must not exceed 81 (17 + 64) characters in any case.
* The node ID has to match either of these:
    * Device label
    * BLE beacon
    * QR code
* Optional: the node ID can also match the device MAC address, or the serial
  number.
* Optional: the node ID length must not exceed 12 characters, if the device
  requires onboarding via BLE. The test will report a warning in all cases where
  the 12 character length limit is exceeded.

**Note:**\
FUT does not validate all criteria due to practical reasons. The testcase
validates the node ID length and character set.

## Expected outcome and pass criteria

The field `id` in the `AWLAN_Node` table is non-empty and its length does not exceed
81 characters and contains only allowed characters.

## Implementation status

Implemented
