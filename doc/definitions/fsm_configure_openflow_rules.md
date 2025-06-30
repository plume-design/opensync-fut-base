# Testcase fsm_configure_openflow_rules

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this test is to make sure the OVSDB table `Openflow_Config` is configurable with parameters needed for
complex FSM tests and that settings are reflected to the `Openflow_State` table.

Testcase falls into the category of simple "moving parts" FSM testcases, which should all pass before any more complex
"end-to-end" FSM testcases are implemented.

## Expected outcome and pass criteria

Fields `bridge`, `action`, `priority`, `table` `rule` and `token` presenting a rule are applied to the `Openflow_Config`
table.\
Rule is correctly created by inspecting the `token` field in the `Openflow_State`, which must be set to `true`.

## Implementation status

Implemented
