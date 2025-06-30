# Testcase onbrd_verify_client_certificate_files

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the certificate files exist in the target directory and that the certificate
files are not empty.\
The certificates target directory is defined by the `ca_cert` field in the `SSL` table.

**Note:** Example of certificates target directory is `/var/certs/`.\
Examples of certificate files are `ca.pem`,
`client.pem`, `client_dec.key`.

## Expected outcome and pass criteria

Target certificate file exists in the target directory. Target certificate file is not empty.

## Implementation status

Implemented
