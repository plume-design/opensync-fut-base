# Testcase fsm_configure_fsm_tables

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The Goal of this test is to make sure OVSDB table `Flow_Service_Manager_Config`
is configurable with parameters needed for complex FSM tests.

Testcase falls into category of simple "moving parts" FSM testcases, which
should all pass before any more complex "end-to-end" FSM testcases are
implemented.

## Expected outcome and pass criteria

Fields `if_name`, `handler` and `plugin` in the table
`Flow_Service_Manager_Config` are correctly configured.

## Implementation status

Implemented
