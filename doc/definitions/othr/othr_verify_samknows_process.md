# Testcase othr_verify_samknows_process

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Samknows module is present on the system.

## Testcase description

Testcase verifies that the Samknows feature can be triggered on the DUT by
populating the `Node_Config` table.

Testcase enables 'samknows' process by populating `module` field in the
`Node_Config` table with below OVS command:

`ovsh U Node_Config -w module==samknows value:=\"true\" key:=enable`

## Expected outcome and pass criteria

Testcase passes if `value` and `key` fields of `Node_Config` table are
propagated to the `Node_State` table and `samknows` process is running on the
DUT successfully.

## Implementation status

Implemented
