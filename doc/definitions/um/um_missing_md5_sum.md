# Testcase um_missing_md5_sum

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server.
The corresponding MD5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW download process indicates
the correct error if FW image is available, but without the corresponding
`md5.sum` file.

During the testcase preparation, a second FW image is generated with a different
name as the original, but not the corresponding `md5.sum` file.

## Expected outcome and pass criteria

After the FW image download starts, an error due to the missing `md5.sum` file
is indicated by the `upgrade_status` field value `UPG_ERR_DL_MD5`.
