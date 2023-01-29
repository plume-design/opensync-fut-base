# Testcase fsm_create_tap_interface

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that a tap type interface can be created,
brought up and configured, and that a tap interface exists on the system.

Testcase falls into category of simple "moving parts" FSM testcases, which
should all pass before any more complex "end-to-end" FSM testcases are
implemented.

## Expected outcome and pass criteria

Tap interface is created, configured in the home bridge, and exists on
the system.

## Implementation status

Implemented
