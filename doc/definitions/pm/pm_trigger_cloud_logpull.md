# Testcase pm_trigger_cloud_logpull

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify cloud triggered logpull is activated and logpull `tar` file is sent to the upload
location.

The testcase simulates the cloud triggered logpull by setting the fields `upload_location` and `upload_token` in the
OVSDB table `AW_LM_Config`. The logpull service starts collecting system logs, states and current configuration of nodes
and creates a tarball.

The testcase checks if the logpull tarball was created by verifying that the directory which should include the created
tarball is initially empty, and the file is there only after the settings are set.

The logpull tarball is uploaded to the specified location, using the upload token as credentials.

The test is applicable for all devices.

## Expected outcome and pass criteria

Initially logpull directory on the device is empty and `AW_Debug` table is clear.

After:

- setting `log_severity` in the table `AW_Debug` for PM manager to `DEBUG` and
- setting values `upload_location` and `upload_token` in the `AW_LM_Config` table

the below conditions must be met:

- logpull service is started,
- logpull directory on the device is not empty, indicating logpull `tar` file was created,
- logpull directory on the device empties, indicating logpull `tar` file was sent and deleted.

## Implementation status

Implemented
