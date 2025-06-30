# Testcase pkim_enroll

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Basic PKI certificate enroll/re-enroll flow test.

### Simple Enroll step

- start EST server on the testbed server
- device restart PKIM with empty certificate store
- set `PKI_Config` to use the testbed server EST service, use the `default`
  label
- ensure that the device connects to EST server and downloads CA certs
- ensure that the device connects to EST server and issues a `simpleenroll`
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
- ensure that the certificate status in `PKI_Config` is set to `success`
- ensure that the certificate on the device matches the one provided the EST
  server

## Expected outcome and pass criteria

`PKI_Config:status` is set to `success` and the certificate serial number
matches the serial number provided by the EST server.

## Implementation status

Implemented
