# Testcase cm2_ssl_check

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The script checks that the required SSL verification files are referenced in
the OVSDB `SSL` table are present and have contents, i.e. are not empty.

## Expected outcome and pass criteria

SSL files: ca_cert, certificate and private_key are on the provided path
and are not empty.

## Implementation status

Implemented
