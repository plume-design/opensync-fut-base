# Testcase onbrd_verify_dut_client_certificate_file_on_server

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify DUT certificates validity. The test
checks if the certificates use the correct PEM format, are signed by a trusted
CA, and are still valid.

**Note:**\
The tools required to verify the certificates are available on the OSRT RPI
server. Therefore, the files are copied from the DUT to the OSRT RPI server
and verified there.

## Expected outcome and pass criteria

The client certificate is in correct PEM format and is not expired.\
The CA certificate is signed by a trusted authority.

## Implementation status

Implemented
