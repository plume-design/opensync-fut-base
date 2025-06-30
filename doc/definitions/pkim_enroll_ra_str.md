# Testcase pkim_enroll_ra_str

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

PKI certificate enroll/re-enroll flow test with a retry step.

This test cases test the PKIM's handling of the `Retry-After` HTTP header,
which is used by the EST server to signal the client that certificate generation
might take some time and should retry at a later date.

The `Retry-After` header may specify the delay as a simple integer or as a
future timestamp as a string. This test tests the string timestamp case.

### Simple Enroll step

- start EST server on the testbed server
- device restart PKIM with empty certificate store
- set `PKI_Config` to use the testbed server EST service, use the `default`
  label
- ensure that the device connects to EST server and downloads CA certs
- ensure that the device connects to EST server and issues a `simpleenroll`
  request
- the server responds with 503 and provides a `Retry-After` header with a future
  string timestamp
- ensure that the device retries connecting to the EST server and re-downloads
  the CA certs
- ensure that the device connects to EST server and retries a `simpleenroll`
  request
- ensure that the certificate status in `PKI_Config` is set to `success`
- ensure that the certificate on the device matches the one provided the EST
  server

### Simple Re-Enroll step

- set `PKI_Config:renew` to request a certificate renewal, use the `default`
  label
- ensure that the device connects to EST server and downloads CA certs
- ensure that the device connects to EST server and issues a `simplereenroll`
  request
- the server responds with 503 and provides a `Retry-After` header with a string
  future timestamp
- ensure that the device retries connecting to the EST server and re-downloads
  the CA certs
- ensure that the device connects to EST server and retries a `simplereenroll`
  request
- ensure that the certificate status in `PKI_Config` is set to `success`
- ensure that the certificate on the device matches the one provided the EST
  server

## Expected outcome and pass criteria

`PKI_Config:status` is set to `success` and the certificate serial number
matches the serial number provided by the EST server.

## Implementation status

Implemented
