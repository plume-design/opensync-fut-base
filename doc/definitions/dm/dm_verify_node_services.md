# Testcase dm_verify_node_services

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the OVSDB `Node_Services` table
includes the expected services and managers.

The expected managers and services are those that are built into the FW image
by setting the Kconfig option to 'y'.

## Expected outcome and pass criteria

Managers and services in the table `Node_Services` must be present,
enabled and running.

## Implementation status

Implemented
