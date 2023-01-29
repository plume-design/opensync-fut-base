# Testcase dm_verify_count_reboot_status

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify the `count` in the OVSDB `Reboot_Status`
table has at least one reboot counted, indicating counter is counting.

Test case relies on device being reset at least once in the past.

## Expected outcome and pass criteria

The field `count` in the `Reboot_Status` table has at least one reboot counted.

## Implementation status

Implemented
