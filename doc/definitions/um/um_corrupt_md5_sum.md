# Testcase um_corrupt_md5_sum

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

FW image is available on the RPI server. The corresponding md5 file is available on the RPI server.

## Testcase description

The goal of this testcase is to verify that the FW image download process indicates the correct error if a FW image is
available, but with the corrupted corresponding `md5.sum` file.

During the testcase preparation, the second FW image is generated with different name as the original. Also, the
corrupted corresponding `md5.sum` file is created.

## Expected outcome and pass criteria

After the FW image download starts, an error due to a missing `md5.sum` is indicated using the `upgrade_status` field
value `UPG_ERR_MD5_FAIL`.

## Implementation status

Implemented
